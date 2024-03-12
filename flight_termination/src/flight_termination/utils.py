MIN_LATITUDE = -90
MAX_LATITUDE = 90
MIN_LONGITUDE = -180
MAX_LONGITUDE = 180

FLIGHT_CONTROLLER_SERIAL_PORT = "/dev/ttyTHS1"
FLIGHT_CONTROLLER_BAUDRATE = 115200


def valid_latitude_and_longitude(lat, lon):
    if lat < MIN_LATITUDE or lat > MAX_LATITUDE:
        return False
    if lon < MIN_LONGITUDE or lon > MAX_LONGITUDE:
        return False
    return True
