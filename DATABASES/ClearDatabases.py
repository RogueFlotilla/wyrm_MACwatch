#!/usr/bin/env python3

import sqlite3
import variables as variable
from pathlib import Path

## CLEAR WIFI DATABASE
def clear_wifi_database():
    if variable.WIFI_DATABASE_PATH.exists():
        connection = sqlite3.connect(variable.WIFI_DATABASE_PATH)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM wifi_devices")
        connection.commit()
        connection.close()
        print(f"[✓] Cleared all entries from {variable.WIFI_DATABASE_PATH}")
    else:
        print(f"[›] Database not found, skipping: {variable.WIFI_DATABASE_PATH}")

## CLEAR BLUETOOTH DATABASE
def clear_bt_database():
    if variable.BT_DATABASE_PATH.exists():
        connection = sqlite3.connect(variable.BT_DATABASE_PATH)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM bt_devices")
        connection.commit()
        connection.close()
        print(f"[✓] Cleared all entries from {variable.BT_DATABASE_PATH}")
    else:
        print(f"[›] Database not found, skipping: {variable.BT_DATABASE_PATH}")

## CLEAR BLUETOOTH DATABASE
def clear_fp_database():
    if variable.FP_DATABASE_PATH.exists():
        connection = sqlite3.connect(variable.FP_DATABASE_PATH)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM flagged_persons")
        connection.commit()
        connection.close()
        print(f"[✓] Cleared all entries from {variable.FP_DATABASE_PATH}")
    else:
        print(f"[›] Database not found, skipping: {variable.FP_DATABASE_PATH}")

## MAIN FUNCTION
if __name__ == "__main__":
    try:
        print("[⋯] Clearing all database...")
        clear_wifi_database()
        clear_bt_database()
        clear_fp_database()
        print("[✓] Clearing databases complete")
    except:
        print("[⚠] Error clearing databases")
