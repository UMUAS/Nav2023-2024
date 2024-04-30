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

echo "Adding PYTHONPATH environment variable to shell config file..."
# Get the absolute path of the parent directory.
root_dir="$(realpath "$(dirname "$(pwd)")")"
export PYTHONPATH="${PYTHONPATH}:$root_dir"

echo "Installing dependencies using pip..."
python -m pip install -r ../requirements.txt
