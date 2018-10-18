from squid_py.ocean_contracts import OceanContracts
from squid_py.consumer import register

import json

# Will be posted through requests library
test_object = {
    # Required, check full ocean stack for format
    # Will be web3.toHex-ed
    "assetId": "",
}
test_consumable = json.dumps(test_object)

# OceanContracts is the new name for OceanContractsWrapper
ocean = OceanContracts(host = 'http://localhost',
                       port = 8545,
                       config_path = 'config.ini')

# TODO: fill in JSON data as specified in contracts

register(publisher_account = ocean.web3.eth.accounts[1],
         provider_account = ocean.web3.eth.accounts[0],
         price = 10,
         ocean_contracts_wrapper = ocean,
         json_metadata = test_consumable)
