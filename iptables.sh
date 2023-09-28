## Build iptables rules

# IPs allowed to be routed through orion
# This includes by -default- all orion ips


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
    -j SNAT --to-source 10.30.$1.1 \
    -m comment --comment "Packets with dst in orion-net which does not have a orion-net src and have a orion-interface routing target"

iptables -t nat -A POSTROUTING \
    -m set --match-set orion-routed dst \
    -m set ! --match-set orion-net src \
    -m devgroup ! --dst-group 2 \
    -j SNAT --to-source 10.30.$1.1 \
    -m comment --comment "Packets which are dst to a locally-routed orion ip but do not have a orion-net ip and are not destinated to a orion-interface"

iptables -t nat -A POSTROUTING \
    -d 172.30.0.0/15 \
    -d 10.30.0.0/16 \
    -m devgroup --dst-group 2 \
    -j SNAT --to-source 10.30.$1.1