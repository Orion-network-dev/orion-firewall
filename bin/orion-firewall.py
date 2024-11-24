#!/usr/bin/env python3
import sys
sys.path.append('/usr/lib/orion-firewall')
import nftables
from utils import *
import json

def main():
    nft = nftables.Nftables()
    self_identity = resolve_identity()
    exposed = read_config()
    
    # chains ready to be exposed
    #  orionForward => ready, all rules are in place
    #  orionNatPostRouting => ready, generated all the rules
    #  orionNatPreRouting => ready, generates all the rules

    myself = "10.30.0.0"

    o1_create_tables = [
        # The orion inet table handles ipv4 traffic for orion
        # a new table, called "orion6" will be added for inet6 traffic.
        make("add", "table", {
            "family": "inet",
            "name": "orion",
        }),
        make("flush", "table", {
            "name": "orion",
            "family": "inet",
        }),
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
        make("add", "rule", {
            "family": "inet",
            "table": "orion",
            "chain": "orionForward",
            "expr": [
                NFT_ORION_OINT_GROUP,
                NFT_ACCEPT,
            ],
        }),
        
        # We accept the already established and related traffic
        make("add", "rule", {
            "family": "inet",
            "table": "orion",
            "chain": "orionForward",
            "expr": [
                make_expr("in", {
                    "ct": {
                        "key": "state",
                    },
                }, ["established", "related"]),
                NFT_ACCEPT,
            ]
        }),
        
        # We accept the traffic that was dst-nat'ed
        make("add", "rule", {
            "family": "inet",
            "table": "orion",
            "chain": "orionForward",
            "expr": [
                make_expr("in", {
                    "ct": {
                        "key": "status",
                    }
                },"dnat"),
                NFT_ACCEPT,
            ]
        }),
        
        # We reject the forwards by default
        make("add", "rule", {
            "family": "inet",
            "table": "orion",
            "chain": "orionForward",
            "expr": [
                NFT_REJECT,
            ]
        })
    ]

    o4_exposed_rules = [
        make("add", "rule", {
            "family": "inet",
            "table": "orion",
            "chain": "orionNatPreRouting",
            "expr": [
                # 1. Vérification de l'adresse de destination
                make_expr("==", {
                    "payload": {
                      "protocol": "ip",
                      "field": "daddr"
                    }
                }, exp["address"]),
                # 2. Vérification du protocole L4
                make_expr("==", {
                    "meta": {
                        "key": "l4proto",
                    },
                }, exp["protocol"]),
            ] + ([make_expr("==", {
                "payload": {
                    "protocol": exp["protocol"],
                    "field": "dport",
                },
            }, exp["port"])] if exp["protocol"] in ["tcp", "udp"] else []) + [
                {
                    "dnat": dict({
                        "addr": exp["redirectAddress"],
                        "family": "ip",
                        
                    }, **({ "port": exp["redirectPort"] } if exp["protocol"] in ["tcp", "udp"] else {}))
                }
            ]
        }) for exp in exposed
    ]
    
    o5_sourcenat = [
        make("add", "rule", {
            "family": "inet",
            "table": "orion",
            "chain": "orionNatPostRouting",
            "expr": [
                make_expr("==", {
                    "payload": {
                        "protocol": "ip",
                        "field": "saddr",
                    },
                }, exo["redirectAddress"]),
                make_expr("==", {
                    "payload": {
                        "protocol": "ip",
                        "field": "daddr",
                    },
                }, NFT_ORION_PREFIX),
                make_expr("!=", {
                    "meta": {
                        "key": "iifgroup",
                    },
                }, "30"),
                {
                    "snat": {
                        "addr": myself,
                    }
                }
            ]
        }) for exo in exposed
    ] + [
        make("add", "rule", {
            "family": "inet",
            "table": "orion",
            "chain": "orionNatPostRouting",
            "expr": [
                make_expr("!=", {
                    "payload": {
                        "protocol": "ip",
                        "field": "saddr",
                    },
                }, NFT_ORION_PREFIX),
                make_expr("==", {
                    "payload": {
                        "protocol": "ip",
                        "field": "daddr",
                    },
                }, NFT_ORION_PREFIX),
                make_expr("!=", {
                    "meta": {
                        "key": "iifgroup",
                    },
                }, "30"),
                {
                    "snat": {
                        "addr": myself,
                    }
                }
            ]
        }),
    ]
    
    o6_hooks = [ # We add all chain that hook into the packets
        make_chain("postrouting", "orion", "inet", "nat", {
            "hook": "postrouting",
            "prio": 1000,
        }),
        make_chain("output", "orion", "inet", "nat", {
            "hook": "output",
            "prio": 1000,
        }),
        make_chain("forward", "orion", "inet", "filter", {
            "hook": "forward",
            "prio": 1000,
        }),
        make_chain("prerouting", "orion", "inet", "nat", {
            "hook": "prerouting",
            "prio": 1000,
        }),
    ]
    
    o7_hooks_jump = [
        make("add", "rule", {
            "family": "inet",
            "table": "orion",
            "chain": "prerouting",
            "expr": [
                { "goto": { "target": "orionNatPreRouting"}  }
            ]
        }),
        make("add", "rule", {
            "family": "inet",
            "table": "orion",
            "chain": "output",
            "expr": [
                { "goto": { "target": "orionNatPreRouting" } }
            ]
        }),
    ]
    
    ops = o1_create_tables \
        + o2_create_orion_chains \
        + o3_forward_filter \
        + o4_exposed_rules \
        + o5_sourcenat \
        + o6_hooks \
        + o7_hooks_jump


    ruleFile = { "nftables": ops }
    print(json.dumps(ruleFile, indent=1))
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
