#!/bin/bash

## INSTALL DEPENDENCIES
sudo apt update
sudo apt install -y aircrack-ng iw sqlite3

## SET MONITOR MODE
# Ensure alfa0 exists
echo "[i] Triggering iw dev to verify alfa0 present"
iw dev # sometimes triggers Alfa to populate

if ! ip link show alfa0 > /dev/null 2>&1; then
    echo "[⚠] alfa0 not found. Unplug and replug in the Alfa."
    exit 1
fi

# Ensure internet on internal adapter remains connected
echo "[i] Ensuring alfa0 will be unmanaged by network interface"
sudo mkdir -p /etc/NetworkManager/conf.d
echo -e "[keyfile]\nunmanaged-devices=interface-name:alfa0" | sudo tee /etc/NetworkManager/conf.d/monitor-ignore.conf >/dev/null

# Stop network manager
echo "[⚠] Warning: Wi-Fi restet in progress"
sudo systemctl stop NetworkManager

# Set Alfa to monitor mode
ip link set alfa0 down
iw dev alfa0 set type monitor
ip link set alfa0 uphttps://www.aircrack-ng.org/doku.php?id=airodump-ng

# Restart Network Manager
sudo systemctl start NetworkManager

## CONFIRM MONITOR MODE SET
echo "Monitor mode should be enabled on alfa0."
iw dev alfa0 info

## RUN WYRM_MACWATCH
# Create databases
python3 -m DATABASES.CreateDatabases
sleep 1

## START DATABASE VIEWER
# Install Database Viewer
chmod +x ./SETUP/InstallDatasette.sh
./SETUP/InstallDatasette.sh

# Run datasette
~/datasette-venv/bin/datasette serve \
    /opt/wyrm/MACwatch/Database/wifi_devices.db \
    /opt/wyrm/MACwatch/Database/bt_devices.db \
    /opt/wyrm/MACwatch/Database/flagged_persons.db \
    --static css:/home/deb-uloq/source/repos/wyrm_MACwatch/DATABASES \
    --metadata /home/deb-uloq/source/repos/wyrm_MACwatch/DATABASES/metadata.json \
    > /opt/wyrm/MACwatch/logs/datasette.log 2>&1 &

# Trap CTRL+C and SIGTERM to stop Datasette
DATASSETTE_PID=$!
trap "echo '[⋯] Stopping Datasette...'; kill $DATASSETTE_PID; echo '[⨯] Datasette stopped.'; exit 0" SIGINT SIGTERM

echo "[i] Datasette server started. It will stop when terminal closes."
echo "[i] Datasette logs stored at /opt/wyrm/MACwatch/logs/datasette.log."
echo -e "[→] Datasette web app viewable at \e]8;;http://127.0.0.1:8001\ahttp://127.0.0.1:8001\e]8;;\a"

## RUN CAPTURE
python3 WifiCapture.py

# When WifiCapture.py exits, kill Datasette
echo "[⨯] Capture stopped."
kill $DATASSETTE_PID
wait $DATASSETTE_PID 2>/dev/null
echo "[i] Databases and logs have been preserved."
echo "[i] Run 'sudo python3 ./DATABASES/ClearDatabases.py' to empty databases."
echo "[i] Run 'sudo python3 ./DATABASES/DeleteDatabases.py' to delete databases."
echo "[✓] Exited Cleanly."
