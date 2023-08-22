$TTL 2d ; Default TTL for zone
$ORIGIN 0.orionet.re.

@   IN  SOA nsx1.orion.matthieu-dev.xyz.  matthieu.matthieu-dev.xyz. (
    0   ; serial number
    12h ; refresh
    15m ; update retry
    3w  ; expiry
    2h  ; minimum
    )
    IN  NS      nsx1.orion.matthieu-dev.xyz.
    IN  NS      nsx2.orion.matthieu-dev.xyz.
pki IN  CNAME   pki.1.orionet.re.

