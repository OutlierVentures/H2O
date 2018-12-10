"""
    Test ocean class

"""
import json
import logging
import os
import pathlib
import time

import pytest
from web3 import Web3

from squid_py.ddo import DDO
from squid_py.exceptions import OceanDIDNotFound
from squid_py.ddo.metadata import Metadata
from squid_py.did import did_generate, did_to_id
from squid_py.keeper.utils import get_fingerprint_by_name
from squid_py.service_agreement.utils import build_condition_key
from squid_py.utils.utilities import generate_new_id, generate_prefixed_id
from squid_py.modules.v0_1.accessControl import grantAccess
from squid_py.modules.v0_1.payment import lockPayment, releasePayment
from squid_py.modules.v0_1.serviceAgreement import fulfillAgreement
from squid_py.ocean.asset import Asset
from squid_py.service_agreement.service_agreement import ServiceAgreement
from squid_py.service_agreement.service_factory import ServiceDescriptor
from squid_py.service_agreement.service_types import ServiceTypes
from tests.test_utils import get_publisher_ocean_instance, get_registered_ddo


def print_config(ocean_instance):
    print("Ocean object configuration:".format())
    print("Ocean.config.keeper_path: {}".format(ocean_instance.config.keeper_path))
    print("Ocean.config.keeper_url: {}".format(ocean_instance.config.keeper_url))
    print("Ocean.config.gas_limit: {}".format(ocean_instance.config.gas_limit))
    print("Ocean.config.aquarius_url: {}".format(ocean_instance.config.aquarius_url))


def test_ocean_instance(publisher_ocean_instance):
    print_config(publisher_ocean_instance)
    assert publisher_ocean_instance.keeper.token is not None

    # There is ONE Web3 instance
    assert publisher_ocean_instance.keeper.market.web3 is publisher_ocean_instance.keeper.auth.web3 is publisher_ocean_instance.keeper.token.web3
    assert publisher_ocean_instance._web3 is publisher_ocean_instance.keeper.web3

    print_config(publisher_ocean_instance)


def test_accounts(publisher_ocean_instance):
    for address in publisher_ocean_instance.accounts:
        print(publisher_ocean_instance.accounts[address])

    # These accounts have a positive ETH balance
    for address, account in publisher_ocean_instance.accounts.items():
        assert account.ether_balance >= 0
        assert account.ocean_balance >= 0


def test_token_request(publisher_ocean_instance, consumer_ocean_instance):
    amount = 2000

    pub_ocn = publisher_ocean_instance
    cons_ocn = consumer_ocean_instance
    # Get the current accounts, assign 2

    # Start balances for comparison
    aquarius_start_eth = pub_ocn.main_account.ether_balance
    aquarius_start_ocean = pub_ocn.main_account.ocean_balance

    # Make requests, assert success on request
    rcpt = pub_ocn.main_account.request_tokens(amount)
    pub_ocn._web3.eth.waitForTransactionReceipt(rcpt)
    rcpt = cons_ocn.main_account.request_tokens(amount)
    publisher_ocean_instance._web3.eth.waitForTransactionReceipt(rcpt)

    # Update and print balances
    # Ocean.accounts is a dict address: account
    for address in pub_ocn.accounts:
        print(pub_ocn.accounts[address])
    aquarius_current_eth = pub_ocn.main_account.ether_balance
    aquarius_current_ocean = pub_ocn.main_account.ocean_balance

    # Confirm balance changes
    assert pub_ocn.main_account.get_balance().eth == aquarius_current_eth
    assert pub_ocn.main_account.get_balance().ocn == aquarius_current_ocean
    # assert aquarius_current_eth < aquarius_start_eth
    # assert aquarius_current_ocean == aquarius_start_ocean + amount


def test_search_assets(publisher_ocean_instance):
    pass


