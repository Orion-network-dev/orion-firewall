import utils
import constants
import identity
import socket

local_ips = (
    socket.gethostbyname_ex(socket.gethostname())[2]
    + socket.gethostbyname_ex("localhost")[2]
    + ["0.0.0.0"]
)


def is_self_ip(ip):
    return ip in local_ips


def flatten(config):
    expositions = []

    for exposition in config:
        shouldUsePorts = (
            "port" in exposition
            and "redirectPort" in exposition
            and exposition["protocol"] in ["tcp", "udp"]
        )

        if shouldUsePorts:
            ports = (
                [exposition["port"]]
                if type(exposition["port"]).__name__ != "list"
                else exposition["port"]
            )

            redirectPort = (
                [exposition["redirectPort"]]
                if type(exposition["redirectPort"]).__name__ != "list"
                else exposition["redirectPort"]
            )

            for zpublicPort, zredirectPort in zip(ports, redirectPort):
                expositions.append(
                    {
                        "protocol": exposition["protocol"],
                        "port": zpublicPort,
                        "redirectPort": zredirectPort,
                        "address": exposition["address"],
                        "redirectAddress": exposition["redirectAddress"],
                        "masquerade": exposition["masquerade"],
                    }
                )
        else:
            expositions.append(
                {
                    "protocol": exposition["protocol"],
                    "address": exposition["address"],
                    "redirectAddress": exposition["redirectAddress"],
                    "masquerade": exposition["masquerade"],
                }
            )

    return expositions


