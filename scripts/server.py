"""This script runs on the drone where it maintains the connection with the drone,
and processes requests from other onboard processes."""

import asyncio
import io
import logging
import logging.config
import os
import queue
import socket
import sys
import threading

from dotenv import load_dotenv

from flight_termination.flight_termination import begin_flight_termination
from navigation.connection import (
    AutopilotConnectionWrapper,
    heartbeat_loop,
    receive_msg_loop,
    validate_connection_loop,
)
from navigation.utils import get_logging_config

SOCKET_PATH = "/tmp/umuas_socket"
MAX_LENGTH = 1024

# Reload environment variables on startup to avoid caching them.
load_dotenv(verbose=True, override=True)

# Configure logging.
logging_config = get_logging_config()
logging.config.fileConfig(io.StringIO(logging_config), disable_existing_loggers=False)

logger = logging.getLogger()

message_queue = queue.PriorityQueue()


async def main():
    autopilot_conn_wrapper = None
    try:
        autopilot_conn_wrapper = get_connection_wrapper()
        setup_server(autopilot_conn_wrapper)
        await start_async_tasks(autopilot_conn_wrapper)
    except KeyboardInterrupt:
        logger.info("Exiting...")
        cleanup(autopilot_conn_wrapper)
        sys.exit(1)


async def start_async_tasks(autopilot_conn_wrapper):
    receive_task, heartbeat_task, validate_connection_task = get_async_tasks(autopilot_conn_wrapper)
    try:
        await asyncio.gather(receive_task, heartbeat_task, validate_connection_task)
    except Exception as error:
        logger.info(error)
        logger.info("Beginning flight termination...")
        begin_flight_termination(autopilot_conn_wrapper)


def get_connection_wrapper():
    autopilot_conn_string = os.getenv("AUTOPILOT_CONN_STRING")
    autopilot_baudrate = os.getenv("AUTOPILOT_BAUDRATE")

    autopilot_conn_wrapper = AutopilotConnectionWrapper(autopilot_conn_string, autopilot_baudrate)
    if not autopilot_conn_wrapper.conn:
        sys.exit(1)

    logger.info("Waiting for a heartbeat from the autopilot...")
    autopilot_conn_wrapper.conn.wait_heartbeat()
    autopilot_conn_wrapper.update_last_heartbeat()
    logger.info("Initial heartbeat received from the autopilot.")

    # Request messages from the flight controller.
    autopilot_conn_wrapper.request_messages()

    return autopilot_conn_wrapper


def setup_server(autopilot_conn_wrapper):
    remove_socket_file()

    # Start the server on a new thread.
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()

    # Process messages from the queue on a new thread.
    process_thread = threading.Thread(
        target=process_messages_from_queue, args=(autopilot_conn_wrapper,)
    )
    process_thread.daemon = True
    process_thread.start()


def start_server():
    server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    # server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(SOCKET_PATH)
    server_socket.listen(5)
    logger.info(f"Server started on path {SOCKET_PATH}.")

    while True:
        try:
            client_socket, _ = server_socket.accept()
            # client_socket.settimeout(60)
            client_thread = threading.Thread(target=handle_client_thread, args=(client_socket,))
            client_thread.daemon = True
            client_thread.start()
            # logger.info(f"Running {threading.active_count()} thread(s).")
        except Exception as e:
            logger.exception("An error occured.")
            logger.exception(e)


def process_messages_from_queue(autopilot_conn_wrapper):
    while True:
        data = message_queue.get()
        if data:
            logger.info(f"Received data: {data.decode()}")


def send_command(autopilot_conn_wrapper, *args):
    assert len(args) == 7
    connection = autopilot_conn_wrapper.conn
    connection.conn.mav.command_long_send(
        connection.target_system, connection.target_component, *args
    )


def send_mission_plan(autopilot_conn_wrapper, *args):
    assert len(args) == 10
    connection = autopilot_conn_wrapper.conn
    connection.conn.mav.command_long_send(
        connection.target_system, connection.target_component, *args
    )


def receive_data(client_socket: socket):
    while True:
        data = client_socket.recv(MAX_LENGTH)
        if not data:
            break
        message_queue.put(data)
    client_socket.close()
    logger.info("Client gone!")


def handle_client_thread(client_socket: socket):
    receive_data(client_socket)


def get_async_tasks(autopilot_conn_wrapper):
    receive_task = asyncio.create_task(receive_msg_loop(autopilot_conn_wrapper))
    heartbeat_task = asyncio.create_task(heartbeat_loop(autopilot_conn_wrapper))
    validate_connection_task = asyncio.create_task(validate_connection_loop(autopilot_conn_wrapper))
    return receive_task, heartbeat_task, validate_connection_task


def remove_socket_file():
    """Remove the socket file if it already exists."""
    try:
        os.unlink(SOCKET_PATH)
    except OSError:
        # If we encounter an error when attempting to delete the file and it still
        # exists, raise the exception again.
        if os.path.exists(SOCKET_PATH):
            raise


def cleanup(autopilot_conn_wrapper):
    if autopilot_conn_wrapper is not None and autopilot_conn_wrapper.conn is not None:
        autopilot_conn_wrapper.conn.close()
    remove_socket_file()
    # TODO: Close sockets.


if __name__ == "__main__":
    asyncio.run(main())
