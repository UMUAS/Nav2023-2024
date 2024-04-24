"""This script runs on the drone and serves as the process waiting to activate
flight termination."""

import asyncio
import os
import sys

from dotenv import load_dotenv
from flight_termination.flight_termination import (
    AutopilotConnection,
    heartbeat_loop,
    receive_msg_loop,
    validate_connection_loop,
)

# Reload environment variables on startup to avoid caching them.
load_dotenv(verbose=True, override=True)


async def main():
    try:
        autopilot_conn_string = os.getenv("AUTOPILOT_CONN_STRING")
        autopilot_baudrate = os.getenv("AUTOPILOT_BAUDRATE")

        autopilot_conn = AutopilotConnection(autopilot_conn_string, autopilot_baudrate)
        if not autopilot_conn.conn:
            sys.exit(1)

        # Wait for a heartbeat from the autopilot before sending commands.
        autopilot_conn.conn.wait_heartbeat()
        print("Initial heartbeat received from the autopilot.")

        # Request messages from the flight controller.
        autopilot_conn.request_messages()

        # Gather asynchronous tasks.
        receive_task = asyncio.create_task(receive_msg_loop(autopilot_conn))
        heartbeat_task = asyncio.create_task(heartbeat_loop(autopilot_conn))
        validate_connection_task = asyncio.create_task(validate_connection_loop(autopilot_conn))

        await asyncio.gather(receive_task, heartbeat_task, validate_connection_task)

    except KeyboardInterrupt:
        print("Exiting...")
        autopilot_conn.conn.close()
        sys.exit(1)

    except ConnectionError as e:
        # We lost connection and could not re-establish.
        print(e)
        if e == "Failed to re-establish the connection.":
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
