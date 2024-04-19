"""This script runs on the drone and serves as the process waiting to activate
flight termination."""

import sys

from flight_termination.flight_termination import (
    AutopilotConnection,
    begin_flight_termination,
    handle_connection_health,
    process_autopilot_msg,
    heartbeat_loop,
)
from flight_termination.utils import load_config

config = load_config()


def main():
    autopilot_conn_string, autopilot_baudrate = (
        config["autopilot_conn_string"],
        config["autopilot_baudrate"],
    )
    autopilot_conn = AutopilotConnection(autopilot_conn_string, autopilot_baudrate)
    if not autopilot_conn.conn:
        sys.exit(1)
    # Wait for a heartbeat from the autopilot before sending commands.
    autopilot_conn.conn.wait_heartbeat()
    print("Initial heartbeat received from the autopilot.")

    while True:
        # Threads:
        # Main thread:
        # Handles received-message queue/buffer.
        # Have 1 thread for sending heartbeat messages.
        # Validating status of components on the drone.

        # Have 1 thread for receiving messages from the Autopilot.
        # Have 1 thread for validating and retrying if necessary, the connection to
        # the Autopilot.

        # asyncio vs threading.

        try:
            # handle_connection_health(autopilot_conn)

            # # Check that the components on the drone are still in an ideal state.
            # if not autopilot_conn.valid_components():
            #     begin_flight_termination()

            # Receive messages from the autopilot.
            autopilot_msg = autopilot_conn.conn.recv_match()
            if autopilot_msg:
                autopilot_conn.check_heartbeat(autopilot_msg)
                # process_autopilot_msg(autopilot_msg)

        except KeyboardInterrupt:
            print("Exiting...")
            autopilot_conn.conn.close()
            sys.exit(1)


if __name__ == "__main__":
    main()
