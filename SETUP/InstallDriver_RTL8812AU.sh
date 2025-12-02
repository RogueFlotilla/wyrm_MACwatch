#!/bin/bash

# ======================================== Wyrm_MACwatch ======================================== #
#
# Script Name:  WyrmInstallDriver_RTL8812AU
# Description:  Installs the most stable RTL8812AU monitor-mode driver from Aircrack-NG.
# Author:       Richard "RogueFlotilla" Flores
# Created:      2025-12-01
# Modified:     2025-12-01
# Version:      dev-2025-12-01
# Usage:        sudo ./InstallDriver_RTL8812AU.sh
# Dependencies: dkms, git, build-essential, raspberrypi-kernel-headers
# Tested on:    Debian 12.10, BlueZ 5.66, Bash 5.2.15-2+b7, Screen 4.9.0-4
# License:      Custom Academic License – for academic, non-commercial use only. See LICENSE.
# Notes:        Developed while attending Marymount University, CAE-CD, Arlington, VA, for the
#               class IT 373 Wireless Networks and Security. Project title: Wi-Fi and BT Alerting
#               for Banned MAC Addresses.
#
# =============================================================================================== #

# ------------------------------------------ VARIABLES ------------------------------------------ #
alfaMAC="00:c0:ca:b8:a6:65" # permanent MAC address for ALFA
alfaNAME="alfa0" # name to assign to this link
ruleFile="/etc/udev/rules.d/70-persistent-net.rules"
# ----------------------------------------------------------------------------------------------- #

## ENSURE SUDO
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root. Please use sudo."
   exit 1
fi

## INSTALL DEPENDENCIES
apt update
apt install -y dkms git build-essential linux-headers-$(uname -r)

## INSTALL DRIVER
cd /home/$USER
git clone https://github.com/aircrack-ng/rtl8812au.git  /tmp/rtl8812au_driver
cd /tmp/rtl8812au_driver
make dkms_install

## RELOAD DRIVER
modprobe -r 8812au 2>/dev/null || true
modprobe 8812au

## CONFIRM DRIVER
ip link

## ENSURE ALFA ALWAYS NAMES SAME
# Remove any existing rules for this MAC, name, or manufacturer
sed -i "\|$alfaMAC|d" "$ruleFile" 2>/dev/null || true
sed -i "\|$alfaNAME|d" "$ruleFile" 2>/dev/null || true
sed -i "\|0bda|d" "$ruleFile" 2>/dev/null || true
sed -i "\|8812|d" "$ruleFile" 2>/dev/null || true

# Add the new rule
echo "SUBSYSTEM==\"net\", ACTION==\"add\", ATTR{address}==\"$alfaMAC\", NAME=\"$alfaNAME\"" | sudo tee -a "$ruleFile" >/dev/null
echo "SUBSYSTEM==\"net\", ACTION==\"add\", ATTRS{idVendor}==\"0bda\", ATTRS{idProduct}==\"8812\", NAME=\"$alfaNAME\"" | sudo tee -a "$ruleFile" >/dev/null

# Reload udev
udevadm control --reload-rules
udevadm trigger

# Output to user
echo "Please unplug and replug the adapter to apply. Then use \"sudo iw dev\" to confirm alfa0 exists."