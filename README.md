# Réseau Orion

> Orion is a network for communicating between IT students. It uses WireGuard and BGP to build a mesh-like network where everyone can publish IPs, DNS domains and L4+ services.

Each participant of the network can publish ips or simply exist in the network.

## Required packages

```bash
apt-get install git frr python3-full wireguard-tools iptables ipset iptables-persistent ipset-persistent netfilter-persistent jq
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Generating wireguard keys

```
./gen-wg.sh
```

Keys are generated in the `wg/` folder.

## Filling the `config.toml` config file

Define each peer in the configuration file according to the spreadsheet,
you need to fill your id, listening port and private key.

## Applying configuration

```
sudo ./update.sh
```

## Configuring FRR

Enable the bgpd daemon in `/etc/frr/daemons`; and define your neighbors like so (will be automated later)

```cisco
!
router bgp 64512
 no bgp ebgp-requires-policy
 no bgp network import-check
 neighbor kylian-prevot peer-group
 neighbor kylian-prevot remote-as 64514
 neighbor 172.30.0.27 peer-group kylian-prevot
 !
 address-family ipv4 unicast
  network 10.30.0.1/32
  network 10.30.0.2/32
  network 10.30.0.3/32
  network 10.30.1.0/24
  network 10.30.2.0/24
  neighbor kylian-prevot prefix-list orion in
  neighbor kylian-prevot prefix-list orion out
  redistribute connected
 exit-address-family
!
ip prefix-list orion seq 10 permit 172.30.0.0/15 le 31 ge 31
ip prefix-list orion seq 15 permit 10.30.0.0/16 le 32 ge 24
!
line vty
!
```