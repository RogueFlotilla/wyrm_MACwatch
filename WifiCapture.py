#!/usr/bin/env python3
import subprocess
import threading
import time
import re
import sqlite3
import hashlib
from pathlib import Path
from DATABASES.CreateDatabases import initialize_wifi_database

# ------------------------------------------ VARIABLES ------------------------------------------ #
INTERFACE = "alfa0"

DATABASE_DIRECTORY = Path("/opt/wyrm/MACwatch/Database")    # Local path to store SQLite databases
DATABASE_DIRECTORY.mkdir(parents=True, exist_ok=True)       # Create directory if it doesn't exist
WIFI_DATABASE_PATH = DATABASE_DIRECTORY / "wifi_devices.db" # SQLite database of WiFi MACs

SALT = b"GDPR_Compliance" # For hashing MACs (GDPR Compliance; future proof for US laws possibly)
CHANNEL_HOP_INTERVAL = 5  # seconds
MAC_DECAY_SECONDS = 300   # optional in-memory cache decay

CHANNELS_24 = [1, 6, 11]
CHANNELS_50 = [36, 40, 44, 48, 149, 153, 157, 161]

MAC_RE = re.compile(r"([0-9a-f]{2}:){5}[0-9a-f]{2}")

stop_event = threading.Event()
# ----------------------------------------------------------------------------------------------- #

## DATABASE FUNCTIONS
# Initialize database if not already done
def initialize_database():
    initialize_wifi_database()

# Hash MAC address for storage in database
def hash_addr(addr: str) -> str:
    return hashlib.sha3_256(SALT + addr.encode()).hexdigest()

# Parse Airodump CSV
def parse_airodump_csv(csv_path):
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

        # Add to database
        try:
            add_device(mac=mac, rssi=rssi, device_name="wifi", manufacturer="airodump")
        except sqlite3.Error as db_err:
            print(f"Database error for MAC {mac}: {db_err}")

# Add or update a device to the database
def add_device(mac: str, rssi: int = None, device_name: str = None, manufacturer: str = None):
    hashed_mac = hash_addr(mac)
    ts = time.time()
    connection = sqlite3.connect(WIFI_DATABASE_PATH)
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM wifi_devices WHERE hashed_mac=?", (hashed_mac,))
    row = cursor.fetchone()
    if row:
        cursor.execute(
            "UPDATE wifi_devices SET last_seen=?, rssi=?, manufacturer=? WHERE hashed_mac=?",
            (ts, rssi, manufacturer, hashed_mac)
        )
    else:
        cursor.execute(
            "INSERT INTO wifi_devices (hashed_mac, first_seen, last_seen, rssi, device_name, manufacturer) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (hashed_mac, ts, ts, rssi, device_name, manufacturer)
        )
    connection.commit()
    connection.close()
    return hashed_mac

## PACKET CAPTURE FUNCTION
def capture():
    print(f"\n[+] Starting airodump-ng capture...")
    print("[ ] Screen output is caputred by devnull to increase speed")
    print(f"[ ] Check current database entries with 'sqlite3 {WIFI_DATABASE_PATH}'")

    cmd = [
        "sudo",
        "airodump-ng",
        "--manufacturer",      # optional, gives vendor
        "--write", "/tmp/airodump",
        "--output-format", "csv",
        INTERFACE
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,   # ignore screen output
        stderr=subprocess.DEVNULL
    )

    csv_path = Path("/tmp/airodump-01.csv")

    last_size = 0

    try:
        while True:
            if csv_path.exists():
                size = csv_path.stat().st_size
                if size != last_size:
                    last_size = size
                    parse_airodump_csv(csv_path)
            time.sleep(1)

    except KeyboardInterrupt:
        print(f"\n[!] Stopping capture...")
        proc.terminate()

## MAIN FUNCTION
if __name__ == "__main__":
    initialize_database()
    
    try:
        capture()
    except KeyboardInterrupt:
        print("\n[!] CTRL+C received. Exiting cleanly...")
        stop_event.set()
        print("[+] Shutdown complete.")
