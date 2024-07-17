## Build iptables rules

# IPs allowed to be routed through orion
# This includes by -default- all orion ips


iptables -A ext-orion \
    -m set --match-set orion-net dst \
    -j ACCEPT
iptables -A ext-orion \
    -m state --state ESTABLISHED \
    -j ACCEPT

iptables -A ext-orion \
    -j DROP

iptables -A FORWARD \
    -m devgroup --src-group 30 \
    -j ext-orion

iptables -t nat -A POSTROUTING \
    -m set ! --match-set orion-net src \
    -m set --match-set orion-net dst \
    -m devgroup --dst-group 30 \
    -j SNAT --to-source 10.30.$1.1

iptables -t nat -A POSTROUTING \
    -m set --match-set orion-routed dst \
    -m set ! --match-set orion-net src \
    -m devgroup ! --dst-group 30 \
    -j SNAT --to-source 10.30.$1.1

iptables -t nat -A POSTROUTING \
    -s 172.30.0.0/15 \
    -d 10.30.0.0/16 \
    -m devgroup --dst-group 30 \
    -j SNAT --to-source 10.30.$1.1
