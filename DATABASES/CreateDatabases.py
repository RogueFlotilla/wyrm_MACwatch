#!/usr/bin/env python3

import csv
import sqlite3
from pathlib import Path

# ------------------------------------------ VARIABLES ------------------------------------------ #
DATABASE_DIRECTORY = Path("/opt/wyrm/MACwatch/Database") # Local path to store SQLite databases
DATABASE_DIRECTORY.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist
FP_CSV_PATH = Path("/home/deb-uloq/source/repos/wyrm_MACwatch/DATA/flagged_persons.csv")

WIFI_DATABASE_PATH = DATABASE_DIRECTORY / "wifi_devices.db" # SQLite database of WiFi MACs
BT_DATABASE_PATH = DATABASE_DIRECTORY / "bt_devices.db" # SQLite database of BT MACs
FP_DATABASE_PATH = DATABASE_DIRECTORY / "flagged_persons.db" # SQLite database of BT MACs
# ----------------------------------------------------------------------------------------------- #


## CREATE WIFI DATABASE
def initialize_wifi_database():
    connection = sqlite3.connect(WIFI_DATABASE_PATH)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wifi_devices (
            id INTEGER PRIMARY KEY,
            mac TEXT UNIQUE,
            first_seen FLOAT,
            last_seen FLOAT,
            rssi INTEGER,
            source TEXT,
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
            mac TEXT UNIQUE,
            first_seen FLOAT,
            last_seen FLOAT,
            rssi INTEGER,
            source TEXT,
            manufacturer TEXT
        )
    ''')
    connection.commit()
    connection.close()
    print(f"Bluetooth database initialized at {BT_DATABASE_PATH}")

## CREATE BANNED PERSON DATABASE
def initialize_fp_database():
    connection = sqlite3.connect(FP_DATABASE_PATH)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flagged_persons (
            id INTEGER PRIMARY KEY,
            mac TEXT UNIQUE,
            last_name TEXT,
            first_name TEXT,
            reason TEXT,
            date_added DATE,
            seen BOOLEAN DEFAULT NULL,
            date_seen DATE NULL
        )
    ''')

    # Load Data CSV and insert Data to Table
    if FP_CSV_PATH.exists():
        with open(FP_CSV_PATH, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO flagged_persons (mac, last_name, first_name, reason, date_added)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        row["MAC_Address"].strip(),
                        row["Last_Name"].strip(),
                        row["First_Name"].strip(),
                        row["Reason"].strip(),
                        row["Date_Added"].strip()
                    ))
                except sqlite3.Error as e:
                    print(f"Error inserting {row['MAC_Address']}: {e}")
    
    connection.commit()
    connection.close()
    print(f"Bluetooth database initialized at {FP_DATABASE_PATH}")

## MAIN FUNCTION
if __name__ == "__main__":
    initialize_wifi_database()
    initialize_bt_database()
    initialize_fp_database
