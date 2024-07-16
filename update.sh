#!/bin/bash

./iptables-clean.sh

echo -e "\t Applying iptables"

# Apply the user rules
./iptables-prelude.sh

if test -f "./iptables-user.sh"; then
    echo -e "\t Apply user iptables rules"
    ./iptables-user.sh
fi

./iptables.sh `cat config.toml | tomlq .id`

netfilter-persistent save
