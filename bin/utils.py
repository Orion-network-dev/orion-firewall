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
NFT_ORION_IINT_GROUP = {
    "match": {
        "op": "==",
        "left": {
            "meta": {"key": "iifgroup"},
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

def ports_map(config):
    expositions = []
    
    for exposition in config:
        valid = 'protocol' in exposition \
            and 'address' in exposition \
            and 'redirectAddress' in exposition
        if not valid:
            continue
        
        shouldUsePorts = 'port' in exposition \
            and 'redirectPort' in exposition \
            and exposition['protocol'] in  ['tcp', 'udp']
        
        if shouldUsePorts:       
            ports = [exposition["port"]] \
                if type(exposition["port"]).__name__ != 'list' \
                else exposition["port"]
            
            redirectPort = [exposition["redirectPort"]] \
                if type(exposition["redirectPort"]).__name__ != 'list' \
                else exposition["redirectPort"]
            
            if len(redirectPort) == len(ports):
                for zpublicPort, zredirectPort in zip(ports, redirectPort):
                    expositions.append({
                        'protocol': exposition['protocol'],
                        'port': zpublicPort,
                        'redirectPort': zredirectPort,
                        'address': exposition['address'],
                        'redirectAddress': exposition['redirectAddress']
                    })
            else:
                print("Ignoring port because redirectPort does not match port")
        else:
            expositions.append({
                'protocol': exposition['protocol'],
                'address': exposition['address'],
                'redirectAddress': exposition['redirectAddress']
            })

    return expositions