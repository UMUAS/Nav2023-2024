import json
import sys

MIN_LATITUDE = -90
MAX_LATITUDE = 90
MIN_LONGITUDE = -180
MAX_LONGITUDE = 180

AUTOPILOT = "Autopilot"
GCS = "GCS"

HEARTBEAT = "HEARTBEAT"
AUTOPILOT_HEARTBEAT_TIMEOUT = 5
GCS_HEARTBEAT_TIMEOUT = 5
HEARTBEAT_TIMEOUT = 2

HEARTBEAT_SEND_RATE_HZ = 1
MESSAGE_CHECK_INTERVAL = 0.01

SYS_STATUS = "SYS_STATUS"


def valid_latitude_and_longitude(lat, lon):
    if lat < MIN_LATITUDE or lat > MAX_LATITUDE:
        return False
    if lon < MIN_LONGITUDE or lon > MAX_LONGITUDE:
        return False
    return True


def load_config():
    with open("../config.json", "r") as file:
        config = json.load(file)

    # Check latitude and longitude.
    latitude, longitude = config["latitude"], config["longitude"]
    if not valid_latitude_and_longitude(latitude, longitude):
        print("Invalid latitude and/or longitude.")
        sys.exit(1)

    return config
