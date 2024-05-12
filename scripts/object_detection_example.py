import io
import logging
import logging.config
import math
import sys
import time

from pymavlink import mavutil

from navigation.connection import AutopilotConnectionWrapper
from navigation.mission import (
    MissionItem,
    arm,
    return_to_launch,
    set_home,
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

autopilot.conn.wait_heartbeat()
logger.info("Heartbeat received from the autopilot.")


# Wait for user input.
while True:
    user_input = input('Enter "yes" to continue: ')
    if user_input.lower() == "yes":
        break


# home_lat = 49.8135194947
# home_lon = -97.120352716196
# home_alt = 0

# Set the home of the drone.
# set_home(autopilot.conn, home_lat, home_lon, home_alt, use_curr_location=True)

# Clear all missions.
autopilot.conn.waypoint_clear_all_send()

# WAYPOINT 1
m1 = MissionItem(conn=autopilot.conn, seq=0, current=2, lat=49.8142336, lon=-97.1205414, alt=20)
waypoints = [m1]
upload_mission(autopilot.conn, waypoints)

# Initial step.
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
    logger.info(msg.__dict__)


# Hold for a few seconds.
time.sleep(1)


# Re-arm.
# arm(autopilot.conn)

# WAYPOINT 2
m2 = MissionItem(conn=autopilot.conn, seq=0, current=2, lat=49.8122997, lon=-97.1186914, alt=20)
waypoints = [m2]
upload_mission(autopilot.conn, waypoints)
start_mission(autopilot.conn)
for mission in waypoints:
    msg = autopilot.conn.recv_match(
        type=["MISSION_ITEM_REACHED"],
        condition=f"MISSION_ITEM_REACHED.seq == {mission.seq}",
        blocking=True,
    )
    logger.info(msg)


# Hold for a few seconds.
time.sleep(1)


# Re-arm.
# arm(autopilot.conn)


# WAYPOINT 3
m3 = MissionItem(conn=autopilot.conn, seq=0, current=2, lat=49.8121986, lon=-97.1202400, alt=20)
waypoints = [m3]
upload_mission(autopilot.conn, waypoints)
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

# # TODO: Verify we have returned before landing.
# land(autopilot.conn)

# # TODO: Verify we have landed before disarming.
# disarm(autopilot.conn)


# NOTE: Clearing missions only at the start and holding once we reach each mission location
# appears to prevent the "No valid mission ..." error.
