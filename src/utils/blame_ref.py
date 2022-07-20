from brownie import chain


def blame_timestamp():
    return f"Message requested at timestamp {chain.time()} and block {chain.height}"
