import argparse
import sys
import time

# Add parent directory to Python path at runtime to allow importing packages.
sys.path.append("../")


from pymavlink import mavutil

from flight_termination.utils import (
    FLIGHT_CONTROLLER_BAUDRATE,
    FLIGHT_CONTROLLER_SERIAL_PORT,
    valid_latitude_and_longitude,
)


def main():
    latitude, longitude = get_command_line_args()
    conn_flight_controller = connect_to_flight_controller(
        FLIGHT_CONTROLLER_SERIAL_PORT, FLIGHT_CONTROLLER_BAUDRATE
    )

    if conn_flight_controller:
        # Make connection to the GCS.
        # conn_gcs = connect_to_gcs()

        while True:
            try:
                # Do this every so often?
                conn_flight_controller.wait_heartbeat()
                print(
                    f"Heartbeat from system (system {conn_flight_controller.target_system} "
                    f"component {conn_flight_controller.target_component})"
                )
            except KeyboardInterrupt:
                print("Exiting...")
                conn_flight_controller.close()
                sys.exit(1)


def connect_to_gcs(connection_string, baudrate):
    return connect_to_mavlink_system(connection_string, baudrate, 0, 0)


def connect_to_flight_controller(connection_string, baudrate):
    return connect_to_mavlink_system(connection_string, baudrate, 0, 0)


def connect_to_mavlink_system(connection_string, baudrate, max_retries=0, retry_delay=0):
    """Establish and return a connection to a MAVLink system (e.g., flight controller, GCS).

    Args:
        connection_string (str): The channel for communication (e.g., serial port, network address).
        baudrate (int): Number of bits per second transferred over the connection line.
        max_retries (int): Number of additional times we will attempt to make a connection.
        retry_delay (int): Time between in each retry attempt.

    Returns:
        mavutil.mavlink_connection or None: The MAVLink connection object or None if unsuccessful.
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


def get_command_line_args():
    parser = argparse.ArgumentParser(
        description="""This script runs on the drone and serves as the process waiting to activate
        flight termination.

        Example usage:
        python flight_termination_controller.py --lat 37 --lon -122
        """
    )
    # Define script arguments.
    parser.add_argument(
        "--lat", dest="latitude", type=int, required=True, help="Latitude of the location to land."
    )
    parser.add_argument(
        "--lon",
        dest="longitude",
        type=int,
        required=True,
        help="Longitude of the location to land.",
    )

    arguments = parser.parse_args()
    latitude, longitude = arguments.latitude, arguments.longitude

    if not valid_latitude_and_longitude(latitude, longitude):
        print("Invalid latitude and/or longitude.")
        sys.exit(1)

    return latitude, longitude


if __name__ == "__main__":
    main()
