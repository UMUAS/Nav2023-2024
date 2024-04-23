"""This script runs on the drone and serves as the process waiting to activate
flight termination."""

import asyncio
import sys

from dotenv import dotenv_values, load_dotenv

from flight_termination.flight_termination import (
    AutopilotConnection,
    begin_flight_termination,
    handle_connection_health,
    heartbeat_loop,
    process_autopilot_msg,
    receive_loop,
)

# Reload environment variables on startup to avoid caching them.
load_dotenv(dotenv_path=".env", verbose=True, override=True)
config = dotenv_values(".env")


async def main():
    try:
        autopilot_conn_string, autopilot_baudrate = (
            config["AUTOPILOT_CONN_STRING"],
            config["AUTOPILOT_BAUDRATE"],
        )
        autopilot_conn = AutopilotConnection(autopilot_conn_string, autopilot_baudrate)
        if not autopilot_conn.conn:
            sys.exit(1)
        # Wait for a heartbeat from the autopilot before sending commands.
        autopilot_conn.conn.wait_heartbeat()
        print("Initial heartbeat received from the autopilot.")

        receive_task = asyncio.create_task(receive_loop())
        heartbeat_task = asyncio.create_task(heartbeat_loop())

        await asyncio.gather(receive_task, heartbeat_task)

    except KeyboardInterrupt:
        print("Exiting...")
        autopilot_conn.conn.close()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
