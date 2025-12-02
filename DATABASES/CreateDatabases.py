#!/usr/bin/env python3

import sqlite3
from pathlib import Path

# ------------------------------------------ VARIABLES ------------------------------------------ #
DATABASE_DIRECTORY = Path("/opt/wyrm/MACwatch/Database") # Local path to store SQLite databases
DATABASE_DIRECTORY.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist

WIFI_DATABASE_PATH = DATABASE_DIRECTORY / "wifi_devices.db" # SQLite database of WiFi MACs
BT_DATABASE_PATH = DATABASE_DIRECTORY / "bt_devices.db" # SQLite database of BT MACs
# ----------------------------------------------------------------------------------------------- #


## CREATE WIFI DATABASE
def initialize_wifi_database():
    connection = sqlite3.connect(WIFI_DATABASE_PATH)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wifi_devices (
            id INTEGER PRIMARY KEY,
            hashed_mac TEXT UNIQUE,
            first_seen FLOAT,
            last_seen FLOAT,
            rssi INTEGER,
            device_name TEXT,
            manufacturer TEXT
        )
    ''')
    connection.commit()
    connection.close()
    print(f"WiFi database initialized at {WIFI_DATABASE_PATH}")

## CREATE BLUETOOTH DATABASE
def initialize_bt_database():
    connection = sqlite3.connect(BT_DATABASE_PATH)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bt_devices (
            id INTEGER PRIMARY KEY,
            hashed_mac TEXT UNIQUE,
            first_seen FLOAT,
            last_seen FLOAT,
            rssi INTEGER,
            device_name TEXT,
            manufacturer TEXT
        )
    ''')
    connection.commit()
    connection.close()
    print(f"Bluetooth database initialized at {BT_DATABASE_PATH}")

## MAIN FUNCTION
if __name__ == "__main__":
    initialize_wifi_database()
    initialize_bt_database()
