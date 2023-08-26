$TTL 2d ; Default TTL for zone
$ORIGIN orionet.re.

@   IN  SOA ns.orionet.re.  matthieu.matthieu-dev.xyz. (
    0   ; serial number
    12h ; refresh
    15m ; update retry
    3w  ; expiry
    2h  ; minimum
    )
    IN  NS      nsx1.orion.matthieu-dev.xyz.
    IN  NS      nsx2.orion.matthieu-dev.xyz.

www IN  A       1.1.1.1
ns     IN      A       165.169.145.167
1.orionet.re.  NS      ns.orionet.re.
1.orionet.re. IN DS 22012 13 2 115FD5AEB938B536A0E58FE45254E28D4AF5D59D9639448576B506C0D9D9FBC7
9.orionet.re.  NS      ns.orionet.re.
9.orionet.re. IN DS 35259 13 2 941338EC4222FA879A6467B0C5D06B42463597D1ABE4C6C6984F363303FBDF7A