def nft(config):
    id = identity.resolve_user_id(config)
    myself = "10.30.%s.0" % id

    flattened = flatten(config["expose"])

    operations = [
        # We add a new table, this is ignored if the table already exists.
        utils.make_nft_expression(
            "add",
            "table",
            {
                "family": "inet",
                "name": "orion",
            },
        ),
        # In case the table already exists, we 'flush' is, meaning erasing all the rules and chains.
        utils.make_nft_expression(
            "flush",
            "table",
            {
                "name": "orion",
                "family": "inet",
            },
        ),
        # Used to do s-nat of outgoing packets.
        utils.make_nft_create_chain("orionNatPostRouting", "orion", "inet", {}),
        # Used to use d-nat routing.
        utils.make_nft_create_chain("orionNatPreRouting", "orion", "inet", {}),
        # Used for input filtering
        utils.make_nft_create_chain("orionInput", "orion", "inet", {}),
    ]

    operations += [
        # Called during the 'forward' action, used to redirect packets.
        utils.make_nft_create_chain("orionForward", "orion", "inet", {}),
        # We accept the traffic if the destination
        # is another orion interface (ex. We are routing to someone)
        utils.make_nft_expression(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "orionForward",
                "expr": [
                    constants.NFT_ORION_OUPUT_INTERFACE_GROUP,
                    constants.NFT_ACCEPT,
                ],
            },
        ),
        # We accept the already established and related traffic
        utils.make_nft_expression(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "orionForward",
                "expr": [
                    utils.make_nft_match(
                        "in",
                        {
                            "ct": {
                                "key": "state",
                            },
                        },
                        ["established", "related"],
                    ),
                    constants.NFT_ACCEPT,
                ],
            },
        ),
        # We accept the traffic that was dst-nat'ed
        utils.make_nft_expression(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "orionForward",
                "expr": [
                    utils.make_nft_match(
                        "in",
                        {
                            "ct": {
                                "key": "status",
                            }
                        },
                        "dnat",
                    ),
                    constants.NFT_ACCEPT,
                ],
            },
        ),
        # We reject the forwards by default
        utils.make_nft_expression(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "orionForward",
                "expr": [
                    constants.NFT_ORION_INPUT_INTERFACE_GROUP,
                    constants.NFT_REJECT,
                ],
            },
        ),
    ]

    for expose in flattened:
        expr = [
            # 1. Vérification de l'adresse de destination
            utils.make_nft_match(
                "==",
                constants.NFT_DESTINATION_ADDRESS,
                expose["address"],
            ),
        ]

        # If we do not have the 'any' protocol
        # we check the l4 protocol that is used
        if expose["protocol"] != "any":
            expr.append(
                utils.make_nft_match(
                    "==",
                    constants.NFT_L4_PROTO,
                    expose["protocol"],
                )
            )

        # if the protocol is "udp" or "tcp" we use ports
        if expose["protocol"] in ["tcp", "udp"]:
            expr += [
                # if the destination port match the one used by the expose
                utils.make_nft_match(
                    "==",
                    {
                        "payload": {
                            "protocol": expose["protocol"],
                            "field": "dport",
                        },
                    },
                    expose["port"],
                )
            ]
            if is_self_ip(expose["redirectAddress"]):
                expr.append(
                    {
                        "redirect": {
                            "port": expose["redirectPort"],
                            "family": "ip",
                        }
                    }
                )
            else:
                expr.append(
                    # for udp or tcp we use a custom dnat rule to redirect ports
                    {
                        "dnat": {
                            "addr": expose["redirectAddress"],
                            "family": "ip",
                            "port": expose["redirectPort"],
                        },
                    }
                )

        else:
            if is_self_ip(expose["redirectAddress"]):
                expr.append(
                    {
                        "redirect": {
                            "family": "ip",
                        },
                    }
                )
            else:
                expr.append(
                    {
                        "dnat": {
                            "addr": expose["redirectAddress"],
                            "family": "ip",
                        },
                    }
                )

        rule = utils.make_nft_expression(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "orionNatPreRouting",
                "expr": expr,
            },
        )

        operations.append(rule)

    snats = {}
    for expose in flattened:
        if not is_self_ip(expose["redirectAddress"]):
            snats[(expose["address"], expose["redirectAddress"])] = {
                "address": expose["address"],
                "redirectAddress": expose["redirectAddress"],
                "masquerade": expose["masquerade"],
            }

    sorted = snats.values()
    for sourcenat in sorted:
        # source-nat the traffic coming from the redirectAddress
        operations.append(
            utils.make_nft_expression(
                "add",
                "rule",
                {
                    "family": "inet",
                    "table": "orion",
                    "chain": "orionNatPostRouting",
                    "expr": [
                        utils.make_nft_match(
                            "==",
                            constants.NFT_SOURCE_ADDRESS,
                            sourcenat["redirectAddress"],
                        ),
                        utils.make_nft_match(
                            "==",
                            constants.NFT_DESTINATION_ADDRESS,
                            constants.NFT_ORION_PREFIX,
                        ),
                        {
                            "snat": {
                                "addr": sourcenat["address"],
                            }
                        },
                    ],
                },
            ),
        )

        if sourcenat["masquerade"]:
            operations.append(
                utils.make_nft_expression(
                    "add",
                    "rule",
                    {
                        "family": "inet",
                        "table": "orion",
                        "chain": "orionNatPostRouting",
                        "expr": [
                            utils.make_nft_match(
                                "==",
                                constants.NFT_DESTINATION_ADDRESS,
                                sourcenat["redirectAddress"],
                            ),
                            {"masquerade": {}},
                        ],
                    },
                )
            )
        else:
            operations.append(
                utils.make_nft_expression(
                    "add",
                    "rule",
                    {
                        "family": "inet",
                        "table": "orion",
                        "chain": "orionNatPostRouting",
                        "expr": [
                            utils.make_nft_match(
                                "!=",
                                constants.NFT_SOURCE_ADDRESS,
                                constants.NFT_ORION_PREFIX,
                            ),
                            utils.make_nft_match(
                                "!=",
                                {
                                    "meta": {"key": "iifgroup"},
                                },
                                30,
                            ),
                            utils.make_nft_match(
                                "==",
                                constants.NFT_DESTINATION_ADDRESS,
                                sourcenat["redirectAddress"],
                            ),
                            {
                                "snat": {
                                    "addr": myself,
                                }
                            },
                        ],
                    },
                ),
            )
    # this is the default sourcenat rule
    operations.append(
        utils.make_nft_expression(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "orionNatPostRouting",
                "expr": [
                    utils.make_nft_match(
                        "!=",
                        constants.NFT_SOURCE_ADDRESS,
                        constants.NFT_ORION_PREFIX,
                    ),
                    utils.make_nft_match(
                        "==",
                        constants.NFT_DESTINATION_ADDRESS,
                        constants.NFT_ORION_PREFIX,
                    ),
                    {
                        "snat": {
                            "addr": myself,
                        }
                    },
                ],
            },
        ),
    )

    operations += [  # We add all chain that hook into the packets
        utils.make_nft_create_chain(
            "postrouting",
            "orion",
            "inet",
            "nat",
            {
                "hook": "postrouting",
                "prio": 99,
            },
        ),
        utils.make_nft_create_chain(
            "output",
            "orion",
            "inet",
            "nat",
            {
                "hook": "output",
                "prio": -199,
            },
        ),
        utils.make_nft_create_chain(
            "forward",
            "orion",
            "inet",
            "filter",
            {
                "hook": "forward",
                "prio": -1,
            },
        ),
        utils.make_nft_create_chain(
            "prerouting",
            "orion",
            "inet",
            "nat",
            {
                "hook": "prerouting",
                "prio": -101,
            },
        ),
        utils.make_nft_create_chain(
            "input",
            "orion",
            "inet",
            "filter",
            {
                "hook": "input",
                "prio": -1,
            },
        ),
        utils.make_nft_expression(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "prerouting",
                "expr": [{"goto": {"target": "orionNatPreRouting"}}],
            },
        ),
        utils.make_nft_expression(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "postrouting",
                "expr": [{"goto": {"target": "orionNatPostRouting"}}],
            },
        ),
        utils.make_nft_expression(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "output",
                "expr": [{"goto": {"target": "orionNatPreRouting"}}],
            },
        ),
        utils.make_nft_expression(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "forward",
                "expr": [{"goto": {"target": "orionForward"}}],
            },
        ),
        utils.make_nft_expression(
            "add",
            "rule",
            {
                "family": "inet",
                "table": "orion",
                "chain": "input",
                "expr": [
                    constants.NFT_ORION_INPUT_INTERFACE_GROUP,
                    {"goto": {"target": "orionInput"}},
                ],
            },
        ),
    ]

    return operations
