#!/bin/bash

echo -e "\t Updating Orion network configurations"

ORION_NET_FILE=/etc/network/interfaces.d/01-orion.conf

# If the interfaces file exists, we must down all interfaces
if test -f "$ORION_NET_FILE"; then
    echo -e "\t Downing interfaces"
    ifdown -i $ORION_NET_FILE
fi

echo -e "\t Shutting down wireguard"
# We down all wireguard tunnels
systemctl stop wg-quick@orion || true

echo -e "\t Regenerating configurations"

# Ru configure script
python3 ./scripts/configure.py

echo -e "\t Enabling wireguard"
# Re-enable wireguard
systemctl enable --now wg-quick@orion || true


echo -e "\t Enabling interfaces"
# Re-enable all interfaces
ifup -i $ORION_NET_FILE


echo -e "\t Applying iptables"
# Apply the user rules
./iptables.sh
if test -f "./iptables-user.sh"; then
    echo -e "\t Apply user iptables rules"
    ./iptables-user.sh
fi
