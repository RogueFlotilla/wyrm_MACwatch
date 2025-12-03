#!/bin/bash

apt install -y python3-venv python3-pip

# Provision Virtual Environment
python3 -m venv ~/datasette-venv
source ~/datasette-venv/bin/activate
pip install datasette

# Create log directory
mkdir -p /opt/wyrm/MACwatch/logs/