def test_register_asset(publisher_ocean_instance):
    logging.debug("".format())
    asset_price = 100
    sample_ddo_path = pathlib.Path.cwd() / 'tests/resources/ddo' / 'ddo_sample2.json'
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)

    ##########################################################
    # Setup account
    ##########################################################
    publisher_acct = publisher_ocean_instance.main_account
    publisher_address = publisher_acct.address

    # ensure Ocean token balance
    if publisher_acct.ocean_balance == 0:
        rcpt = publisher_acct.request_tokens(200)
        publisher_ocean_instance._web3.eth.waitForTransactionReceipt(rcpt)

    # You will need some token to make this transfer!
    assert publisher_acct.ocean_balance > 0

    ##########################################################
    # Create an Asset with valid metadata
    ##########################################################
    asset = Asset.from_ddo_json_file(sample_ddo_path)

    ######################

    # For this test, ensure the asset does not exist in Aquarius
    meta_data_assets = publisher_ocean_instance.metadata_store.list_assets()
    if asset.ddo.did in meta_data_assets:
        publisher_ocean_instance.metadata_store.get_asset_metadata(asset.ddo.did)
        publisher_ocean_instance.metadata_store.retire_asset_metadata(asset.ddo.did)

    ##########################################################
    # Register using high-level interface
    ##########################################################
    service_descriptors = [ServiceDescriptor.access_service_descriptor(asset_price, '/purchaseEndpoint', '/serviceEndpoint', 600, ('0x%s' % generate_new_id()))]
    publisher_ocean_instance.register_asset(asset.metadata, publisher_address, service_descriptors)


def test_resolve_did(publisher_ocean_instance):
    # prep ddo
    metadata = Metadata.get_example()
    publisher = publisher_ocean_instance.main_account
    original_ddo = publisher_ocean_instance.register_asset(
        metadata, publisher.address,
        [ServiceDescriptor.access_service_descriptor(7, '/dummy/url', '/service/endpoint', 3, ('0x%s' % generate_new_id()))]
    )

    # happy path
    did = original_ddo.did
    ddo = publisher_ocean_instance.resolve_did(did).as_dictionary()
    original = original_ddo.as_dictionary()
    assert ddo['publicKey'] == original['publicKey']
    assert ddo['authentication'] == original['authentication']
    assert ddo['service'][:-1] == original['service'][:-1]
    # assert ddo == original_ddo.as_dictionary(), 'Resolved ddo does not match original.'

    # Can't resolve unregistered asset
    asset_id = generate_new_id()
    unregistered_did = did_generate(asset_id)
    with pytest.raises(OceanDIDNotFound, message='Expected OceanDIDNotFound error.'):
        publisher_ocean_instance.resolve_did(unregistered_did)

    # Raise error on bad did
    asset_id = '0x0123456789'
    invalid_did = did_generate(asset_id)
    with pytest.raises(OceanDIDNotFound, message='Expected a OceanDIDNotFound error when resolving invalid did.'):
        publisher_ocean_instance.resolve_did(invalid_did)


def test_sign_agreement(publisher_ocean_instance, consumer_ocean_instance, registered_ddo):
    # assumptions:
    #  - service agreement template must already be registered
    #  - asset ddo already registered

    consumer = consumer_ocean_instance.main_account.address

    # point consumer_ocean_instance's brizo mock to the publisher's ocean instance
    consumer_ocean_instance._http_client.ocean_instance = publisher_ocean_instance
    # sign agreement using the registered asset did above
    service = registered_ddo.get_service(service_type=ServiceTypes.ASSET_ACCESS)
    assert ServiceAgreement.SERVICE_DEFINITION_ID_KEY in service.as_dictionary()
    sa = ServiceAgreement.from_service_dict(service.as_dictionary())

    service_agreement_id = consumer_ocean_instance.sign_service_agreement(registered_ddo.did, sa.sa_definition_id, consumer)
    print('got new service agreement id:', service_agreement_id)
    filter1 = {'serviceAgreementId': Web3.toBytes(hexstr=service_agreement_id)}
    filter_2 = {'serviceId': Web3.toBytes(hexstr=service_agreement_id)}
    executed = wait_for_event(consumer_ocean_instance.keeper.service_agreement.events.ExecuteAgreement, filter1)
    assert executed
    locked = wait_for_event(consumer_ocean_instance.keeper.payment_conditions.events.PaymentLocked, filter_2)
    assert locked
    granted = wait_for_event(consumer_ocean_instance.keeper.access_conditions.events.AccessGranted, filter_2)
    assert granted
    released = wait_for_event(consumer_ocean_instance.keeper.payment_conditions.events.PaymentReleased, filter_2)
    assert released
    fulfilled = wait_for_event(consumer_ocean_instance.keeper.service_agreement.events.AgreementFulfilled, filter1)
    assert fulfilled
    print('agreement was fulfilled.')


