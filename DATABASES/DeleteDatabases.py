#!/usr/bin/env python3

import sqlite3
import os
import variables as variable
from pathlib import Path

## DELETE WIFI DATABASE
def delete_wifi_database():
    if variable.WIFI_DATABASE_PATH.exists():
        variable.WIFI_DATABASE_PATH.unlink()
        print(f"[✓] Deleted database at {variable.WIFI_DATABASE_PATH}")
    else:
        print(f"[›] Database not found, skipping: {variable.WIFI_DATABASE_PATH}")

## DELETE BLUETOOTH DATABASE
def delete_bt_database():
    if variable.BT_DATABASE_PATH.exists():
        variable.BT_DATABASE_PATH.unlink()
        print(f"[✓] Deleted database at {variable.BT_DATABASE_PATH}")
    else:
        print(f"[›] Database not found, skipping: {variable.BT_DATABASE_PATH}")

## DELETE FLAGGED PERSONS DATABASE
def delete_fp_database():
    if variable.FP_DATABASE_PATH.exists():
        variable.FP_DATABASE_PATH.unlink()
        print(f"[✓] Deleted database at {variable.FP_DATABASE_PATH}")
    else:
        print(f"[›] Database not found, skipping: {variable.FP_DATABASE_PATH}")

## MAIN FUNCTION
if __name__ == "__main__":
    try:
        print("[⋯] Deleting all databases...")
        delete_wifi_database()
        delete_bt_database()
        delete_fp_database()
        print("[✓] Deleting databases complete")
    except:
        print("[⚠] Error deleting databases")
