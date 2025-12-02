#!/usr/bin/env python3

import sqlite3
import os
from pathlib import Path

# ------------------------------------------ VARIABLES ------------------------------------------ #
DATABASE_DIRECTORY = Path("/opt/wyrm/MACwatch/Database") # Local path to store SQLite databases
DATABASE_DIRECTORY.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist

WIFI_DATABASE_PATH = DATABASE_DIRECTORY / "wifi_devices.db" # SQLite database of WiFi MACs
BT_DATABASE_PATH = DATABASE_DIRECTORY / "bt_devices.db" # SQLite database of BT MACs
# ----------------------------------------------------------------------------------------------- #


## DELETE WIFI DATABASE
def delete_wifi_database():
    if WIFI_DATABASE_PATH.exists():
        WIFI_DATABASE_PATH.unlink()
        print(f"Deleted database at {WIFI_DATABASE_PATH}")
    else:
        print(f"Database not found, skipping: {WIFI_DATABASE_PATH}")

## DELETE BLUETOOTH DATABASE
def delete_bt_database():
    if BT_DATABASE_PATH.exists():
        BT_DATABASE_PATH.unlink()
        print(f"Deleted database at {BT_DATABASE_PATH}")
    else:
        print(f"Database not found, skipping: {BT_DATABASE_PATH}")

## MAIN FUNCTION
if __name__ == "__main__":
    delete_wifi_database()
    delete_bt_database()
