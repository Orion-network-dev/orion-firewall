#!/bin/bash

ipset -L orion-net > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Creating the Orion-net ipset..."
    ipset create orion-net hash:net
fi

ipset add orion-net 10.30.0.0/16
ipset add orion-net 172.30.0.0/15

ipset -L orion-routed > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Creating the Orion-routed ipset..."
    ipset create orion-routed hash:net
fi

# We create a simple sub-chain to filter incoming packets from the orion interfaces
iptables -N ext-orion