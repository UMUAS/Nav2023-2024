import asyncio
import logging
import time
from abc import ABC, abstractmethod

from pymavlink import mavutil

from .utils import (
    AUTOPILOT,
    AUTOPILOT_HEARTBEAT_TIMEOUT,
    GCS,
    GCS_HEARTBEAT_TIMEOUT,
    HEARTBEAT,
    HEARTBEAT_SEND_RATE_HZ,
    HEARTBEAT_TIMEOUT,
    SYS_STATUS,
)

logger = logging.getLogger()


class ServerConnection:
    pass


class ClientConnection(ABC):
    """A connection that acts as a client, receiving data from a flight controller or other
    mavlink system."""

    heartbeat_timeout = None

    def __init__(self, conn_string, baudrate=None):
        self.conn_string = conn_string
        self.baudrate = baudrate
        self.last_heartbeat = None
        self.conn = None

    @abstractmethod
    def reconnect(self):
        pass

    def update_last_heartbeat(self):
        self.last_heartbeat = time.time()
        logger.info(
            f"Heartbeat from system: {self.conn.target_system} "
            f"component: {self.conn.target_component}."
        )

    def check_heartbeat(self, msg):
        if not msg:
            return
        if msg.get_type() == HEARTBEAT:
            self.update_last_heartbeat()

    def retry_connection(self):
        # Try reconnecting.
        self.reconnect()
        if self.conn:
            msg = self.conn.wait_heartbeat(blocking=False, timeout=HEARTBEAT_TIMEOUT)
            if msg:
                self.update_last_heartbeat()
                return
        raise ConnectionError("Failed to re-establish the connection.")

    def is_valid_connection(self):
        """Check that we have received a heartbeat within the last `heartbeat_timeout`
        seconds."""
        current_time = time.time()
        if current_time - self.last_heartbeat > self.heartbeat_timeout:
            return True
        return False

    def send_heartbeat_msg(self):
        self.conn.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER,
            mavutil.mavlink.MAV_AUTOPILOT_INVALID,
            0,
            0,
            0,
        )

    def validate_components(self):
        # TODO
        pass

    def get_msg(self):
        msg = self.conn.recv_match()
        return msg

    def request_messages(self):
        request_message_interval(self.conn, mavutil.mavlink.MAVLINK_MSG_ID_AHRS2, 1)
        request_message_interval(self.conn, mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 2)


class AutopilotConnection(ClientConnection):
    heartbeat_timeout = AUTOPILOT_HEARTBEAT_TIMEOUT

    def __init__(self, conn_string, baudrate=None):
        super().__init__(conn_string, baudrate)
        self.conn = connection_to_autopilot(conn_string, baudrate)

    def reconnect(self):
        self.conn = connection_to_autopilot(self.conn_string, self.baudrate)


class GCSConnection(ClientConnection):
    heartbeat_timeout = GCS_HEARTBEAT_TIMEOUT

    def __init__(self, conn_string, baudrate=None):
        super().__init__(conn_string, baudrate)
        self.conn = connection_to_gcs(conn_string, baudrate)

    def reconnect(self):
        self.conn = connection_to_gcs(self.conn_string, self.baudrate)


async def heartbeat_loop(conn: ClientConnection):
    while True:
        try:
            conn.send_heartbeat_msg()
            await asyncio.sleep(HEARTBEAT_SEND_RATE_HZ)
        except Exception as e:
            logger.exception(e)


async def receive_msg_loop(conn: ClientConnection):
    while True:
        try:
            message = await asyncio.get_event_loop().run_in_executor(None, conn.get_msg)
            if message:
                message = message.to_dict()
                logger.info(message)
                asyncio.create_task(process_autopilot_msg(message, conn))
        except Exception as e:
            logger.exception(e)


async def validate_connection_loop(conn: ClientConnection):
    while True:
        if not conn.is_valid_connection():
            conn.retry_connection()
        asyncio.sleep(HEARTBEAT_SEND_RATE_HZ)


async def process_autopilot_msg(message, conn: ClientConnection):
    # Is the drone still in a valid state?
    # Did we receive a heartbeat message?
    conn.check_heartbeat(message)
    if message == SYS_STATUS:
        pass
    if message == "":
        pass


def request_message_interval(
    conn: mavutil.mavlink_connection, message_id: int, frequency_hz: float
):
    """
    Request MAVLink message in a desired frequency,
    documentation for SET_MESSAGE_INTERVAL:
        https://mavlink.io/en/messages/common.html#MAV_CMD_SET_MESSAGE_INTERVAL

    Args:
        conn (mavutil.mavlink_connection): MAVLink connection object
        message_id (int): MAVLink message ID
        frequency_hz (float): Desired frequency in Hz
    """
    conn.mav.command_long_send(
        conn.target_system,
        conn.target_component,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
        0,
        message_id,  # The MAVLink message ID
        1e6
        / frequency_hz,  # The interval between two messages in microseconds. Set to -1 to disable and 0 to request default rate.
        0,
        0,
        0,
        0,  # Unused parameters
        0,  # Target address of message stream (if message has target address fields). 0: Flight-stack default (recommended), 1: address of requestor, 2: broadcast.
    )


def begin_flight_termination():
    pre_flight_termination()
    # Set flight to Hold for some time.
    # Then start flight termination.


def pre_flight_termination():
    pass


def terminate_flight():
    pass


def post_flight_termination():
    pass


def connection_to_autopilot(conn_string, baudrate):
    return connection_to_mavlink_system(AUTOPILOT, conn_string, baudrate, 0, 0)


def connection_to_gcs(conn_string, baudrate):
    return connection_to_mavlink_system(GCS, conn_string, baudrate, 0, 0)


def connection_to_mavlink_system(system_name, conn_string, baudrate, max_retries=0, retry_delay=0):
    """Establish and return a connection to a MAVLink system (e.g., flight controller, GCS).

    Args:
        system_name (str): The name of the MAVLink system we want to connect to.
        conn_string (str): The channel for communication (e.g., serial port, network address).
        baudrate (int or None): Number of bits per second transferred over the connection line. None
            if not applicable or provided (e.g., for internet connections).
        max_retries (int): Number of additional times we will attempt to make a connection.
        retry_delay (int): Number of seconds between each retry attempt.

    Returns:
        mavutil.mavlink_connection or None: The MAVLink connection or None if unsuccessful.
    """
    num_tries = max_retries + 1
    for attempt in range(1, num_tries + 1):
        try:
            connection = mavutil.mavlink_connection(conn_string, baud=baudrate)
            logger.info(f"Connected to the {system_name}.")
            return connection
        except Exception as e:
            logger.exception(f"Error establishing connection (Attempt {attempt}/{num_tries}): {e}")
            if attempt < num_tries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    logger.error(f"Connection to the {system_name} could not be established.")
    return None
