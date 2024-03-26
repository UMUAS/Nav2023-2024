import argparse
import configparser
import sys
import time

# Add parent directory to Python path at runtime to allow importing packages.
sys.path.append("../")

from flight_termination.flight_termination import AutopilotConnection, GCSConnection
from flight_termination.utils import (
    AUTOPILOT_BAUDRATE,
    AUTOPILOT_SERIAL_PORT,
    GCS_BAUDRATE,
    GCS_SERIAL_PORT,
    valid_latitude_and_longitude,
)


def main():
    latitude, longitude = get_command_line_args()
    autopilot_conn = AutopilotConnection(AUTOPILOT_SERIAL_PORT, AUTOPILOT_BAUDRATE)

    if autopilot_conn:
        # Wait for a heartbeat from the autopilot before sending commands.
        autopilot_conn.conn.wait_heartbeat()

        gcs_conn = GCSConnection(GCS_SERIAL_PORT, GCS_BAUDRATE)
        # Wait for a heartbeat from the GCS before sending commands.
        gcs_conn.conn.wait_heartbreat()

        while True:
            try:
                msg = autopilot_conn.conn.recv_match()
                if msg:
                    autopilot_conn.check_heartbeat(msg)

            except KeyboardInterrupt:
                print("Exiting...")
                autopilot_conn.close()
                sys.exit(1)


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
