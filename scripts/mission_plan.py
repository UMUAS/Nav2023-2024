import io
import logging
import logging.config
import sys
import time

from navigation.connection import AutopilotConnectionWrapper
from navigation.mission import (
    MissionItem,
    arm,
    disarm,
    land,
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

autopilot.conn.wait_heartbeat()
logger.info("Heatbeat received from the autopilot.")

# Request all parameters.
autopilot.conn.mav.param_request_list_send(
    autopilot.conn.target_system, autopilot.conn.target_component
)

start_time = time.time()
while True:
    time.sleep(0.01)
    try:
        message = autopilot.conn.recv_match(type="PARAM_VALUE", blocking=True).to_dict()
        logger.info(f"name: {message['param_id']}\tvalue: {message['param_value']}.")
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

m1 = MissionItem(conn=autopilot.conn, seq=0, current=0, lat=28.452050, lon=-13.865000, alt=10)
m2 = MissionItem(conn=autopilot.conn, seq=1, current=0, lat=28.452300, lon=-13.865200, alt=10)
m3 = MissionItem(conn=autopilot.conn, seq=2, current=0, lat=28.451000, lon=-13.865909, alt=10)
waypoints = [m1, m2, m3]

upload_mission(
    autopilot.conn, waypoints, home_lat=35.3632618888, home_lon=149.165236018, home_alt=10
)
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

# Hold for a few seconds.
time.sleep(5)

return_to_launch(autopilot.conn)

# TODO: Verify we have returned before landing.
land(autopilot.conn)

# TODO: Verify we have landed before disarming.
disarm(autopilot.conn)
