#!/bin/bash

## INSTALL DEPENDENCIES
sudo apt update
sudo apt install -y aircrack-ng iw sqlite3

## SET MONITOR MODE
# Ensure alfa0 exists
if ! ip link show alfa0 > /dev/null 2>&1; then
    echo "Error: alfa0 not found. Unplug and replug in the Alfa."
    exit 1
fi

# Ensure internet on internal adapter remains connected
sudo mkdir -p /etc/NetworkManager/conf.d
echo -e "[keyfile]\nunmanaged-devices=interface-name:alfa0" | sudo tee /etc/NetworkManager/conf.d/monitor-ignore.conf >/dev/null

# Restart network manager
sudo systemctl restart NetworkManager

# Set Alfa to monitor mode
ip link set alfa0 down
iw dev alfa0 set type monitor
ip link set alfa0 up

# Restart Network Manager
sudo systemctl start NetworkManager

## CONFIRM MONITOR MODE SET
echo "Monitor mode should be enabled on alfa0."
iw dev alfa0 info

