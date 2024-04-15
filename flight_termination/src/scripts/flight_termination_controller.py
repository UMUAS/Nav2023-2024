import argparse

# import configparser
import sys

# Add parent directory to Python path at runtime to allow importing packages.
sys.path.append("../")

from flight_termination.flight_termination import (
    AutopilotConnection,
    GCSConnection,
    begin_flight_termination,
    handle_connection_health,
    process_autopilot_msg,
    send_heartbeat,
)
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
    if not autopilot_conn.conn:
        sys.exit(1)
    # Wait for a heartbeat from the autopilot before sending commands.
    autopilot_conn.conn.wait_heartbeat()
    print("Initial heartbeat received from the autopilot.")

    gcs_conn = GCSConnection(GCS_SERIAL_PORT, GCS_BAUDRATE)
    if not gcs_conn.conn:
        sys.exit(1)
    # Wait for a heartbeat from the GCS before sending commands.
    gcs_conn.conn.wait_heartbreat()
    print("Initial heartbeat received from the GCS.")

    # Send heartbeat messages to the autopilot and GCS.
    send_heartbeat(autopilot_conn)
    send_heartbeat(gcs_conn)

    while True:
        # Threads:
        # Main thread:
        # Handles received-message queue/buffer.
        # Have 1 thread for sending heartbeat messages.
        # Validating status of components on the drone.

        # Have 1 thread for receiving messages from the Autopilot.
        # Have 1 thread for receiving messages from the GCS.
        # Have 1 thread for validating and retrying if necessary, the connection to
        # the Autopilot and GCS.

        # asyncio vs threading.

        try:
            # handle_connection_health(autopilot_conn)
            # handle_connection_health(gcs_conn)

            # # Check that the components on the drone are still in an ideal state.
            # if not autopilot_conn.valid_components():
            #     begin_flight_termination()

            # Receive messages from the ground control station.
            gcs_msg = gcs_conn.conn.recv_match()
            if gcs_msg:
                gcs_conn.check_heartbeat(gcs_msg)

            # Receive messages from the autopilot.
            autopilot_msg = autopilot_conn.conn.recv_match()
            if autopilot_msg:
                autopilot_conn.check_heartbeat(autopilot_msg)
                # process_autopilot_msg(autopilot_msg)

        except KeyboardInterrupt:
            print("Exiting...")
            autopilot_conn.conn.close()
            gcs_conn.conn.close()
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
