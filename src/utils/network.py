import brownie
from brownie._config import CONFIG

from dotenv import dotenv_values

config = dotenv_values(".env")


def connect_to_rpc(network_name="mainnet"):
    if not brownie.network.is_connected():
        CONFIG.networks[network_name][
            "host"
        ] = f"https://eth-mainnet.alchemyapi.io/v2/{config['ALCHEMY_API_KEY']}"
        CONFIG.networks[network_name]["name"] = "Ethereum mainnet"

        brownie.network.connect(network_name)
