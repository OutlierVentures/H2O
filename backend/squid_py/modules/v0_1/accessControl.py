from squid_py.config import DEFAULT_GAS_LIMIT
from squid_py.keeper.utils import get_contract_abi_and_address
from squid_py.modules.v0_1.utils import (
    get_condition_contract_data,
    is_condition_fulfilled
    )
from squid_py.service_agreement.service_agreement import ServiceAgreement
from squid_py.service_agreement.service_agreement_template import ServiceAgreementTemplate


def grantAccess(web3, contract_path, account, service_agreement_id, service_definition,
                *args, **kwargs):
    """ Checks if grantAccess condition has been fulfilled and if not calls
        AccessConditions.grantAccess smart contract function.
    """
    access_conditions, contract, abi, access_condition_definition = get_condition_contract_data(
        web3,
        contract_path,
        service_definition,
        'grantAccess',
    )
    contract_name = service_definition['serviceAgreementContract']['contractName']
    service_agreement_address = get_contract_abi_and_address(web3, contract_path, contract_name)[1]
    if is_condition_fulfilled(web3, contract_path, service_definition[ServiceAgreementTemplate.TEMPLATE_ID_KEY],
                              service_agreement_id, service_agreement_address,
                              access_conditions.address, abi, 'grantAccess'):
        return

    name_to_parameter = {param['name']: param for param in access_condition_definition['parameters']}
    asset_id = name_to_parameter['assetId']['value']
    document_key_id = name_to_parameter['documentKeyId']['value']
    transact = {'from': account.address, 'gas': DEFAULT_GAS_LIMIT}

    try:
        if account.password:
            web3.personal.unlockAccount(account.address, account.password)

        tx_hash = access_conditions.grantAccess(service_agreement_id, asset_id, document_key_id, transact=transact)
    except Exception as e:
        print('error: ', e)
        raise

    web3.eth.waitForTransactionReceipt(tx_hash)
    receipt = web3.eth.getTransactionReceipt(tx_hash)
    event = contract.events.AccessGranted().processReceipt(receipt)
    print('AccessGranted event: ', event)


def consumeAsset(web3, contract_path, account, service_agreement_id, service_definition,
                 consume_callback, *args, **kwargs):

    if consume_callback:
        result = consume_callback(
            service_agreement_id, service_definition['id'],
            service_definition[ServiceAgreement.SERVICE_DEFINITION_ID_KEY], account
        )
        print('done consuming asset, result: ', result)

    else:
        raise ValueError('Consume asset triggered but the consume callback is not set.')
