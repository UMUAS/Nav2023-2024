import asyncio
import logging
import time
from abc import ABC, abstractmethod

from pymavlink import mavutil

from .utils import (
    ALT_SCALING_FACTOR,
    AUTOPILOT,
    AUTOPILOT_HEARTBEAT_TIMEOUT,
    BAD_DATA,
    COMMAND_ACK,
    GCS,
    GCS_HEARTBEAT_TIMEOUT,
    GLOBAL_POSITION_INT,
    HEARTBEAT,
    HEARTBEAT_SEND_RATE_HZ,
    LAT_LON_SCALING_FACTOR,
    MISSION_ACK,
    MISSION_ITEM_REACHED,
    MISSION_REQUEST,
    RC_CHANNELS,
    SYS_STATUS,
)

logger = logging.getLogger()


class ServerConnection:
    pass


class ClientConnectionWrapper(ABC):
    """A wrapper for a connection that acts as a client, receiving and sending information to a
    flight controller or other mavlink system."""

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
            f"Heartbeat from autopilot received: system: {self.conn.target_system} "
            f"component: {self.conn.target_component}"
        )

    def update_current_position(self, message):
        self.latitude = message.lat / LAT_LON_SCALING_FACTOR
        self.longitude = message.lon / LAT_LON_SCALING_FACTOR
        self.altitude = message.alt / ALT_SCALING_FACTOR
        self.pos_last_set_time = time.time()

    def retry_connection(self):
        if self.conn:
            msg = self.conn.recv_match(
                type=[HEARTBEAT], blocking=True, timeout=self.heartbeat_timeout
            )
            if msg:
                self.process_heartbeat(msg)
                return
        raise ConnectionError("Failed to re-establish the connection.")

    def is_valid_connection(self):
        """Check that we have received a heartbeat within the last `heartbeat_timeout`
        seconds."""
        current_time = time.time()
        if (current_time - self.last_heartbeat) > self.heartbeat_timeout:
            return False
        return True

    def send_heartbeat_msg(self):
        logger.info("Heartbeat sent from companion computer.")
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
        request_message_interval(self.conn, mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 1)
        request_message_interval(self.conn, mavutil.mavlink.MAVLINK_MSG_ID_SYS_STATUS, 1)
        request_message_interval(self.conn, mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 1)
        # request_message_interval(self.conn, mavutil.mavlink.MAVLINK_MSG_ID_RC_CHANNELS, 1)

    def process_heartbeat(self, heartbeat_message):
        if not heartbeat_message:
            return
        self.update_last_heartbeat()
        self.system_status = heartbeat_message.system_status

    def process_sys_status(self, sys_status):
        self.battery_remaining = sys_status.battery_remaining


class AutopilotConnectionWrapper(ClientConnectionWrapper):
    """A wrapper for a connection that acts as a client, receiving and sending information to an
    Autopilot."""

    heartbeat_timeout = AUTOPILOT_HEARTBEAT_TIMEOUT

    def __init__(self, conn_string, baudrate=None):
        super().__init__(conn_string, baudrate)
        self.conn = connection_to_autopilot(conn_string, baudrate)

    def reconnect(self):
        self.conn = connection_to_autopilot(self.conn_string, self.baudrate)


class GCSConnectionWrapper(ClientConnectionWrapper):
    """A wrapper for a connection that acts as a client, receiving and sending information to a
    GCS."""

    heartbeat_timeout = GCS_HEARTBEAT_TIMEOUT

    def __init__(self, conn_string, baudrate=None):
        super().__init__(conn_string, baudrate)
        self.conn = connection_to_gcs(conn_string, baudrate)

    def reconnect(self):
        self.conn = connection_to_gcs(self.conn_string, self.baudrate)


async def heartbeat_loop(conn: ClientConnectionWrapper):
    while True:
        conn.send_heartbeat_msg()
        await asyncio.sleep(HEARTBEAT_SEND_RATE_HZ)


async def receive_msg_loop(conn: ClientConnectionWrapper):
    while True:
        message = conn.get_msg()
        if message:
            await process_autopilot_msg(message, conn)
        else:
            await asyncio.sleep(0.01)


async def validate_connection_loop(conn: ClientConnectionWrapper):
    while True:
        if not conn.is_valid_connection():
            logger.info(f"Failed to receive a heartbeat in {conn.heartbeat_timeout} seconds.")
            conn.retry_connection()
        logger.info("Connection still valid!")
        await asyncio.sleep(HEARTBEAT_SEND_RATE_HZ)


async def process_autopilot_msg(message, conn: ClientConnectionWrapper):
    # Validate message.
    if not message:
        return
    message_type = message.get_type()
    if message_type == BAD_DATA:
        if mavutil.all_printable(message.data):
            logger.info(message.data)

    if message_type == HEARTBEAT:
        conn.process_heartbeat(message)
    elif message_type == GLOBAL_POSITION_INT:
        conn.update_current_position(message)
    elif message_type == SYS_STATUS:
        conn.process_sys_status(message)
    elif message_type == COMMAND_ACK:
        pass
    elif message_type == MISSION_ACK:
        pass
    elif message_type == MISSION_REQUEST:
        pass
    elif message_type == MISSION_ITEM_REACHED:
        pass
    elif message_type == RC_CHANNELS:
        logger.info(f"Channel 1: {message.chan1_raw}")
        logger.info(f"Channel 2: {message.chan2_raw}")
        logger.info(f"Channel 3: {message.chan3_raw}")
        logger.info(f"Channel 4: {message.chan4_raw}")


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
        message_id,
        1e6 / frequency_hz,
        0,
        0,
        0,
        0,
        0,
    )


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
