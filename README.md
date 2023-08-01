# Réseau Orion

> Orion is a network for communicating between IT students. It uses WireGuard and BGP to build a mesh-like network where everyone can publish IPs, DNS domains and L4+ services.

Structure of a orion packet:

```
+----------------+
|    IP Packet   |
+----------------+
|    GRE         |
+----------------+
|    IP          |
+----------------+
|    WireGuard   |
+----------------+
|    IP          |
+----------------+
|    Ethernet    |
+----------------+
```

Each participant of the network can publish ips or simply exist in the network.