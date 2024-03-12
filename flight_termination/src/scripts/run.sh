#!/bin/sh

# Entrypoint for flight termination on the nano.

set -e

echo "Update list of available packages..."
sudo apt update
sudo apt -y upgrade

echo "Installing pip..."
sudo apt install -y python3-pip

# echo "Installing Python packages..."
# sudo apt install python3-dev python3-opencv python3-wxgtk4.0 python3-matplotlib python3-lxml libxml2-dev libxslt-dev

# echo "Installing mavproxy and PyYAML..."
# sudo pip3 install PyYAML mavproxy

# echo "Attempting connection with flight controller..."
# until sudo mavproxy.py --master=/dev/ttyTHS1; do
#     echo "Reattempting connection with flight controller..."
#     sleep 3s
# done

echo "Create, then activate a Python virtual environment..."
venv_dir=".venv"
python3 -m venv $venv_dir
source $venv_dir/bin/activate

echo "Installing dependencies using pip..."
python -m pip install -r ../requirements.txt

echo "Run flight termination script"
python -m flight_termination_controller.py
