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
