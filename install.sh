#!/bin/bash

# Check sudo
if [ "$(id -u)" -ne 0 ]; then
    echo "Please run this script using 'sudo bash install.sh'!"
    exit 1
fi

# Dependencies
apt-get update
apt-get -y install python3
apt-get -y install python3-paho-mqtt
apt-get -y install python3-flask

# Variables
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create service
echo "Creating systemd service file..."

cat <<EOF > "/etc/systemd/system/modbus2mqtt.service"
[Unit]
Description=Python Service: modbus2mqtt
After=network.target

[Service]
ExecStart=/usr/bin/python3 $INSTALL_DIR/main.py
WorkingDirectory=$INSTALL_DIR
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

# Activate service
echo "Activate service..."
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable modbus2mqtt
systemctl start modbus2mqtt

echo "Service modbus2mqtt started."
