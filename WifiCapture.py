#!/usr/bin/env python3
import subprocess
import threading
import time
import re
import sqlite3
import hashlib
from pathlib import Path
from DATABASES.CreateDatabases import initialize_wifi_database

# sys.path.append(str(Path(__file__).parent / "DATABASES"))
# import CreateDatabases

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
# ----------------------------------------------------------------------------------------------- #

## DATABASE FUNCTIONS
# Initialize database if not already done
def initialize_database():
    initialize_wifi_database()

# Hash MAC address for storage in database
def hash_addr(addr: str) -> str:
    return hashlib.sha3_256(SALT + addr.encode()).hexdigest()

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

## CHANNEL HOPPING FUNCTION
def channel_hopper():
    while True:
        for channel in CHANNELS_24 + CHANNELS_50:
            subprocess.run(["sudo", "iw", "dev", INTERFACE, "set", "channel", str(channel)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(CHANNEL_HOP_INTERVAL)

## PACKET CAPTURE FUNCTION
# def capture():
#     proc = subprocess.Popen(
#         [
#             "tshark", "-I", "-i", INTERFACE,
#             "-Y", "wlan.fc.type_subtype == 4 || wlan.fc.type_subtype == 8",
#             "-T", "fields",
#             "-e", "wlan.sa", "-e", "wlan.ta",
#             "-e", "radiotap.dbm_antsignal",
#             "-e", "frame.time_epoch"
#         ],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True
#     )

#     for line in proc.stdout:
#         parts = line.strip().split("\t")
#         if len(parts) < 1:
#             continue

#         macs = [p for p in parts[:2] if MAC_RE.match(p)]
#         signal = int(parts[2]) if len(parts) > 2 and parts[2] else None
#         ts = float(parts[3]) if len(parts) > 3 else time.time()

#         for mac in macs:
#             # Save to database
#             add_device(mac=mac, device_name="wifi", rssi=signal, manufacturer="none")

def capture():
    try:
        proc = subprocess.Popen(
            [
                "tshark", "-I", "-i", INTERFACE,
                "-Y", "wlan.fc.type_subtype == 4 || wlan.fc.type_subtype == 8",
                "-T", "fields",
                "-e", "wlan.sa", "-e", "wlan.ta",
                "-e", "radiotap.dbm_antsignal",
                "-e", "frame.time_epoch"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except FileNotFoundError:
        print("tshark not found. Please install tshark.")
        return
    except Exception as e:
        print(f"Failed to start capture: {e}")
        return

    # Process lines
    for line in proc.stdout:
        print(line.strip())
        try:
            parts = line.strip().split("\t")
            if len(parts) < 1:
                continue

            macs = [p for p in parts[:2] if MAC_RE.match(p)]

            try:
                signal = int(parts[2]) if len(parts) > 2 and parts[2] else None
            except ValueError:
                signal = None

            try:
                ts = float(parts[3]) if len(parts) > 3 else time.time()
            except ValueError:
                ts = time.time()

            for mac in macs:
                # Save to database safely
                try:
                    add_device(mac=mac, device_name="wifi", rssi=signal, manufacturer="none")
                except sqlite3.Error as db_err:
                    print(f"Database error for MAC {mac}: {db_err}")

        except Exception as line_err:
            print(f"Error processing line: {line_err}")


## MAIN FUNCTION
if __name__ == "__main__":
    initialize_database()
    threading.Thread(target=channel_hopper, daemon=True).start()
    while True:
        capture()
