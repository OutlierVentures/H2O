from squid_py.ocean_contracts import OceanContracts
from squid_py.consumer import register

ocean = OceanContracts(host='http://localhost', port=8545, config_path='config.ini')

register(publisher_account=ocean.web3.eth.accounts[1],
         provider_account=ocean.web3.eth.accounts[0],
         price=10,
         ocean_contracts_wrapper=ocean,
         json_metadata=json_consume)