def test_execute_agreement(publisher_ocean_instance, consumer_ocean_instance, registered_ddo):
    """
    This tests execute agreement without going through Ocean's sign agreement / execute agreement
    functions so we can bypass the event handling watchers.
    In this test we invoke all of the conditions directly in the expected order and also check
    for the emitted events to verify that the keeper contracts are working correctly.

    """
    consumer_ocn = consumer_ocean_instance
    keeper = consumer_ocn.keeper
    web3 = keeper.web3
    consumer_acc = consumer_ocn.main_account
    publisher_acc = publisher_ocean_instance.main_account
    service_index = '1'
    did = registered_ddo.did

    # sign agreement
    agreement_id, service_agreement, service_def, ddo = consumer_ocn._get_service_agreement_to_sign(did, service_index)

    consumer_ocn.main_account.unlock()
    signature, sa_hash = service_agreement.get_signed_agreement_hash(
        web3, consumer_ocn.keeper.contract_path, agreement_id, consumer_acc.address
    )
    # Must approve token transfer for this purchase
    consumer_ocn._approve_token_transfer(service_agreement.get_price())

    # execute the agreement
    pub_ocn = publisher_ocean_instance
    asset_id = did_to_id(ddo.did)
    ddo, service_agreement, service_def = pub_ocn._get_ddo_and_service_agreement(ddo.did, service_index)
    pub_ocn.keeper.service_agreement.execute_service_agreement(
        service_agreement.template_id,
        signature,
        consumer_acc.address,
        service_agreement.conditions_params_value_hashes,
        service_agreement.conditions_timeouts,
        agreement_id,
        asset_id,
        pub_ocn.main_account
    )

    filter1 = {'serviceAgreementId': Web3.toBytes(hexstr=agreement_id)}
    filter_2 = {'serviceId': Web3.toBytes(hexstr=agreement_id)}

    # WAIT FOR ####### ExecuteAgreement Event
    executed = wait_for_event(pub_ocn.keeper.service_agreement.events.ExecuteAgreement, filter1)
    assert executed, ''
    cons = keeper.service_agreement.get_service_agreement_consumer(agreement_id)
    pub = keeper.service_agreement.get_service_agreement_publisher(agreement_id)
    assert cons == consumer_acc.address
    assert pub == publisher_acc.address

    cond = service_agreement.conditions[0]
    fn_fingerprint = get_fingerprint_by_name(keeper.payment_conditions.contract.abi, cond.function_name)
    sa_contract = keeper.service_agreement.contract_concise
    pay_cont_address = keeper.payment_conditions.address

    terminated = sa_contract.isAgreementTerminated(agreement_id)
    assert terminated is False
    template_id = web3.toHex(sa_contract.getTemplateId(agreement_id))
    assert template_id == service_agreement.template_id

    k = build_condition_key(web3, pay_cont_address, web3.toBytes(hexstr=fn_fingerprint), service_agreement.template_id)
    cond_key = web3.toHex(sa_contract.getConditionByFingerprint(agreement_id, pay_cont_address, fn_fingerprint))
    assert k == cond_key, 'problem with condition keys: %s vs %s' % (k, cond_key)
    assert cond_key == service_agreement.conditions_keys[0]

    pay_status = sa_contract.getConditionStatus(agreement_id, service_agreement.conditions_keys[0])
    assert pay_status == 0, 'lockPayment condition should be 0 at this point.'
    pay_has_dependencies = sa_contract.hasUnfulfilledDependencies(agreement_id, service_agreement.conditions_keys[0])
    assert pay_has_dependencies is False

    # Lock payment
    lockPayment(web3, keeper.contract_path, consumer_acc, agreement_id, service_def)
    # WAIT FOR ####### PaymentLocked event
    locked = wait_for_event(keeper.payment_conditions.events.PaymentLocked, filter_2)
    # assert locked, ''
    if not locked:
        lock_cond_status = keeper.service_agreement.contract_concise.getConditionStatus(agreement_id, service_agreement.conditions_keys[0])
        assert lock_cond_status > 0
        grant_access_cond_status = keeper.service_agreement.contract_concise.getConditionStatus(agreement_id, service_agreement.conditions_keys[1])
        release_cond_status = keeper.service_agreement.contract_concise.getConditionStatus(agreement_id, service_agreement.conditions_keys[2])
        assert grant_access_cond_status == 0 and release_cond_status == 0, 'grantAccess and/or releasePayment is fulfilled but not expected to.'

    # Grant access
    grantAccess(web3, keeper.contract_path, publisher_acc, agreement_id, service_def)
    # WAIT FOR ####### AccessGranted event
    granted = wait_for_event(keeper.access_conditions.events.AccessGranted, filter_2)
    assert granted, ''
    # Release payment
    releasePayment(web3, keeper.contract_path, publisher_acc, agreement_id, service_def)
    # WAIT FOR ####### PaymentReleased event
    released = wait_for_event(keeper.payment_conditions.events.PaymentReleased, filter_2)
    assert released, ''
    # Fulfill agreement
    fulfillAgreement(web3, keeper.contract_path, publisher_acc, agreement_id, service_def)
    # Wait for ####### AgreementFulfilled event (verify agreement was fulfilled)
    fulfilled = wait_for_event(keeper.service_agreement.events.AgreementFulfilled, filter1)
    assert fulfilled, ''
    print('All good.')
    # Repeat execute test but with a refund payment (i.e. don't grant access)


