#!/usr/bin/env python3

from pathlib import Path

# ------------------------------------------ VARIABLES ------------------------------------------ #
DATABASE_DIRECTORY = Path("/opt/wyrm/MACwatch/Database") # Local path to store SQLite databases
DATABASE_DIRECTORY.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist
FP_CSV_PATH = Path("/home/deb-uloq/source/repos/wyrm_MACwatch/DATA/flagged_persons.csv")

WIFI_DATABASE_PATH = DATABASE_DIRECTORY / "wifi_devices.db" # SQLite database of WiFi MACs
BT_DATABASE_PATH = DATABASE_DIRECTORY / "bt_devices.db" # SQLite database of BT MACs
FP_DATABASE_PATH = DATABASE_DIRECTORY / "flagged_persons.db" # SQLite database of BT MACs
# ----------------------------------------------------------------------------------------------- #