## Build iptables rules

# Setting up ipsets
ipset create orion hash:net
ipset add orion 10.30.0.0/16
ipset add orion 172.16.0.0/15

# Create a subchain
iptables -N ext-orion

# We accept incoming traffic from orion.
iptables -A ext-orion -m set --match-set orion dst -j ACCEPT

# If you have a service that is manually exposed
# You need to allow forwarding to it.

# For example, I expose an http server (port 80) running on 192.168.1.40.
iptables -A ext-orion -d 192.168.1.40 -p tcp --dport 80 -j ACCEPT

# Allow conns that wera already established.
iptables -A ext-orion -m state --state ESTABLISHED -j ACCEPT
iptables -A ext-orion -j DROP

# We apply our rule to all the orion interfaces.
iptables -A FORWARD -m devgroup --src-group 2 -j ext-orion
# We drop all other forwards.
iptables -A FORWARD -j DROP

# Traffic to orion that is not in an orion subnet should be nat translated
iptables -t nat -A POSTROUTING \
    -m set ! --match-set orion src \
    -m set --match-set orion dst \
    -j MASQUERADE

# We translate traffic destinated to our http service to the internal ip
# In this case, we expose our service to 10.30.1.1/32
iptables -t nat -A PREROUTING \
    -d 10.30.1.1/32 \
    -j DNAT --to-destination 192.168.1.40
