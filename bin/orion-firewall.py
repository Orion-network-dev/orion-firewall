#!/usr/bin/env python3
import sys

sys.path.append("/usr/lib/orion-firewall")
import nftables
from utils import *
import toml


def main():
    nft = nftables.Nftables()

    with open("/etc/orion-firewall/config.toml", "r") as f:
        config = toml.load(f)

    id = config["memberID"]
    exposed = ports_map(config["expose"])

    myself = "10.30.%s.0" % id

    o1_create_tables = [
        # The orion inet table handles ipv4 traffic for orion
        # a new table, called "orion6" will be added for inet6 traffic.
        make(
            "add",
            "table",
            {
                "family": "inet",
                "name": "orion",
            },
        ),
        make(
            "flush",
            "table",
            {
                "name": "orion",
                "family": "inet",
            },
        ),
    ]

    # Create the orion chains for handling packets
    o2_create_orion_chains = [
        make_chain("orionForward", "orion", "inet", {}),
        make_chain("orionNatPostRouting", "orion", "inet", {}),
        make_chain("orionNatPreRouting", "orion", "inet", {}),
    ]

    o3_forward_filter = [
        # We accept the traffic if the destination
        # is another orion interface (ex. We are routing to someone)
        make(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "orionForward",
                "expr": [
                    NFT_ORION_OINT_GROUP,
                    NFT_ACCEPT,
                ],
            },
        ),
        # We accept the already established and related traffic
        make(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "orionForward",
                "expr": [
                    make_expr(
                        "in",
                        {
                            "ct": {
                                "key": "state",
                            },
                        },
                        ["established", "related"],
                    ),
                    NFT_ACCEPT,
                ],
            },
        ),
        # We accept the traffic that was dst-nat'ed
        make(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "orionForward",
                "expr": [
                    make_expr(
                        "in",
                        {
                            "ct": {
                                "key": "status",
                            }
                        },
                        "dnat",
                    ),
                    NFT_ACCEPT,
                ],
            },
        ),
        # We reject the forwards by default
        make(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "orionForward",
                "expr": [
                    NFT_ORION_IINT_GROUP,
                    NFT_REJECT,
                ],
            },
        ),
    ]

    o4_exposed_rules = []

    for exp in exposed:
        expr = [
            # 1. Vérification de l'adresse de destination
            make_expr(
                "==",
                {"payload": {"protocol": "ip", "field": "daddr"}},
                exp["address"],
            ),
        ] + []
        
        # if the protocol is not "any" we match the protocol
        if exp["protocol"] not in ["any"]:
            expr.append(
                make_expr(
                    "==",
                    {
                        "meta": {
                            "key": "l4proto",
                        },
                    },
                    exp["protocol"],
                )
            )
        
        # if the protocol is "udp" or "tcp" we use ports
        if exp["protocol"] in ["tcp", "udp"]:
            expr.append(
                make_expr(
                    "==",
                    {
                        "meta": {
                            "key": "l4proto",
                        },
                    },
                    exp["protocol"],
                )
            )
            expr.append(
                make_expr(
                    "==",
                    {
                        "payload": {
                            "protocol": exp["protocol"],
                            "field": "dport",
                        },
                    },
                    exp["port"],
                )
            )
            
            # for udp or tcp we use a custom dnat rule to redirect ports
            expr.append(
                {
                    "dnat": {
                        "addr": exp["redirectAddress"],
                        "family": "ip",
                        "port": exp["redirectPort"],
                    },
                }
            )
        else:
            # else, we simply redirect the traffic
            expr.append(
                {
                    "dnat": {
                        "addr": exp["redirectAddress"],
                        "family": "ip",
                    },
                }
            )

        rule = make(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "orionNatPreRouting",
                "expr": expr,
            },
        )

        o4_exposed_rules.append(rule)
    
    snatSet = {}
    for exo in exposed:
        snatSet[(exo["address"], exo["redirectAddress"])] = {
            "address": exo["address"],
            "redirectAddress": exo["redirectAddress"],
        }
    sorted = snatSet.values()
    o5_sourcenat = [
        make(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "orionNatPostRouting",
                "expr": [
                    make_expr(
                        "!=",
                        {
                            "payload": {
                                "protocol": "ip",
                                "field": "saddr",
                            },
                        },
                        NFT_ORION_PREFIX,
                    ),
                    make_expr(
                        "==",
                        {
                            "payload": {
                                "protocol": "ip",
                                "field": "daddr",
                            },
                        },
                        exo["redirectAddress"],
                    ),
                    {
                        "snat": {
                            "addr": myself,
                        }
                    },
                ],
            },
        )
        for exo in sorted
    ] + [
        make(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "orionNatPostRouting",
                "expr": [
                    make_expr(
                        "==",
                        {
                            "payload": {
                                "protocol": "ip",
                                "field": "saddr",
                            },
                        },
                        exo["redirectAddress"],
                    ),
                    make_expr(
                        "==",
                        {
                            "payload": {
                                "protocol": "ip",
                                "field": "daddr",
                            },
                        },
                        NFT_ORION_PREFIX,
                    ),
                    {
                        "snat": {
                            "addr": exo["address"],
                        }
                    },
                ],
            },
        )
        for exo in sorted
    ] + [
        make(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "orionNatPostRouting",
                "expr": [
                    make_expr(
                        "!=",
                        {
                            "payload": {
                                "protocol": "ip",
                                "field": "saddr",
                            },
                        },
                        NFT_ORION_PREFIX,
                    ),
                    make_expr(
                        "==",
                        {
                            "payload": {
                                "protocol": "ip",
                                "field": "daddr",
                            },
                        },
                        NFT_ORION_PREFIX,
                    ),
                    {
                        "snat": {
                            "addr": myself,
                        }
                    },
                ],
            },
        ),
    ]

    o6_hooks = [  # We add all chain that hook into the packets
        make_chain(
            "postrouting",
            "orion",
            "inet",
            "nat",
            {
                "hook": "postrouting",
                "prio": 99,
            },
        ),
        make_chain(
            "output",
            "orion",
            "inet",
            "nat",
            {
                "hook": "output",
                "prio": -199,
            },
        ),
        make_chain(
            "forward",
            "orion",
            "inet",
            "filter",
            {
                "hook": "forward",
                "prio": -1,
            },
        ),
        make_chain(
            "prerouting",
            "orion",
            "inet",
            "nat",
            {
                "hook": "prerouting",
                "prio": -101,
            },
        ),
    ]

    o7_hooks_jump = [
        make(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "prerouting",
                "expr": [{"goto": {"target": "orionNatPreRouting"}}],
            },
        ),
        make(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "postrouting",
                "expr": [{"goto": {"target": "orionNatPostRouting"}}],
            },
        ),
        make(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "output",
                "expr": [{"goto": {"target": "orionNatPreRouting"}}],
            },
        ),
        make(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "forward",
                "expr": [{"goto": {"target": "orionForward"}}],
            },
        ),
    ]

    ops = (
        o1_create_tables
        + o2_create_orion_chains
        + o3_forward_filter
        + o4_exposed_rules
        + o5_sourcenat
        + o6_hooks
        + o7_hooks_jump
    )

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


if __name__ == "__main__":
    main()
