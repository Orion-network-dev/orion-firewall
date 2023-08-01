## Build iptables rules

# Setting up ipsets
ipset create orion-routed hash:net
ipset add orion-routed 10.30.0.0/16
ipset add orion-routed 172.16.0.0/15



# Create a subchain
iptables -N ext-orion

# We accept incoming traffic from orion.
iptables -A ext-orion -m set --match-set orion-routed dst -j ACCEPT

# Allow conns that wera already established.
iptables -A ext-orion -m state --state ESTABLISHED -j ACCEPT
iptables -A ext-orion -j DROP

# We apply our rule to all the orion interfaces.
iptables -A FORWARD -j ext-orion
# We drop all other forwards.
iptables -A FORWARD -j DROP

# Traffic to orion that is not in an orion subnet should be nat translated
# This uses the 10.30.1.1 ip for all outoing connections.
iptables -t nat -A POSTROUTING \
    -m set ! --match-set orion-routed src \
    -m set --match-set orion-routed dst \
    -j SNAT --to-source 10.30.1.1

FC=`cat orion_services`

for kv in $"${FC[@]}" ; do
    ORION_IP=${kv%%:*}
    LOCAL_IP=${kv#*:}

    # Add to the allowed routed
    ipset add orion-routed $ORION_IP/32

    iptables -t nat -A PREROUTING \
        -d $ORION_IP/32 \
        -j DNAT --to-destination $LOCAL_IP
done