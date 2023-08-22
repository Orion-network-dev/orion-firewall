#!/bin/bash
# Generate 10 sequence numbers

echo |> forwards.conf

for i in `seq 254`
do

cat << EOF >>forwards.conf
zone "$i.orionet.re" {
    type forward;
    forward only;
    forwarders { 10.30.$i.255; };
};

EOF

done