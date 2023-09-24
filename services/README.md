# Orion Services

This folder contains all configuration for the Orion services

* `user/` represents services that can be run by any user on their own ip address space
* `platform/` represents services that are run by the platform - Using the 10.30.0.0/24 address space, this is typically anycast adresses.

## Orion Anycast ips

* `10.30.0.1/32` => `dns.orionet.re`   orion dns recursor
* `10.30.0.2/32` => `rpki.orionet.re`  orion rpki trust anchor
* `10.30.0.3/32` => `sip.orionet.re`   orion sip proxy
