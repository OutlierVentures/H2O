import os
import json

from squid_py.ddo.authentication import Authentication
from squid_py.ddo.public_key_hex import PublicKeyHex, PUBLIC_KEY_TYPE_HEX, AUTHENTICATION_TYPE_HEX
from squid_py.keeper.utils import (
    get_fingerprint_by_name,
    get_contract_abi_and_address,
    hexstr_to_bytes,
    get_network_name)
from squid_py.service_agreement.service_agreement_condition import ServiceAgreementCondition
from squid_py.service_agreement.service_agreement_template import ServiceAgreementTemplate
from squid_py.service_agreement.service_types import ServiceTypes
from squid_py.utils.utilities import get_publickey_from_address


def get_sla_template_path(service_type=ServiceTypes.ASSET_ACCESS):
    if service_type == ServiceTypes.ASSET_ACCESS:
        name = 'access_sla_template.json'
    elif service_type == ServiceTypes.CLOUD_COMPUTE:
        name = 'compute_sla_template.json'
    elif service_type == ServiceTypes.FITCHAIN_COMPUTE:
        name = 'fitchain_sla_template.json'
    else:
        raise ValueError('Invalid/unsupported service agreement type "%s"' % service_type)

    return os.path.join(os.path.sep, *os.path.realpath(__file__).split(os.path.sep)[1:-1], name)


def get_sla_template_dict(path):
    with open(path) as template_file:
        return json.load(template_file)


def build_condition_key(web3, contract_address, fingerprint, template_id):
    assert isinstance(fingerprint, bytes), 'Expecting `fingerprint` of type bytes, got %s' % type(fingerprint)
    return web3.soliditySha3(
        ['bytes32', 'address', 'bytes4'],
        [template_id, contract_address, fingerprint]
    ).hex()


def build_conditions_keys(web3, contract_addresses, fingerprints, template_id):
    return [build_condition_key(web3, address, fingerprints[i], template_id)
            for i, address in enumerate(contract_addresses)]


def get_conditions_data_from_keeper_contracts(web3, contract_path, conditions, template_id):
    """Helper function to generate conditions data that is typically used together in a
    service agreement.

    :param web3:
    :param contract_path: str path to contracts artifacts
    :param conditions: list of ServiceAgreementCondition instances
    :param template_id:
    :return:
    """
    _network_name = get_network_name(web3)
    names = {cond.contract_name for cond in conditions}
    name_to_contract_abi_n_address = {
        name: get_contract_abi_and_address(web3, contract_path, name, _network_name)
        for name in names
    }
    contract_addresses = [
        web3.toChecksumAddress(name_to_contract_abi_n_address[cond.contract_name][1])
        for cond in conditions
    ]
    fingerprints = [
        hexstr_to_bytes(web3, get_fingerprint_by_name(
            name_to_contract_abi_n_address[cond.contract_name][0],
            cond.function_name
        ))
        for i, cond in enumerate(conditions)
    ]
    fulfillment_indices = [i for i, cond in enumerate(conditions) if cond.is_terminal]
    conditions_keys = build_conditions_keys(web3, contract_addresses, fingerprints, template_id)
    return contract_addresses, fingerprints, fulfillment_indices, conditions_keys


def register_service_agreement_template(service_agreement_contract, contract_path, owner_account, sla_template_instance=None, sla_template_path=None):
    if sla_template_instance is None:
        if sla_template_path is None:
            raise AssertionError('Invalid arguments, a template instance or a template json path is required.')

        sla_template_instance = ServiceAgreementTemplate.from_json_file(sla_template_path)

    # sla_template_instance.template_id = generate_prefixed_id()
    conditions_data = get_conditions_data_from_keeper_contracts(
        service_agreement_contract.web3, contract_path, sla_template_instance.conditions, sla_template_instance.template_id
    )
    contract_addresses, fingerprints, fulfillment_indices, conditions_keys = conditions_data
    # Fill the conditionKey in each condition in the template
    conditions = sla_template_instance.conditions
    for i in range(len(conditions)):
        conditions[i].condition_key = conditions_keys[i]

    service_agreement_contract.setup_agreement_template(
        sla_template_instance.template_id,
        contract_addresses, fingerprints, sla_template_instance.conditions_dependencies,
        sla_template_instance.description,
        fulfillment_indices, sla_template_instance.service_agreement_contract.fulfillment_operator,
        owner_account
    )
    return sla_template_instance.template_id


def get_conditions_with_updated_keys(web3, contract_path, conditions, template_id):
    """Return a copy of `conditions` with updated conditions keys using the corresponding
    contracts addresses found in `contract_path`.
    Condition keys are used to identify an instance of a condition controller function in a specific
    deployed instance of a solidity contract. The key binds the function to a service agreement
    template id that is registered on-chain.

    :param web3:
    :param contract_path:
    :param conditions:
    :param template_id:
    :return:
    """
    conditions_data = get_conditions_data_from_keeper_contracts(
        web3, contract_path, conditions, template_id
    )
    fingerprints, fulfillment_indices, conditions_keys = conditions_data[1:]
    # Fill the conditionKey in each condition in the template
    _conditions = [ServiceAgreementCondition(cond.as_dictionary()) for cond in conditions]
    for i, cond in enumerate(_conditions):
        cond.condition_key = conditions_keys[i]

    return _conditions


def make_public_key_and_authentication(did, publisher_address, web3):
    """Create a public key and authentication sections to include in a DDO (DID document).
    The public key is derived from the ethereum address by signing an arbitrary message
    then using ec recover to extract the public key.
    Alternatively, the public key can be generated from a private key if provided by the publisher.

    :param did:
    :param publisher_address:
    :param web3:
    :return:
    """
    # set public key
    public_key_value = get_publickey_from_address(web3, publisher_address).to_hex()
    pub_key = PublicKeyHex('keys-1', **{'value': public_key_value, 'owner': publisher_address,
                                         'type': PUBLIC_KEY_TYPE_HEX})
    pub_key.assign_did(did)
    # set authentication
    auth = Authentication(pub_key, AUTHENTICATION_TYPE_HEX)
    return pub_key, auth
