import argparse
import sys

# Add parent directory to Python path at runtime to allow importing packages.
sys.path.append("../")


from flight_termination.utils import valid_latitude_and_longitude


def main():
    latitude, longitude = get_command_line_args()


def get_command_line_args():
    parser = argparse.ArgumentParser(
        description="""This script runs on the drone and serves as the process waiting to activate
        flight termination.

        Example usage:
        python flight_termination_controller.py --lat 37 --lon -122
        """
    )
    # Define script arguments.
    parser.add_argument(
        "--lat", dest="latitude", type=int, required=True, help="Latitude of the location to land."
    )
    parser.add_argument(
        "--lon",
        dest="longitude",
        type=int,
        required=True,
        help="Longitude of the location to land.",
    )

    arguments = parser.parse_args()
    latitude, longitude = arguments.latitude, arguments.longitude

    if not valid_latitude_and_longitude(latitude, longitude):
        print("Invalid latitude and/or longitude.")
        sys.exit(1)

    return latitude, longitude


if __name__ == "__main__":
    main()
