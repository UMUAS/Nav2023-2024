#!/bin/sh

# Entrypoint for flight termination on the nano.

echo "Run flight termination script"
python -m flight_termination_controller.py

# Check for SSH connection to GCS. If we never connect then?
# If we connected initially and we lose connection, set an environment varibale
# to initate flight termination.

export  GCS_CONNECTION_LOST="${GCS_CONNECTION_LOST}GCS_CONNECTION_LOST"
