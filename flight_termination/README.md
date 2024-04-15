# Flight Termaination

## Overview
Contains code for handling Flight Termination. This includes code that will run on the drone and the Ground Control Station (GCS).

## Table of Contents
- [Requirements](#requirements)
- [Installation](#installation)
- [Flowchart](#flowchart)

## Requirements
- Python 3.xx

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/UMUAS/Nav2023-2024.git
    ```

2. Navigate to the `FlightTermination` directory:

    ```bash
    cd Nav2023-2024
    cd flight_termination
    ```

3. Create, then activate a Python Virtual Environment (Recommended):

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

4. Install Dependencies:

    ```bash
    python -m pip install -r requirements.txt
    ```

5. Run this command to add a system environment variable called PYTHONPATH to allow importing our custom packages:
    - Note: To have this setup for all terminal sessions, add the below command to your shell configuration file called `~/.bashrc` or `~/.bash_profile` for Bash, or `~/.zshrc` for Zsh. For example:
        1. Open the configuration file: `vim ~/.bash_profile`
        2. Add the command below to the end of the file, then save the file.
        3. Restart your terminal or apply the changes to the current shell: `source ~/.bash_profile`

    ```bash
    export PYTHONPATH="${PYTHONPATH}:/ABSOLUTE/PATH/TO/Nav2023-2024/flight_termination/src/"
    ```

## Flowchart
<img width="909" alt="process" src="https://github.com/UMUAS/Nav2023-2024/assets/75279931/b1e69f48-a085-4ede-971e-6ce0769785a1">
