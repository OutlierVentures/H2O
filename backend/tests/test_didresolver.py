import logging
import math
import pytest
import secrets

from web3 import (
    Web3,
)

from eth_abi import (
    decode_single,
)

from squid_py.ddo import DDO
from squid_py.did import id_to_did

from squid_py.ocean.ocean import Ocean

from squid_py.didresolver import (
    DIDResolver,
    DIDResolved,
    VALUE_TYPE_DID,
    VALUE_TYPE_DID_REF,
    VALUE_TYPE_URL,
    VALUE_TYPE_DDO,
)

from squid_py.exceptions import (
    OceanDIDCircularReference,
    OceanDIDNotFound,
)

logger = logging.getLogger()

"""
def test_did_resolver_raw_test():

    # test basic didregistry , contract loading and register a DID
    ocean = Ocean(config_file='config_local.ini')
    didregistry = ocean.keeper.didregistry
    register_account = list(ocean.accounts)[1]
    did_test = 'did:op:' + secrets.token_hex(32)
    did_hash = Web3.sha3(text=did_test)
    value_type = VALUE_TYPE_URL
    key_test = Web3.sha3(text='provider')
    key_test = did_hash
    value_test = 'http://localhost:5000'
    register_did = didregistry.register_attribute(did_hash, value_type, key_test, value_test, register_account)
    receipt = didregistry.get_tx_receipt(register_did)

    block_number = didregistry.get_update_at(did_hash)
    assert block_number > 0

    event_signature = didregistry.get_event_signature('DIDAttributeRegistered')
    assert event_signature

    actual_signature = Web3.toHex(receipt['logs'][0]['topics'][0])
    # print('Actual Signature', actual_signature)
    # print('event ABI', event_signature)

    calc_signature = Web3.sha3(text="DIDAttributeRegistered(bytes32,address,bytes32,string,uint8,uint256)").hex()
    # print('Calc signature', Web3.toHex(calc_signature))

    assert actual_signature == calc_signature
    assert actual_signature == event_signature

    # TODO: fix sync with keeper-contracts
    # at the moment assign the calc signature, since the loadad ABI sig is incorret

    event_signature = calc_signature

    # transaction_count = ocean._web3.eth.getBlockTransactionCount(block_number)
    # for index in range(0, transaction_count):
        # transaction = ocean._web3.eth.getTransactionByBlock(block_number, index)
        # print('transaction', transaction)
        # receipt = ocean._web3.eth.getTransactionReceipt(transaction['hash'])
        # print('receipt', receipt)

    # because createFilter does not return any log events
    test_filter = ocean._web3.eth.filter({'fromBlock': block_number, 'topics': [event_signature, Web3.toHex(did_hash)]})
    log_items = test_filter.get_all_entries()
    assert log_items

    assert len(log_items) > 0
    log_item = log_items[len(log_items) - 1]
    decode_value, decode_value_type, decode_block_number = decode_single('(string,uint8,uint256)', Web3.toBytes(hexstr=log_item['data']))
    assert decode_value_type == value_type
    assert decode_value.decode('utf8') == value_test
    assert decode_block_number == block_number
"""


def test_did_resitry_register(publisher_ocean_instance):
    ocean = publisher_ocean_instance

    register_account = ocean.main_account
    owner_address = register_account.address
    didregistry = ocean.keeper.didregistry
    did_id = secrets.token_hex(32)
    did_test = 'did:op:' + did_id
    key_test = Web3.sha3(text='provider')
    value_test = 'http://localhost:5000'

    # register DID-> URL
    didregistry.register(did_test, url=value_test, key=key_test, account=register_account)

    # register DID-> DDO Object
    ddo = DDO(did_test)
    ddo.add_signature()
    ddo.add_service('metadata-test', value_test)

    didregistry.register(did_test, ddo=ddo, key=key_test, account=register_account)

    # register DID-> DDO json
    didregistry.register(did_test, ddo=ddo.as_text(), account=register_account)

    # register DID-> DID string
    did_id_new = secrets.token_hex(32)
    did_test_new = 'did:op:' + did_id_new
    didregistry.register(did_test, did=did_test_new, account=register_account)

    # register DID-> DID bytes
    didregistry.register(did_test, did=Web3.toBytes(hexstr=did_id_new), account=register_account)

    # test circular ref
    with pytest.raises(OceanDIDCircularReference):
        didregistry.register(did_test, did=did_test, account=register_account)

    # No account provided
    with pytest.raises(ValueError):
        didregistry.register(did_test, url=value_test)

    # Invalide key field provided
    with pytest.raises(ValueError):
        didregistry.register(did_test, url=value_test, account=register_account, key=42)


