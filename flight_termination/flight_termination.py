import logging
import os
import subprocess
import time

from pymavlink import mavutil

from navigation.mission import disarm, land, return_to_launch
from navigation.utils import BATTERY_THRESHOLD

logger = logging.getLogger()

RC_OUTPUT = os.getenv("RC_OUTPUT")


def begin_flight_termination(autopilot):
    # TODO: See CONOPS for more flight termintaion instructions.
    logger.info("Beginning flight termination...")
    pre_flight_termination(autopilot)


def pre_flight_termination(autopilot):
    terminate_flight(autopilot)


def terminate_flight(autopilot):
    connection = autopilot.conn
    battery_remaining = autopilot.battery_remaining
    landed = is_drone_landed(connection)

    if landed:
        if connection.motors_armed():
            disarm(connection)
        else:
            logger.info("Already disarmed.")
    elif not battery_remaining or battery_remaining < BATTERY_THRESHOLD:
        # If battery_remaining hasn't been set yet (and hence is None), we are in an undefined
        # state. We could have just started the flight with 100% battery or we could have lost
        # and regained connection with battery level below our threshold. We assume the worst.
        land(connection)
        disarm(connection)
    elif battery_remaining and battery_remaining >= BATTERY_THRESHOLD:
        return_to_launch(connection)


def is_drone_landed(connection):
    """Check if the drone has landed."""
    landed = False
    ext_sys_state = connection.recv_match(
        type=["EXTENDED_SYS_STATE"],
        blocking=True,
        timeout=1,
    )

    if not ext_sys_state:
        logger.info("Did not receive the message in time. Assume not landed.")
    else:
        landed_state = ext_sys_state.landed_state
        landed = landed_state == mavutil.mavlink.MAV_LANDED_STATE_ON_GROUND
        if landed_state == mavutil.mavlink.MAV_LANDED_STATE_LANDING:
            # The drone is currently landing. Wait till it has landed, then disarm.
            logger.info("Drone landing...")
            connection.recv_match(
                type=["EXTENDED_SYS_STATE"],
                condition=f"EXTENDED_SYS_STATE.landed_state == \
                {mavutil.mavlink.MAV_LANDED_STATE_ON_GROUND}",
                blocking=True,
            )
            logger.info("Drone landed.")
            landed = True
    return landed


def get_lsusb_output():
    """Run the lsusb command and return its output."""
    try:
        result = subprocess.run(["lsusb"], stdout=subprocess.PIPE, check=True)
        return result.stdout.decode("utf-8")
    except subprocess.CalledProcessError as e:
        print(f"Error running lsusb: {e}")
        return ""


def is_usb_lost():
    """Detect changes in the lsusb output and return whether there is a change."""
    current_output = get_lsusb_output()
    logger.info(current_output)
    if current_output and RC_OUTPUT not in current_output:
        return True
    return False


def main():
    while True:
        time.sleep(1)
        if is_usb_lost():
            begin_flight_termination(None)


if __name__ == "__main__":
    main()
