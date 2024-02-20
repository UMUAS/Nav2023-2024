MIN_LATITUDE = -90
MAX_LATITUDE = 90
MIN_LONGITUDE = -180
MAX_LONGITUDE = 180


def valid_latitude_and_longitude(lat, lon):
    if lat < MIN_LATITUDE or lat > MAX_LATITUDE:
        return False
    if lon < MIN_LONGITUDE or lon > MAX_LONGITUDE:
        return False
    return True
