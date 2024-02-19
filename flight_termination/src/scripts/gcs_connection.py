import argparse


def main():
    handle_command_line_args()


def handle_command_line_args():
    parser = argparse.ArgumentParser(
        description="""This script runs on the GCS, and creates and maintains a radio connection
        with the drone."""
    )
    parser.parse_args()


if __name__ == "__main__":
    main()
