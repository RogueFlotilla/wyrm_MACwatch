#!/usr/bin/env python3

import csv
import sqlite3
import variables as variable
from pathlib import Path

## CREATE WIFI DATABASE
def initialize_wifi_database():
    connection = sqlite3.connect(variable.WIFI_DATABASE_PATH)
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
    print(f"[✓] WiFi database initialized at {variable.WIFI_DATABASE_PATH}")

## CREATE BLUETOOTH DATABASE
def initialize_bt_database():
    connection = sqlite3.connect(variable.BT_DATABASE_PATH)
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
    print(f"[✓] Bluetooth database initialized at {variable.BT_DATABASE_PATH}")

## CREATE BANNED PERSON DATABASE
def initialize_fp_database():
    connection = sqlite3.connect(variable.FP_DATABASE_PATH)
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
    if variable.FP_CSV_PATH.exists():
        with open(variable.FP_CSV_PATH, "r", encoding="utf-8", errors="ignore") as f:
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
                    print(f"[⚠] Error inserting {row['MAC_Address']}: {e}")
    
    connection.commit()
    connection.close()
    print(f"[✓] Flagged persons database initialized at {variable.FP_DATABASE_PATH}")

## MAIN FUNCTION
if __name__ == "__main__":
    try:
        print("[⋯] Creating all databases...")
        initialize_wifi_database()
        initialize_bt_database()
        initialize_fp_database
        print("[✓] Creating databases complete")
    except:
        print("[⚠] Error creating databases")
