import time
from abc import ABC, abstractmethod

from pymavlink import mavutil

from .utils import AUTOPILOT_HEARTBEAT_TIMEOUT, GCS_HEARTBEAT_TIMEOUT, HEARTBEAT, HEARTBEAT_TIMEOUT


class Connection(ABC):
    heartbeat_timeout = None

    def __init__(self, conn_string, baudrate):
        self.conn_string = conn_string
        self.baudrate = baudrate
        self.last_heartbeat = None
        self.conn = None

    @abstractmethod
    def reconnect(self):
        pass

    def update_last_heartbeat(self):
        self.last_heartbeat = time.time()
        print(
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
        raise ConnectionError("Failed to reestablish the connection.")

    def is_valid_connection(self):
        """Check that we have received a heartbeat within the last `heartbeat_timeout`
        seconds."""
        current_time = time.time()
        if current_time - self.last_heartbeat > self.heartbeat_timeout:
            return True
        return False

    def valid_components(self):
        pass

    def get_msg(self):
        msg = self.conn.recv_match()
        return msg


class AutopilotConnection(Connection):
    heartbeat_timeout = AUTOPILOT_HEARTBEAT_TIMEOUT

    def __init__(self, conn_string, baudrate):
        super().__init__(conn_string, baudrate)
        self.conn = connect_to_autopilot(conn_string, baudrate)

    def reconnect(self):
        self.conn = connect_to_autopilot(self.conn_string, self.baudrate)


class GCSConnection(Connection):
    heartbeat_timeout = GCS_HEARTBEAT_TIMEOUT

    def __init__(self, conn_string, baudrate):
        super().__init__(conn_string, baudrate)
        self.conn = connect_to_gcs(conn_string, baudrate)

    def reconnect(self):
        self.conn = connect_to_gcs(self.conn_string, self.baudrate)


def pre_flight_termination():
    pass


def begin_flight_termination():
    pre_flight_termination()
    # Set flight mode to stable.


def handle_connection_health(conn):
    if not conn.is_valid_connection():
        try:
            conn.retry_connection()
        except Exception as e:
            print(e)
            begin_flight_termination()


def connect_to_gcs(connection_string, baudrate):
    return connect_to_mavlink_system(connection_string, baudrate, 0, 0)


def connect_to_autopilot(connection_string, baudrate):
    return connect_to_mavlink_system(connection_string, baudrate, 0, 0)


def connect_to_mavlink_system(connection_string, baudrate, max_retries=0, retry_delay=0):
    """Establish and return a connection to a MAVLink system (e.g., flight controller, GCS).

    Args:
        connection_string (str): The channel for communication (e.g., serial port, network address).
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
            connection = mavutil.mavlink_connection(connection_string, baud=baudrate)
            print("Connected to the flight controller.")
            return connection
        except Exception as e:
            print(f"Error establishing connection (Attempt {attempt}/{num_tries}): {e}")
            if attempt < num_tries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    print("Connection with the flight controller could not be established.")
    return None
