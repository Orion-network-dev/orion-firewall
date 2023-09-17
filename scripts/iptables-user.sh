# Simple function to add add a IP redirection
# Used like so: route_ip "<orion ip>" "<local ip>" <(optional) iptables options>
function route_ip {
    ipset add orion-routed $2/32
    iptables -t nat -A POSTROUTING -s $2 -m devgroup --dst-group 2 -j SNAT --to-source $1
    
    # Accept incoming packets from orion interfaces by allowing using the ext-orion chain
    echo ${@:3} | xargs iptables -A ext-orion \
        -d $2 \
        -j ACCEPT
    # Rewrite packets to the destination host.
    echo ${@:3} | xargs iptables -t nat -A PREROUTING \
        -d $1/32 \
        -j DNAT --to-destination $2
}
