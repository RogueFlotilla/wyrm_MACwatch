#!/usr/bin/env python3

import sqlite3
from pathlib import Path

# ------------------------------------------ VARIABLES ------------------------------------------ #
DATABASE_DIRECTORY = Path("/opt/wyrm/MACwatch/Database") # Local path to store SQLite databases
DATABASE_DIRECTORY.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist

WIFI_DATABASE_PATH = DATABASE_DIRECTORY / "wifi_devices.db" # SQLite database of WiFi MACs
BT_DATABASE_PATH = DATABASE_DIRECTORY / "bt_devices.db" # SQLite database of BT MACs
# ----------------------------------------------------------------------------------------------- #


## CLEAR WIFI DATABASE
def clear_wifi_database():
    connection = sqlite3.connect(WIFI_DATABASE_PATH)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM wifi_devices")
    connection.commit()
    connection.close()
    print(f"Cleared all entries from {WIFI_DATABASE_PATH}")

## CLEAR BLUETOOTH DATABASE
def clear_bt_database():
    connection = sqlite3.connect(BT_DATABASE_PATH)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM bt_devices")
    connection.commit()
    connection.close()
    print(f"Cleared all entries from {BT_DATABASE_PATH}")

## MAIN FUNCTION
if __name__ == "__main__":
    clear_wifi_database()
    clear_bt_database()