def test_check_permissions(publisher_ocean_instance, registered_ddo):
    pass


def test_verify_service_agreement_signature(publisher_ocean_instance, registered_ddo):
    pass


def wait_for_event(event, arg_filter, wait_iterations=20):
    _filter = event.createFilter(fromBlock=0 , argument_filters=arg_filter)
    for check in range(wait_iterations):
        events = _filter.get_all_entries()
        if events:
            return events[0]
        time.sleep(0.5)


def test_agreement_hash(publisher_ocean_instance):
    """
    This test verifies generating agreement hash using fixed inputs and ddo example.
    This will make it easier to compare the hash generated from different languages.
    """
    pub_ocn = publisher_ocean_instance

    did = "did:op:0xcb36cf78d87f4ce4a784f17c2a4a694f19f3fbf05b814ac6b0b7197163888865"
    user_address = pub_ocn.keeper.web3.toChecksumAddress("0x00bd138abd70e2f00903268f3db08f2d25677c9e")
    template_id = "0x044852b2a670ade5407e78fb2863c51de9fcb96542a07186fe3aeda6bb8a116d"
    service_agreement_id = '0xf136d6fadecb48fdb2fc1fb420f5a5d1c32d22d9424e47ab9461556e058fefaa'
    print('sid: ', service_agreement_id)
    ddo_file_name = 'shared_ddo_example.json'

    filepath = os.path.join(os.path.sep, *os.path.realpath(__file__).split(os.path.sep)[:-1], 'resources', 'ddo', ddo_file_name)
    ddo = DDO(json_filename=filepath)

    service = ddo.get_service(service_type='Access')
    service = service.as_dictionary()
    sa = ServiceAgreement.from_service_dict(service)
    service[ServiceAgreement.SERVICE_CONDITIONS_KEY] = [cond.as_dictionary() for cond in sa.conditions]
    assert template_id == sa.template_id, ''
    assert did == ddo.did
    agreement_hash = ServiceAgreement.generate_service_agreement_hash(
        pub_ocn.keeper.web3, sa.template_id, sa.conditions_keys,
        sa.conditions_params_value_hashes, sa.conditions_timeouts, service_agreement_id
    )
    print('agreement hash: ', agreement_hash.hex())
    print('expected hash: ', "0x66652d0f8f8ec464e67aa6981c17fa1b1644e57d9cfd39b6f1b58ad1b71d61bb")
    assert agreement_hash.hex() == "0x66652d0f8f8ec464e67aa6981c17fa1b1644e57d9cfd39b6f1b58ad1b71d61bb", 'hash does not match.'
    # signed_hash = pub_ocn.keeper.web3.eth.sign(user_address, agreement_hash).hex()
    # print('signed agreement hash:', signed_hash)


