#!/bin/bash

function route_ip {
    iptables add orion-routed $2/32
    echo ${@:2} | xargs iptables -t nat -A PREROUTING \
        -d $1/32 \
        -j DNAT --to-destination $2
}

# Exposer un serveur (tout les ports acceptés)
route_ip "10.30.1.1" "192.168.1.1"
# Exposer un serveur seulement sur le port 80
route_ip "10.30.1.2" "192.168.1.2" -p tcp --dport 80
