def make_nft_expression(operation: str, kind: str, object: object):
    """Generates a generic operation for nftables config

    Args:
        operation (str): Operation in the nft expression
        kind (str): kind of object
        object (object): object in the expression

    Returns:
        nft_expression: Final nft expression 
    """
    return {operation: {kind: object}}


def make_nft_create_chain(name, table, family, type, additional={}):
    """Utility to create a chain

    Args:
        name (_type_): Name of the NFT chain
        table (_type_): Name of the table to add a chain
        family (_type_): Address family to use the chain with
        type (_type_): Type of chain
        additional (dict, optional): Additional data to add. Defaults to {}.

    Returns:
        nft_expression: Action to add a chain
    """
    return make_nft_expression(
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


def make_nft_match(operation, lhs, rhs):
    """Generates an expression to match a nft value

    Args:
        operation (str): Type of operation to use for the match
        lhs (any): Data in the lhs
        rhs (any): Data in the rhs

    Returns:
        any: Rule expression that matches the input
    """
    return {
        "match": {
            "op": operation,
            "left": lhs,
            "right": rhs,
        }
    }

