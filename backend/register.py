import requests
from squid_py.ocean_contracts import OceanContracts
from squid_py.consumer import register

json_consume = {
    "publisherId": "0x01",
    "metadata": {
        # User-specified
        "name": "H2O Output",
        "description": "Clustered dataset from OrbitDB data.",
        "contentUrls": ["http://0.0.0.0:4200"], # TODO: Map user string to array
        "price": 10,
        "author": "Outlier Ventures",
        # Fixed
        "type": "dataset",
        "licence": "CC-BY",
        # Internal, used to generate resource ID
        "links": "",
        "size": "",
        "format": ""
    },
    "assetId": "0x01"
}

ocean = OceanContracts(host = 'http://0.0.0.0',
                       port = 8545,
                       config_path = 'config_local.ini')

resource_id = register(publisher_account = ocean.web3.eth.accounts[1],
                       provider_account = ocean.web3.eth.accounts[0],
                       price = 10,
                       ocean_contracts_wrapper = ocean,
                       json_metadata = json_consume,
                       provider_host = 'http://0.0.0.0:5000')

assert requests.get('http://0.0.0.0:5000/api/v1/provider/assets/metadata/%s' % resource_id).status_code == 200
