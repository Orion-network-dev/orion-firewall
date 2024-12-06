#!/usr/bin/env python3
import sys

sys.path.append("/usr/lib/orion-firewall")

import nftables
import nftgen
import orion_config
import toml


def main():
    schema = orion_config.FirewallConfig()
    file = open("/etc/orion-firewall/config.toml", "r")
    config = schema.load(toml.load(file))

    nft = nftables.Nftables()
    ops = nftgen.nft(config)
    
    ruleFile = {"nftables": ops}
    
    nft.json_validate(ruleFile)
    rc, output, error = nft.json_cmd(ruleFile)
    if rc != 0:
        # do proper error handling here, exceptions etc
        print(f"ERROR: running json cmd: {error}")
        exit(1)
    if len(output) != 0:
        # more error control?
        print(f"WARNING: output: {output}")
    file.close()

if __name__ == "__main__":
    main()
