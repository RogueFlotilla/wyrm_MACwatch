#!/bin/bash

## ENSURE SUDO
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root. Please use sudo."
   exit 1
fi

## SET ALFA TO MONITOR MODE
ip link set alfa0 down
iw alfa0 set monitor control
ip link set alfa0 up
iw dev

## CONFIRM MONITOR MODE SET
iw dev

