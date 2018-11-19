from web3.contract import ConciseContract

from squid_py.keeper.utils import (
    get_contract_abi_by_address,
    get_fingerprint_by_name,
    hexstr_to_bytes,
)
from squid_py.modules.v0_1.exceptions import InvalidModule


def is_condition_fulfilled(web3, contract_path, template_id, service_agreement_id,
                           service_agreement_address, condition_address, condition_abi, fn_name):
    service_agreement = _get_concise_contract(web3, contract_path, service_agreement_address)
    status = service_agreement.getConditionStatus(
        service_agreement_id.encode(),
        get_condition_key(
            web3,
            template_id,
            condition_address,
            condition_abi,
            fn_name,
        ),
    )
    return status == 1


def get_condition_key(web3, template_id, address, abi, fn_name):
    return web3.soliditySha3(
        ['bytes32', 'address', 'bytes4'],
        [
            template_id.encode(),
            address,
            hexstr_to_bytes(web3, get_fingerprint_by_name(abi, fn_name)),
        ]
    ).hex()


def get_condition_contract_data(web3, contract_path, service_definition, name):
    condition_definition = None
    for condition in service_definition['conditions']:
        if condition['name'] == name:
            condition_definition = condition
            break

    if condition_definition is None:
        raise InvalidModule('Failed to find the {} condition in the service definition'.format(name))

    address = condition_definition['conditionKey']['contractAddress']
    fingerprint = condition_definition['conditionKey']['fingerprint']

    abi = get_contract_abi_by_address(contract_path, address)
    if get_fingerprint_by_name(abi, name) != fingerprint:
        raise InvalidModule('The {} fingerprint specified in the service definition ' +
                            'does not match the known fingerprint'.format(name))

    return web3.eth.contract(
        address=address,
        abi=abi,
        ContractFactoryClass=ConciseContract,
    ), abi, condition_definition


def _get_concise_contract(web3, contract_path, address):
    abi = get_contract_abi_by_address(contract_path, address)

    return web3.eth.contract(
        address=address,
        abi=abi,
        ContractFactoryClass=ConciseContract,
    )
