#!/bin/bash
# Generate 10 sequence numbers

echo |> db.orionet.re

cat << EOF >db.orionet.re
\$TTL 2d ; Default TTL for zone
\$ORIGIN orionet.re.

@   IN  SOA ns.orionet.re.  matthieu.matthieu-dev.xyz. (
    0   ; serial number
    12h ; refresh
    15m ; update retry
    3w  ; expiry
    2h  ; minimum
    )
    IN  NS  nsx1.orion.matthieu-dev.xyz.
    IN  NS  nsx2.orion.matthieu-dev.xyz.

EOF

for i in `seq 254`
do

cat << EOF >>db.orionet.re
\$ORIGIN $i.orionet.re.
@   IN  NS  ns
ns  IN  A   10.30.$i.255

EOF

done