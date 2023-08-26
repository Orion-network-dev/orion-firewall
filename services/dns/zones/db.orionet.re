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

www             IN A  1.1.1.1
; primary nameserver
ns              IN A  165.169.145.167

; Zone for user 1
all IN  CNAME   1
1   IN  NS      ns
1   IN  DS      22012 13 2 115FD5AEB938B536A0E58FE45254E28D4AF5D59D9639448576B506C0D9D9FBC7
; Zone for user 9
all IN  CNAME   9
9   IN  NS      ns
9   IN  DS      35259 13 2 941338EC4222FA879A6467B0C5D06B42463597D1ABE4C6C6984F363303FBDF7A
