## Build iptables rules

# IPs allowed to be routed through orion
# This includes by -default- all orion ips

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

iptables -A ext-orion \
    -m set --match-set orion-routed dst \
    -j ACCEPT \
    -m comment --comment "Accept traffic destinated to a Orion-routed ip address"

iptables -A ext-orion \
    -m set --match-set orion-net dst \
    -j ACCEPT \
    -m comment --comment "Accept traffic destinated to a Orion network"

iptables -A ext-orion \
    -m state --state ESTABLISHED \
    -j ACCEPT \
    -m comment --comment "Allow already established conns"

iptables -A ext-orion \
    -j DROP \
    -m comment --comment "Drop packets by default"

iptables -A FORWARD \
    -m devgroup --src-group 2 \
    -j ext-orion \
    -m comment --comment "Allow forwarding given the forwarding rules for Orion"

iptables -t nat -A POSTROUTING \
    -m set ! --match-set orion-net src \
    -m set --match-set orion-net dst \
    -m devgroup --dst-group 2 \
    -j MASQUERADE \
    -m comment --comment "Packets with dst in orion-net which does not have a orion-net src and have a orion-interface routing target"

iptables -t nat -A POSTROUTING \
    -m set --match-set orion-routed dst \
    -m set ! --match-set orion-net src \
    -m devgroup ! --dst-group 2 \
    -j MASQUERADE \
    -m comment --comment "Packets which are dst to a locally-routed orion ip but do not have a orion-net ip and are not destinated to a orion-interface"
