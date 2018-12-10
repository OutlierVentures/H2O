import os
import pytest
from web3 import Web3

from squid_py.ddo.metadata import Metadata
from squid_py.ocean.account import Account
from squid_py.service_agreement.service_agreement_template import ServiceAgreementTemplate
from squid_py.service_agreement.service_factory import ServiceDescriptor
from squid_py.service_agreement.utils import register_service_agreement_template, get_sla_template_path
from squid_py.utils import utilities
from squid_py.ocean.ocean import Ocean
from tests.brizo_mock import BrizoMock
from tests.secret_store_mock import SecretStoreClientMock
from squid_py.utils.utilities import get_purchase_endpoint, get_service_endpoint

PUBLISHER_INDEX = 1
CONSUMER_INDEX = 0


def test_split_signature():
    signature = b'\x19\x15!\xecwnX1o/\xdeho\x9a9\xdd9^\xbb\x8c2z\x88!\x95\xdc=\xe6\xafc\x0f\xe9\x14\x12\xc6\xde\x0b\n\xa6\x11\xc0\x1cvv\x9f\x99O8\x15\xf6f\xe7\xab\xea\x982Ds\x0bX\xd9\x94\xa42\x01'
    split_signature = utilities.split_signature(Web3, signature=signature)
    assert split_signature.v == 28
    assert split_signature.r == b'\x19\x15!\xecwnX1o/\xdeho\x9a9\xdd9^\xbb\x8c2z\x88!\x95\xdc=\xe6\xafc\x0f\xe9'
    assert split_signature.s == b'\x14\x12\xc6\xde\x0b\n\xa6\x11\xc0\x1cvv\x9f\x99O8\x15\xf6f\xe7\xab\xea\x982Ds\x0bX\xd9\x94\xa42'


def test_get_publickey_from_address(publisher_ocean_instance):
    from eth_keys.exceptions import BadSignature
    for account in publisher_ocean_instance.accounts:
        try:
            pub_key = utilities.get_publickey_from_address(publisher_ocean_instance._web3, account)
            assert pub_key.to_checksum_address() == account, 'recovered public key address does not match original address.'
        except BadSignature:
            pytest.fail("BadSignature")
        except ValueError:
            pass


def test_convert():
    input_text = "my text"
    print("output %s" % utilities.convert_to_string(Web3, utilities.convert_to_bytes(Web3, input_text)))
    assert utilities.convert_to_text(Web3, utilities.convert_to_bytes(Web3, input_text)) == input_text


def init_ocn_tokens(ocn, amount=100):
    ocn.main_account.request_tokens(amount)
    ocn.keeper.token.token_approve(
        ocn.keeper.payment_conditions.address,
        amount,
        ocn.main_account
    )


def make_ocean_instance(secret_store_client, account_index):
    path_config = 'config_local.ini'
    os.environ['CONFIG_FILE'] = path_config
    ocn = Ocean(os.environ['CONFIG_FILE'], secret_store_client=secret_store_client)
    ocn._http_client = BrizoMock(ocn)
    ocn.main_account = Account(ocn.keeper, list(ocn.accounts)[account_index])
    return ocn


def get_publisher_ocean_instance():
    ocn = make_ocean_instance(SecretStoreClientMock, PUBLISHER_INDEX)
    address = None
    if ocn.config.has_option('keeper-contracts', 'parity.address'):
        address = ocn.config.get('keeper-contracts', 'parity.address')
    address = ocn._web3.toChecksumAddress(address) if address else None
    if address and address in ocn.accounts:
        password = ocn.config.get('keeper-contracts', 'parity.password') \
            if ocn.config.has_option('keeper-contracts', 'parity.password') else None
        ocn.set_main_account(address, password)
    init_ocn_tokens(ocn)
    return ocn


def get_consumer_ocean_instance():
    ocn = make_ocean_instance(SecretStoreClientMock, CONSUMER_INDEX)
    address = None
    if ocn.config.has_option('keeper-contracts', 'parity.address1'):
        address = ocn.config.get('keeper-contracts', 'parity.address1')

    address = ocn._web3.toChecksumAddress(address) if address else None
    if address and address in ocn.accounts:
        password = ocn.config.get('keeper-contracts', 'parity.password1') \
            if ocn.config.has_option('keeper-contracts', 'parity.password1') else None
        ocn.set_main_account(address, password)
    init_ocn_tokens(ocn)
    return ocn


def get_registered_ddo(ocean_instance):
    # register an AssetAccess service agreement template
    template_id = register_service_agreement_template(
        ocean_instance.keeper.service_agreement, ocean_instance.keeper.contract_path,
        ocean_instance.main_account, ServiceAgreementTemplate.from_json_file(get_sla_template_path()),
        ocean_instance.keeper.network_name
    )

    config = ocean_instance.config
    purchase_endpoint = get_purchase_endpoint(config)
    service_endpoint = get_service_endpoint(config)
    ddo = ocean_instance.register_asset(
        Metadata.get_example(), ocean_instance.main_account.address,
        [ServiceDescriptor.access_service_descriptor(7, purchase_endpoint, service_endpoint, 360, template_id)]
    )

    return ddo


