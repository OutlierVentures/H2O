'''
This file gives you access to a nice high-level register function for Ocean Protocol:
simple_register(name, price, description, author, azure_url)
'''

import squid_py.ocean.ocean as ocean
from squid_py.ocean.asset import Asset
from squid_py.service_agreement.service_factory import ServiceDescriptor
from unittest.mock import Mock


def simple_register(name, price, description, author, azure_url):


    # Instantiate Ocean, form metadata object and create asset from it
    ocean_inst = ocean.Ocean('config_local.ini')

    asset_metadata = {
        "base": {
            "name": name,
            "type": "dataset",
            "description": description,
            "size": "3.1gb", # THIS FIELD IS NOW REQUIRED. WILL HAVE TO READ FILE SIZE.
            "author": author,
            "license": "CC-BY",
            "contentType": "text/json",
            "contentUrls": [azure_url] # contentUrls is an array
        }
    }

    asset = Asset.create_from_metadata(asset_metadata, "http://localhost:5000/api/v1/provider/assets/metadata/")


    # Set up accounts
    publisher_address = list(ocean_inst.accounts)[0]
    consumer_address = list(ocean_inst.accounts)[1]
    publisher_acct = ocean_inst.accounts[publisher_address]
    consumer_acct = ocean_inst.accounts[consumer_address]

    # Ensure accounts have sufficient Ocean tokens
    if publisher_acct.ocean_balance == 0:
        rcpt = publisher_acct.request_tokens(200)
        ocean_inst._web3.eth.waitForTransactionReceipt(rcpt)
    if consumer_acct.ocean_balance == 0:
        rcpt = consumer_acct.request_tokens(200)
        ocean_inst._web3.eth.waitForTransactionReceipt(rcpt)

    # Tokens are required for the transfer
    assert publisher_acct.ocean_balance > 0
    assert consumer_acct.ocean_balance > 0


    # Register on blockchain (Keeper)
    ocean_inst.keeper.market.register_asset(asset, price, publisher_acct.address)

    # Assert asset exists and price is correct
    chain_asset_exists = ocean_inst.keeper.market.check_asset(asset.asset_id)
    assert chain_asset_exists
    chain_asset_price = ocean_inst.keeper.market.get_asset_price(asset.asset_id)
    assert price == chain_asset_price


    # Check asset is not already be registered in Aquarius
    meta_data_assets = ocean_inst.metadata_store.list_assets()
    
    if asset.ddo.did in meta_data_assets:
        print('yer')
        ocean_inst.metadata_store.get_asset_metadata(asset.ddo.did)
        ocean_inst.metadata_store.retire_asset_metadata(asset.ddo.did)


    # Register asset in Aquarius
    service_descriptors = [ServiceDescriptor.access_service_descriptor(price, '/purchaseEndpoint', '/serviceEndpoint', 600)]
    ocean.Client = Mock({'publish_document': '!encrypted_message!'})
    ocean_inst.register_asset(asset.metadata, publisher_address, service_descriptors)


    # Escaped characters are just for coloured prints
    print('\033[0;32mAsset published:')
    print(asset.metadata['base']['name'] + '\033[0m')



if __name__ == "__main__":
    simple_register()
