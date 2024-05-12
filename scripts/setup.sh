#!/bin/sh

# Commands to run for the initial setup on the companion computer.

set -e

# echo "Updating list of available packages..."
# sudo apt update
# sudo apt -y upgrade

# echo "Installing pip..."
# sudo apt install -y python3-pip

# echo "Creating and activating a Python virtual environment..."
# venv_dir=".venv"
# python3 -m venv $venv_dir
# source $venv_dir/bin/activate

echo "Set custom home takeoff location for SITL"
export PX4_HOME_LAT=49.81351997154947
export PX4_HOME_LON=-97.12035271466196
export PX4_HOME_ALT=0

echo "Adding PYTHONPATH environment variable to shell config file..."
# Get the absolute path of the parent directory.
root_dir="$(realpath "$(dirname "$(pwd)")")"
echo $root_dir
export PYTHONPATH="${PYTHONPATH}:$root_dir"

echo "Installing dependencies using pip..."
python -m pip install -r ../requirements.txt
