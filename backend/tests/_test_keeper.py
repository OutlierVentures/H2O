import os.path
import time

from web3 import Web3

import squid_py.acl as acl

from squid_py import Ocean_Legacy
import json
from squid_py.utils import convert_to_string
import pathlib

SAMPLE_METADATA_PATH = os.path.join(pathlib.Path.cwd(), 'tests', 'sample_metadata1.json')
assert SAMPLE_METADATA_PATH.exists()
with open(SAMPLE_METADATA_PATH) as f:
    SAMPLE_METADATA = json.load(f)

def get_events(event_filter, max_iterations=100, pause_duration=0.1):
    events = event_filter.get_new_entries()
    i = 0
    while not events and i < max_iterations:
        i += 1
        time.sleep(pause_duration)
        events = event_filter.get_new_entries()

    if not events:
        print('no events found in %s events filter.' % str(event_filter))
    return events


def process_enc_token(event):
    # should get accessId and encryptedAccessToken in the event
    print("token published event: %s" % event)


def test_keeper():
    expire_seconds = 9999999999
    asset_price = 100
    ocean = Ocean_Legacy(keeper_url='http://localhost:8545', config_file='config_local.ini')
    market = ocean.contracts.market
    token = ocean.contracts.token
    auth = ocean.contracts.auth
    aquarius_account = ocean.helper.accounts[0]
    consumer_account = ocean.helper.accounts[1]
    assert market.request_tokens(2000, aquarius_account)
    assert market.request_tokens(2000, consumer_account)

    # 1. Aquarius register an asset
    asset_id = market.register_asset(SAMPLE_METADATA['base']['name'], SAMPLE_METADATA['base']['description'], asset_price, aquarius_account)
    assert market.check_asset(asset_id)
    assert asset_price == market.get_asset_price(asset_id)

    SAMPLE_METADATA['assetId'] = Web3.toHex(asset_id)
    # ocean.metadata.register_asset(json_dict)
    expiry = int(time.time() + expire_seconds)

    pubprivkey = acl.generate_encryption_keys()
    pubkey = pubprivkey.public_key
    req = auth.contract_concise.initiateAccessRequest(asset_id,
                                                      aquarius_account,
                                                      pubkey,
                                                      expiry,
                                                      transact={'from': consumer_account})
    receipt = ocean.helper.get_tx_receipt(req)

    send_event = auth.contract.events.AccessConsentRequested().processReceipt(receipt)
    request_id = send_event[0]['args']['_id']

    assert auth.get_order_status(request_id) == 0 or auth.get_order_status(
        request_id) == 1

    # filter_token_published = ocean.helper.watch_event(auth.contract, 'EncryptedTokenPublished', process_enc_token, 0.5,
    #                                                   fromBlock='latest')

    i = 0
    while (auth.get_order_status(request_id) == 1) is False and i < 100:
        i += 1
        time.sleep(0.1)

    assert auth.get_order_status(request_id) == 1

    token.token_approve(Web3.toChecksumAddress(market.address),
                        asset_price,
                        consumer_account)

    buyer_balance_start = token.get_token_balance(consumer_account)
    seller_balance_start = token.get_token_balance(aquarius_account)
    print('starting buyer balance = ', buyer_balance_start)
    print('starting seller balance = ', seller_balance_start)

    send_payment = market.contract_concise.sendPayment(request_id,
                                                       aquarius_account,
                                                       asset_price,
                                                       expiry,
                                                       transact={'from': consumer_account, 'gas': 400000})
    receipt = ocean.helper.get_tx_receipt(send_payment)
    print('Receipt: %s' % receipt)

    print('buyer balance = ', token.get_token_balance(consumer_account))
    print('seller balance = ', token.get_token_balance(aquarius_account))
    ocean.metadata.retire_asset_metadata(convert_to_string(asset_id))


    # events = get_events(filter_token_published)
    # assert events
    # assert events[0].args['_id'] == request_id
    # on_chain_enc_token = events[0].args["_encryptedAccessToken"]
