import unittest

from src.flight_termination.utils import (
    MAX_LATITUDE,
    MAX_LONGITUDE,
    MIN_LATITUDE,
    MIN_LONGITUDE,
    valid_latitude_and_longitude,
)


class TestLatAndLonValidator(unittest.TestCase):
    def test_valid_latitudes_and_longitudes(self):
        for latitude in range(MIN_LATITUDE, MAX_LATITUDE + 1):
            for longitude in range(MIN_LONGITUDE, MAX_LONGITUDE + 1):
                result = valid_latitude_and_longitude(latitude, longitude)
                self.assertTrue(result)

    def test_invalid_latitudes(self):
        latitude = MIN_LATITUDE - 1
        longitude = MAX_LONGITUDE
        result = valid_latitude_and_longitude(latitude, longitude)
        self.assertFalse(result)

        latitude = MAX_LATITUDE + 1
        longitude = MAX_LONGITUDE
        result = valid_latitude_and_longitude(latitude, longitude)
        self.assertFalse(result)

    def test_invalid_longitudes(self):
        latitude = MIN_LATITUDE
        longitude = MAX_LONGITUDE + 1
        result = valid_latitude_and_longitude(latitude, longitude)
        self.assertFalse(result)

        latitude = MIN_LATITUDE
        longitude = MIN_LONGITUDE - 1
        result = valid_latitude_and_longitude(latitude, longitude)
        self.assertFalse(result)
