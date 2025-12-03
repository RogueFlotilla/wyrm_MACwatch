#!/bin/bash

sudo apt install pipx
sudo pipx ensurepath

# Install datasette globally via pipx
pipx install datasette

# Run datasette
datasette serve /opt/wyrm/MACwatch/Database/*.db --static css:/home/deb-uloq/source/repos/wyrm_MACwatch/DATABASES
