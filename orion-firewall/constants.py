# Expression NFT pour accepter le traffic
NFT_ACCEPT = {
    "accept": None,
}
# Expression NFT pour rejeter le traffic
NFT_REJECT = {
    "reject": {
        "type": "icmp",
        "expr": "port-unreachable",
    },
}

# Expression NFT pour sélectionner le traffic ayant comme cible une interface orion
NFT_ORION_OUPUT_INTERFACE_GROUP = {
    "match": {
        "op": "==",
        "left": {
            "meta": {"key": "oifgroup"},
        },
        "right": 30,
    }
}
# Expression NFT pour sélectionner le traffic ayant comme source une interface orion
NFT_ORION_INPUT_INTERFACE_GROUP = {
    "match": {
        "op": "==",
        "left": {
            "meta": {"key": "iifgroup"},
        },
        "right": 30,
    }
}

# Expression nft pour sélectionner le traffic ayant comme adresse orion
NFT_ORION_PREFIX = {
    "prefix": {
        "addr": "10.30.0.0",
        "len": 16,
    }
}

NFT_DESTINATION_ADDRESS = {
    "payload": {
        "protocol": "ip",
        "field": "daddr",
    },
}
NFT_SOURCE_ADDRESS = {
    "payload": {
        "protocol": "ip",
        "field": "saddr",
    },
}
NFT_L4_PROTO = {
    "meta": {
        "key": "l4proto",
    },
}