def test_integration(consumer_ocean_instance):
    # this test is disabled for now.
    return
    # This test requires all services running including:
    # secret store
    # parity node
    # aquarius
    # brizo
    # mongodb/bigchaindb

    import requests
    from secret_store_client.client import Client

    pub_ocn = get_publisher_ocean_instance()

    # restore the proper http requests client and secret store client
    pub_ocn._http_client = requests
    pub_ocn._secret_store_client = Client
    consumer_ocean_instance._http_client = requests
    consumer_ocean_instance._secret_store_client = Client

    # Register ddo
    ddo = get_registered_ddo(pub_ocn)
    # did = 'did:op:0x96a49018357a4a1e9f179a3a746af5a087559b4ca133499198428dc4b0868731'
    # ddo = consumer_ocean_instance.resolve_did(did)

    path = os.path.join(consumer_ocean_instance._downloads_path, 'testfiles')
    consumer_ocean_instance._downloads_path = path

    # pub_ocn here will be used only to publish the asset. Handling the asset by the publisher
    # will be performed by the Brizo server running locally

    consumer = consumer_ocean_instance.main_account.address

    # sign agreement using the registered asset did above
    service = ddo.get_service(service_type=ServiceTypes.ASSET_ACCESS)
    assert ServiceAgreement.SERVICE_DEFINITION_ID_KEY in service.as_dictionary()
    sa = ServiceAgreement.from_service_dict(service.as_dictionary())
    # This will send the purchase request to Brizo which in turn will execute the agreement on-chain
    service_agreement_id = consumer_ocean_instance.sign_service_agreement(ddo.did, sa.sa_definition_id, consumer)
    print('got new service agreement id:', service_agreement_id)
    filter1 = {'serviceAgreementId': Web3.toBytes(hexstr=service_agreement_id)}
    filter_2 = {'serviceId': Web3.toBytes(hexstr=service_agreement_id)}

    executed = wait_for_event(consumer_ocean_instance.keeper.service_agreement.events.ExecuteAgreement, filter1)
    assert executed
    granted = wait_for_event(consumer_ocean_instance.keeper.access_conditions.events.AccessGranted, filter_2)
    assert granted
    fulfilled = wait_for_event(consumer_ocean_instance.keeper.service_agreement.events.AgreementFulfilled, filter1)
    assert fulfilled

    path = consumer_ocean_instance._downloads_path
    # check consumed data file in the downloads folder
    assert os.path.exists(path), ''
    folder_names = os.listdir(path)
    assert folder_names, ''
    for name in folder_names:
        asset_path = os.path.join(path, name)
        if os.path.isfile(asset_path):
            continue

        filenames = os.listdir(asset_path)
        assert filenames, 'no files created in this dir'
        assert os.path.isfile(os.path.join(asset_path, filenames[0])), ''

    print('agreement was fulfilled.')
    import shutil
    shutil.rmtree(consumer_ocean_instance._downloads_path)
