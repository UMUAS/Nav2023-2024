"""A test script for sending waypoints all at once to the flight controller -
A mission."""

import io
import logging
import logging.config
import sys
import time

from navigation.connection import AutopilotConnectionWrapper
from navigation.mission import (
    MissionItem,
    arm,
    return_to_launch,
    start_mission,
    takeoff,
    upload_mission,
)
from navigation.utils import get_logging_config

# Configure logging.
logging_config = get_logging_config()
logging.config.fileConfig(io.StringIO(logging_config), disable_existing_loggers=False)

logger = logging.getLogger()

autopilot = AutopilotConnectionWrapper("udpin:localhost:14540")

logger.info("Waiting for a heartbeat from the autopilot...")
autopilot.conn.wait_heartbeat()
logger.info("Heartbeat received from the autopilot.")


# batter_status_msg = autopilot.conn.recv_match(type=["BATTERY_STATUS"], blocking=True)
# sys_status_msg = autopilot.conn.recv_match(type=["SYS_STATUS"], blocking=True)
# logger.info(batter_status_msg)
# logger.info(sys_status_msg)


# Request all parameters.
autopilot.conn.mav.param_request_list_send(
    autopilot.conn.target_system, autopilot.conn.target_component
)

start_time = time.time()
while True:
    try:
        message = autopilot.conn.recv_match(type="PARAM_VALUE", blocking=True, timeout=1)
        if message:
            messsage_dict = message.to_dict()
            logger.info(
                f"name: {messsage_dict['param_id']}\tvalue: {messsage_dict['param_value']}."
            )
    except Exception as error:
        logger.exception(error)
        sys.exit(0)

    end_time = time.time()
    if end_time - start_time >= 5:
        break

# Wait for user input.
while True:
    user_input = input('Enter "yes" to continue: ')
    if user_input.lower() == "yes":
        break


home_lat = 49.81351997154947
home_lon = -97.12035271466196
home_alt = 0

# Set the home of the drone.
# set_home(autopilot.conn, home_lat, home_lon, home_alt, use_curr_location=False)

# Clear all missions.
autopilot.conn.waypoint_clear_all_send()

m1 = MissionItem(conn=autopilot.conn, seq=0, current=0, lat=49.8142336, lon=-97.1205414, alt=20)
m2 = MissionItem(conn=autopilot.conn, seq=1, current=0, lat=49.8122997, lon=-97.1186914, alt=20)
m3 = MissionItem(conn=autopilot.conn, seq=2, current=0, lat=49.8121986, lon=-97.1202400, alt=20)
waypoints = [m1, m2, m3]

upload_mission(autopilot.conn, waypoints)
arm(autopilot.conn)
takeoff(autopilot.conn)
start_mission(autopilot.conn)

for mission in waypoints:
    msg = autopilot.conn.recv_match(
        type=["MISSION_ITEM_REACHED"],
        condition=f"MISSION_ITEM_REACHED.seq == {mission.seq}",
        blocking=True,
    )
    logger.info(msg)

# Hold for a couple seconds.
time.sleep(2)


return_to_launch(autopilot.conn)