def test_did_resolver_library(publisher_ocean_instance):
    ocean = publisher_ocean_instance
    register_account = ocean.main_account
    owner_address = register_account.address
    didregistry = ocean.keeper.didregistry
    did_id = secrets.token_hex(32)
    did_test = 'did:op:' + did_id
    value_type = VALUE_TYPE_URL
    key_test = Web3.sha3(text='provider')
    value_test = 'http://localhost:5000'
    key_zero = Web3.toBytes(hexstr='0x' + ('00' * 32))

    didresolver = DIDResolver(ocean._web3, ocean.keeper.didregistry)

    # resolve URL from a direct DID ID value
    did_id_bytes = Web3.toBytes(hexstr=did_id)

    didregistry.register(did_test, url=value_test, account=register_account)

    didresolved = didresolver.resolve(did_test)
    assert didresolved
    assert didresolved.is_url
    assert didresolved.url == value_test
    assert didresolved.key == key_zero
    assert didresolved.owner == owner_address

    with pytest.raises(ValueError):
        didresolver.resolve(did_id)

    didresolved = didresolver.resolve(did_id_bytes)
    assert didresolved
    assert didresolved.is_url
    assert didresolved.url == value_test
    assert didresolved.key == key_zero
    assert didresolved.owner == owner_address

    # resolve URL from a hash of a DID string
    did_hash = Web3.sha3(text=did_test)

    register_account.unlock()
    register_did = didregistry.register_attribute(did_hash, value_type, key_test, value_test, owner_address)
    receipt = didregistry.get_tx_receipt(register_did)
    gas_used_url = receipt['gasUsed']
    didresolved = didresolver.resolve(did_hash)
    assert didresolved
    assert didresolved.is_url
    assert didresolved.url == value_test
    assert didresolved.key == key_test
    assert didresolved.value_type == value_type
    assert didresolved.owner == owner_address
    assert didresolved.block_number == receipt['blockNumber']

    # test update of an already assigned DID
    value_test_new = 'http://aquarius:5000'
    register_account.unlock()
    register_did = didregistry.register_attribute(did_hash, value_type, key_test, value_test_new, owner_address)
    receipt = didregistry.get_tx_receipt(register_did)
    didresolved = didresolver.resolve(did_hash)
    assert didresolved
    assert didresolved.is_url
    assert didresolved.url == value_test_new
    assert didresolved.key == key_test
    assert didresolved.value_type == value_type
    assert didresolved.owner == owner_address
    assert didresolved.block_number == receipt['blockNumber']

    # resolve DDO from a direct DID ID value
    ddo = DDO(did_test)
    ddo.add_signature()
    ddo.add_service('meta-store', value_test)
    did_id = secrets.token_hex(32)
    did_id_bytes = Web3.toBytes(hexstr=did_id)
    value_type = VALUE_TYPE_DDO

    register_account.unlock()
    register_did = didregistry.register_attribute(did_id_bytes, value_type, key_test, ddo.as_text(), owner_address)
    receipt = didregistry.get_tx_receipt(register_did)
    gas_used_ddo = receipt['gasUsed']

    didresolved = didresolver.resolve(did_id_bytes)
    resolved_ddo = DDO(json_text = didresolved.ddo)

    assert didresolved
    assert didresolved.is_ddo
    assert ddo.calculate_hash() == resolved_ddo.calculate_hash()
    assert didresolved.key == key_test
    assert didresolved.value_type == value_type
    assert didresolved.owner == owner_address
    assert didresolved.block_number == receipt['blockNumber']

    logger.info('gas used URL: %d, DDO: %d, DDO +%d extra', gas_used_url, gas_used_ddo, gas_used_ddo - gas_used_url)

    value_type = VALUE_TYPE_URL
    # resolve chain of direct DID IDS to URL
    chain_length = 4
    ids = []
    for i in range(0, chain_length):
        ids.append(secrets.token_hex(32))

    for i in range(0, chain_length):
        did_id_bytes = Web3.toBytes(hexstr=ids[i])
        register_account.unlock()
        if i < len(ids) - 1:
            next_did_id = Web3.toHex(hexstr=ids[i + 1])
            logger.debug('add chain {0} -> {1}'.format(Web3.toHex(did_id_bytes), next_did_id))
            register_did = didregistry.register_attribute(did_id_bytes, VALUE_TYPE_DID, key_test, next_did_id,
                                                          owner_address)
        else:
            logger.debug('end chain {0} -> URL'.format(Web3.toHex(did_id_bytes)))
            register_did = didregistry.register_attribute(did_id_bytes, VALUE_TYPE_URL, key_test, value_test,
                                                          owner_address)
        receipt = didregistry.get_tx_receipt(register_did)

    did_id_bytes = Web3.toBytes(hexstr=ids[0])
    didresolved = didresolver.resolve(did_id_bytes)
    assert didresolved
    assert didresolved.is_url
    assert didresolved.url == value_test
    assert didresolved.hop_count == chain_length
    assert didresolved.key == key_test
    assert didresolved.value_type == value_type
    assert didresolved.owner == owner_address
    assert didresolved.block_number == receipt['blockNumber']

    # test circular chain

    # get the did at the end of the chain
    did_id_bytes = Web3.toBytes(hexstr=ids[len(ids) - 1])
    # make the next DID at the end of the chain to point to the first DID
    next_did_id = Web3.toHex(hexstr=ids[0])
    register_account.unlock()
    logger.debug('set end chain {0} -> {1}'.format(Web3.toHex(did_id_bytes), next_did_id))
    register_did = didregistry.register_attribute(did_id_bytes, VALUE_TYPE_DID, key_test, next_did_id, owner_address)
    receipt = didregistry.get_tx_receipt(register_did)
    # get the first DID in the chain
    did_id_bytes = Web3.toBytes(hexstr=ids[0])
    with pytest.raises(OceanDIDCircularReference):
        didresolver.resolve(did_id_bytes)

    # test hop count
    hop_count = math.floor(len(ids) / 2)
    didresolved = didresolver.resolve(did_id_bytes, hop_count)
    assert didresolved
    assert didresolved.is_did
    assert didresolved.did == id_to_did(Web3.toHex(hexstr=ids[hop_count]))

    # test DID not found
    did_id = secrets.token_hex(32)
    did_id_bytes = Web3.toBytes(hexstr=did_id)
    with pytest.raises(OceanDIDNotFound):
        didresolver.resolve(did_id_bytes)

    # test value type error on a linked DID
    register_account.unlock()
    register_did = didregistry.register_attribute(did_id_bytes, VALUE_TYPE_DID, key_test, value_test, owner_address)
    receipt = didregistry.get_tx_receipt(register_did)

    # resolve to get the error
    with pytest.raises(TypeError):
        didresolver.resolve(did_id_bytes)

    # test value type error on a linked DID_REF
    register_account.unlock()
    register_did = didregistry.register_attribute(did_id_bytes, VALUE_TYPE_DID_REF, key_test, value_test,
                                                  owner_address)
    receipt = didregistry.get_tx_receipt(register_did)

    # resolve to get the error
    with pytest.raises(TypeError):
        didresolver.resolve(did_id_bytes)
