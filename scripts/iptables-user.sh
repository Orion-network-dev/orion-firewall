
function route_ip {
    ipset add orion-routed $2/32
    iptables -t nat -A POSTROUTING -s $2 -m devgroup --dst-group 2 -j SNAT --to-source $1
    iptables -A ext-orion \
        -d $2 \
        -j ACCEPT

    echo ${@:3} | xargs iptables -t nat -A PREROUTING \
        -d $1/32 \
        -j DNAT --to-destination $2
}