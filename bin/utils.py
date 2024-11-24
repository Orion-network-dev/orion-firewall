NFT_ACCEPT = {"accept": None}
NFT_ORION_OINT_GROUP = {
    "match": {
        "op": "==",
        "left": {
            "meta": {"key": "oifgroup"},
        },
        "right": 30,
    }
}

NFT_REJECT = {"reject": {"type": "icmp", "expr": "port-unreachable"}}
NFT_ORION_PREFIX = {
    "prefix": {
        "addr": "10.30.0.0",
        "len": 16,
    }
}


def make(operation: str, kind: str, object: object):
    """ """
    return {operation: {kind: object}}


def make_chain(name, table, family, type, additional={}):
    return make(
        "add",
        "chain",
        dict(
            {
                "family": family,
                "type": type,
                "name": name,
                "table": table,
            },
            **additional
        ),
    )


def make_expr(op, left, right):
    return {
        "match": {
            "op": op,
            "left": left,
            "right": right,
        }
    }


def resolve_identity():
    return "idk bruh"


def read_config():
    return [
        {
            "protocol": "icmp",  # protocol of the match
            "port": 533,  # port dans le réseau orion
            "address": "10.30.69.1",  # ip dans le réseau orion
            "redirectPort": 53,  # port dans le backend
            "redirectAddress": "1.1.1.1",  # adresse du backend
        }
    ]
