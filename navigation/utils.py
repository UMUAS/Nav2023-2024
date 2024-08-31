import os

import jinja2

MIN_LATITUDE = -90
MAX_LATITUDE = 90
MIN_LONGITUDE = -180
MAX_LONGITUDE = 180

AUTOPILOT = "Autopilot"
GCS = "GCS"

HEARTBEAT = "HEARTBEAT"
AUTOPILOT_HEARTBEAT_TIMEOUT = 2.5
GCS_HEARTBEAT_TIMEOUT = 2.5
HEARTBEAT_SEND_RATE_HZ = 1

LAT_LON_SCALING_FACTOR = 1.0e7
ALT_SCALING_FACTOR = 1000.0

SYS_STATUS = "SYS_STATUS"
MISSION_REQUEST = "MISSION_REQUEST"
COMMAND_ACK = "COMMAND_ACK"
MISSION_ACK = "MISSION_ACK"
GLOBAL_POSITION_INT = "GLOBAL_POSITION_INT"
BAD_DATA = "BAD_DATA"
MISSION_ITEM_REACHED = "MISSION_ITEM_REACHED"
RC_CHANNELS = "RC_CHANNELS"
SYS_STATUS = "SYS_STATUS"

BATTERY_THRESHOLD = 70


def valid_latitude_and_longitude(lat, lon):
    if lat < MIN_LATITUDE or lat > MAX_LATITUDE:
        return False
    if lon < MIN_LONGITUDE or lon > MAX_LONGITUDE:
        return False
    return True


def get_logging_config():
    nav_dir = get_nav_dir()

    # Load the logging configuration template file.
    template_loader = jinja2.FileSystemLoader(searchpath=nav_dir)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("logging.conf")

    log_file_abs_path = os.path.join(nav_dir, "app.log")

    # Render the template with variables.
    logging_config = template.render(log_file_path=log_file_abs_path)
    return logging_config


def get_nav_dir():
    curr_path = os.path.dirname(__file__)
    nav_dir = os.path.abspath(os.path.join(curr_path, os.pardir))
    return nav_dir
