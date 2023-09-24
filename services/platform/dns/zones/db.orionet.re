$TTL 2d ; Default TTL for zone
$ORIGIN orionet.re.

@   IN  SOA ns.orionet.re.  matthieu.matthieu-dev.xyz. (
    0   ; serial number
    12h ; refresh
    15m ; update retry
    3w  ; expiry
    2h  ; minimum
    )
@   IN  NS      nsx1.orion.matthieu-dev.xyz.
@   IN  NS      nsx2.orion.matthieu-dev.xyz.

; Glue record for the orion ns
ns      IN	A  41.213.187.32

dns         IN  A   10.30.0.1
rpki	    IN	A   10.30.0.2
sip		    IN	A	10.30.0.3
routinator  IN  A   10.30.0.4

; Zone for user 1
1   IN  NS      ns
1   IN  DS      22012 13 2 115FD5AEB938B536A0E58FE45254E28D4AF5D59D9639448576B506C0D9D9FBC7
; Zone for user 9
9   IN  NS      ns
9   IN  DS      35259 13 2 941338EC4222FA879A6467B0C5D06B42463597D1ABE4C6C6984F363303FBDF7A
; Zone for user 3
3   IN  NS	ns
3   IN  DS      59193 13 2 8B1DFA302929DD5FE24249008E91FFAFE5A486693007F3A8E28E8339D96FC673
