#!/usr/bin/env python3

import csv
import hashlib
import re
import sqlite3
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
import DATABASES.CreateDatabases as CreateDatabase
import DATABASES.variables as variable

# ------------------------------------------ VARIABLES ------------------------------------------ #
INTERFACE = "alfa0"

DATABASE_DIRECTORY = Path("/opt/wyrm/MACwatch/Database")    # Local path to store SQLite databases
DATABASE_DIRECTORY.mkdir(parents=True, exist_ok=True)       # Create directory if it doesn't exist
WIFI_DATABASE_PATH = DATABASE_DIRECTORY / "wifi_devices.db" # SQLite database of WiFi MACs
FP_CSV_PATH = Path("/home/deb-uloq/source/repos/wyrm_MACwatch/DATA/flagged_persons.csv")
FP_DATABASE_PATH = DATABASE_DIRECTORY / "flagged_persons.db" # SQLite database of BT MACs

CSV_DATA_PATH = Path("/home/deb-uloq/source/repos/wyrm_MACwatch/DATA/IEEE-standards-oui.csv")

SALT = b"GDPR_Compliance" # For hashing MACs (GDPR Compliance; future proof for US laws possibly)
CHANNEL_HOP_INTERVAL = 5  # seconds
MAC_DECAY_SECONDS = 300   # optional in-memory cache decay

MAC_RE = re.compile(r"([0-9a-f]{2}:){5}[0-9a-f]{2}")

stop_event = threading.Event()
# ----------------------------------------------------------------------------------------------- #

## DATABASE FUNCTIONS
# Initialize database if not already done
def initialize_database():
    CreateDatabase.initialize_wifi_database()
    CreateDatabase.initialize_fp_database()

# Hash MAC address for storage in database
def hash_addr(addr: str) -> str:
    return hashlib.sha3_256(SALT + addr.encode()).hexdigest()

# Parse Airodump CSV
def parse_airodump_csv(csv_path, oui_dictionary):
    try:
        with open(csv_path, "r", errors="ignore") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return

    in_client_section = False

    for line in lines:
        line = line.strip()

        # Section separator
        if line.startswith("Station MAC,"):
            in_client_section = True
            continue

        if not in_client_section:
            continue  # Skip AP table

        parts = [p.strip() for p in line.split(",")]

        # Ensure it looks like a station row
        if len(parts) < 6:
            continue

        mac = parts[0]
        if not MAC_RE.match(mac.lower()):
            continue

        # RSSI (column 3 in client section)
        try:
            rssi = int(parts[3])
        except:
            rssi = None

        # VENDOR ASSOCIATION
        try:
            vendor = associate_vendor(mac, oui_dictionary)
        except:
            vendor="Not Found, Possibly Randomized"

        # Add to database
        try:
            add_device(mac=mac, rssi=rssi, source="Airodump-ng", manufacturer=vendor)
        except sqlite3.Error as db_err:
            print(f"Database error for MAC {mac}: {db_err}")

# Add or update a device to the database
def add_device(mac: str, rssi: int = None, source: str = None, manufacturer: str = None):
    mac = hash_addr(mac) # Hash mac w/ salt; Comment out to deanonymize
    ts = time.time()  # Unix Timestamp; Comment out next line to keep unformatted
    # ts = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S.%f")
    connection = sqlite3.connect(WIFI_DATABASE_PATH)
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM wifi_devices WHERE mac=?", (mac,))
    row = cursor.fetchone()
    if row:
        cursor.execute(
            "UPDATE wifi_devices SET last_seen=?, rssi=?, manufacturer=? WHERE mac=?",
            (ts, rssi, manufacturer, mac)
        )
    else:
        cursor.execute(
            "INSERT INTO wifi_devices (mac, first_seen, last_seen, rssi, source, manufacturer) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (mac, ts, ts, rssi, source, manufacturer)
        )
    connection.commit()
    connection.close()

    # Check if MAC in flagged persons list
    connection = sqlite3.connect(FP_DATABASE_PATH)
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM flagged_persons WHERE mac=?", (mac,))
    row = cursor.fetchone()
    if row:
        cursor.execute(
            "UPDATE flagged_persons SET seen=?, date_seen=? WHERE mac=?",
            (True, ts, mac)
        )
    connection.commit()
    connection.close()

    return mac

def load_oui_csv(CSV_DATA_PATH):
    oui_dictionary = {}

    with open(CSV_DATA_PATH, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            prefix = row["Assignment"].strip().upper()

            # Use the first occurrence only
            if prefix not in oui_dictionary:
                oui_dictionary[prefix] = row["Organization Name"].strip()

    return oui_dictionary

def associate_vendor(mac, oui_dictionary):
    # https://standards-oui.ieee.org/oui/oui.csv
    # Remove anything that's not hex
    cleaned = re.sub(r'[^0-9A-Fa-f]', '', mac)

    # Need the first 6 hex digits = 3 bytes
    if len(cleaned) < 6:
        return "ERROR: Prefix was < 6"

    prefix = cleaned[:6].upper()

    # Check if MAC is randomized using the locally administered bit
    first_byte = int(cleaned[:2], 16)
    if first_byte & 0b10:  # LAA bit set
        return "randomized"
    # Check if MAC is in IEEE OUI Database, otherwise return unknown
    return oui_dictionary.get(prefix, "unknown")

## PACKET CAPTURE FUNCTION
def capture():
    print(f"[⋯] Starting airodump-ng capture...")
    print("[i] Screen output is caputred by devnull to increase speed")
    print("[i] Airodump-ng capture stored at /opt/wyrm/MACwatch/logs/airodump-*.csv.")
    print(f"[i] Check current database entries with 'sqlite3 {WIFI_DATABASE_PATH}'")

    oui_dictionary = load_oui_csv(CSV_DATA_PATH)

    cmd = [
        "sudo",
        "airodump-ng",
        "--manufacturer",      # optional, gives vendor
        "--write", "/opt/wyrm/MACwatch/logs/airodump",
        "--output-format", "csv",
        INTERFACE
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,   # ignore screen output
        stderr=subprocess.DEVNULL
    )

    def get_latest_airodump_csv():
        files = sorted(Path("/opt/wyrm/MACwatch/logs/").glob("airodump-*.csv"))
        if not files:
            return None
        return files[-1]  # newest file

    last_size = 0

    while True:
        csv_path = get_latest_airodump_csv()
        if csv_path and csv_path.exists():
            size = csv_path.stat().st_size
            if size != last_size:
                last_size = size
                parse_airodump_csv(csv_path, oui_dictionary)
        time.sleep(1)       

def abort_run():
    print("\n[⋯] CTRL+C received. Exiting cleanly...")
    print("[⋯] Stopping capture...")

## MAIN FUNCTION
if __name__ == "__main__":
    initialize_database()
    
    try:
        capture()
    except KeyboardInterrupt:
        abort_run()
