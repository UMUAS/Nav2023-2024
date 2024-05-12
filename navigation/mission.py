import logging
import math
import time

from pymavlink import mavutil, mavwp

from .utils import COMMAND_ACK, MISSION_ACK, MISSION_REQUEST

logger = logging.getLogger()


class MissionItem:
    def __init__(
        self,
        conn,
        seq,
        current,
        lat,
        lon,
        alt,
        autocontinue=1,
        hold_time=0.0,
        accept_radius=1.00,
        pass_radius=20.00,
    ):
        self.target_system = conn.target_system
        self.target_component = conn.target_component
        self.seq = seq
        self.frame = mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT
        self.command = mavutil.mavlink.MAV_CMD_NAV_WAYPOINT
        self.current = current
        self.autocontinue = autocontinue
        self.param1 = hold_time
        self.param2 = accept_radius
        self.param3 = pass_radius
        self.param4 = math.nan
        self.x = lat
        self.y = lon
        self.z = alt
        self.mission_type = 0

    @property
    def to_list(self):
        instance_variables = [
            self.target_system,
            self.target_component,
            self.seq,
            self.frame,
            self.command,
            self.current,
            self.autocontinue,
            self.param1,
            self.param2,
            self.param3,
            self.param4,
            self.x,
            self.y,
            self.z,
            self.mission_type,
        ]
        return instance_variables


def upload_mission(conn, waypoints: list[MissionItem]):
    waypoint_loader = mavwp.MAVWPLoader()
    for waypoint in waypoints:
        waypoint_loader.add(mavutil.mavlink.MAVLink_mission_item_message(*waypoint.to_list))

    # Send the number of mission items to the flight controller.
    conn.waypoint_count_send(waypoint_loader.count())

    # Send waypoint to the flight controller.
    for _ in range(waypoint_loader.count()):
        msg = conn.recv_match(type=[MISSION_REQUEST], blocking=True)
        conn.mav.send(waypoint_loader.wp(msg.seq))
        logger.info(f"Sending waypoint: {msg.seq}/{waypoint_loader.count()-1}.")

    msg = conn.recv_match(type=[MISSION_ACK], blocking=True)
    logger.info(msg)

    logger.info("Mission acknowledgement received.")


def set_home(conn, lat, lon, alt, use_curr_location=False):
    if use_curr_location:
        logger.info(f"Setting home position to the current position.")
    else:
        logger.info(f"Setting home position: lat={lat}, lon={lon}, alt={alt}.")
    param1 = 1 if use_curr_location else 0
    conn.mav.command_long_send(
        conn.target_system,
        conn.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_HOME,
        0,
        param1,
        math.nan,
        math.nan,
        math.nan,
        lat,
        lon,
        alt,
    )
    # Wait for command acknowledgment before proceeding.
    msg = conn.recv_match(type=[COMMAND_ACK], blocking=True)
    logger.info(msg)
    msg = conn.recv_match(type=["HOME_POSITION"], blocking=True)
    logger.info(msg)

    # Wait for a couple seconds after setting the home location.
    time.sleep(2)


def command_long_send(
    conn,
    command,
    confirmation=0,
    param1=0,
    param2=0,
    param3=0,
    param4=0,
    param5=0,
    param6=0,
    param7=0,
):
    conn.mav.command_long_send(
        conn.target_system,
        conn.target_component,
        command,
        confirmation,
        param1,
        param2,
        param3,
        param4,
        param5,
        param6,
        param7,
    )


def simple_goto(conn, lat, lon, alt):
    conn.mav.command_long_send(
        conn.target_system,
        conn.target_component,
        mavutil.mavlink.MAV_CMD_DO_REPOSITION,
        0,
        -1,
        mavutil.mavlink.MAV_DO_REPOSITION_FLAGS_CHANGE_MODE,
        1.00,
        math.nan,
        lat,
        lon,
        alt,
    )
    msg = conn.recv_match(type=[COMMAND_ACK], blocking=True)
    logger.info(msg)
    logger.info("Simple goto...")


def arm(conn):
    conn.mav.command_long_send(
        conn.target_system,
        conn.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
    )
    # Wait until arming confirmed (can manually check with master.motors_armed()).
    logger.info("Waiting for the vehicle to arm...")
    conn.motors_armed_wait()
    logger.info("Armed!")


def disarm(conn):
    conn.mav.command_long_send(
        conn.target_system,
        conn.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    )
    # Wait until disarming confirmed.
    logger.info("Waiting for the vehicle to disarm...")
    conn.motors_disarmed_wait()
    logger.info("Disarmed!")


def takeoff(conn):
    conn.mav.command_long_send(
        conn.target_system,
        conn.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0,
        0,
        0,
        0,
        math.nan,
        0,
        0,
        0,
    )
    msg = conn.recv_match(type=[COMMAND_ACK], blocking=True)
    logger.info(msg)
    logger.info("Taking off!")


def start_mission(conn):
    conn.mav.command_long_send(
        conn.target_system,
        conn.target_component,
        mavutil.mavlink.MAV_CMD_MISSION_START,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    )
    msg = conn.recv_match(type=[COMMAND_ACK], blocking=True)
    logger.info(msg)
    logger.info("Started the mission!")


def return_to_launch(conn):
    conn.mav.command_long_send(
        conn.target_system,
        conn.target_component,
        mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    )
    msg = conn.recv_match(type=[COMMAND_ACK], blocking=True)
    logger.info(msg)
    logger.info("Returning to launch point...")


def land(conn):
    conn.mav.command_long_send(
        conn.target_system,
        conn.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    )
    msg = conn.recv_match(type=[COMMAND_ACK], blocking=True)
    logger.info(msg)
    logger.info("Landing...")
