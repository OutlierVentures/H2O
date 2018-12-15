from squid_py.ocean.asset import Asset
import pathlib
from squid_py.service_agreement.service_factory import ServiceDescriptor
from squid_py.utils.utilities import generate_new_id
import logging
from squid_py.ocean.ocean import Ocean

def simple_register(name, price, description, author, azure_url):

    pub_ocn = Ocean('config_local.ini')
    cons_ocn = Ocean('config_local.ini')
    logging.debug("".format())

    # Format metadata as required by Ocean
    metadata = {
        "base": {
            "name": name,
            "type": "dataset",
            "description": description,
            "size": "0.1MB", # Approx
            "author": author,
            "license": "CC-BY",
            "contentType": "text/json",
            "contentUrls": [azure_url] # contentUrls is an array
        }
    }

    aquarius_acct = pub_ocn.main_account
    consumer_acct = cons_ocn.main_account

    # Ensure there are tokens for the contract
    if aquarius_acct.ocean_balance == 0:
        rcpt = aquarius_acct.request_tokens(200)
        pub_ocn._web3.eth.waitForTransactionReceipt(rcpt)
    if consumer_acct.ocean_balance == 0:
        rcpt = consumer_acct.request_tokens(200)
        cons_ocn._web3.eth.waitForTransactionReceipt(rcpt)

    assert aquarius_acct.ocean_balance > 0
    assert consumer_acct.ocean_balance > 0

    # If you are hosting Aquarius somewhere else, use the second parameter here
    asset = Asset.create_from_metadata(metadata, "http://localhost:5000/api/v1/provider/assets/metadata/")

    # Register asset
    pub_ocn.keeper.market.register_asset(asset, price, aquarius_acct.address)


    # These checks work for local deployment

    # Check asset exists
    #chain_asset_exists = pub_ocn.keeper.market.check_asset(asset.asset_id)
    #logging.debug("check_asset = {}".format(chain_asset_exists))
    #assert chain_asset_exists

    # Check price is as specified
    #chain_price = pub_ocn.keeper.market.get_asset_price(asset.asset_id)
    #assert price == chain_price
    #logging.debug("chain_price = {}".format(chain_price))


    print('\033[0;32mAsset published:')
    print(asset.metadata['base']['name'] + '\033[0m')


# For quick testing
if __name__ == "__main__":
    simple_register('test', 10, 'test', 'test', 'test')
