from squid_py.config import DEFAULT_GAS_LIMIT
from squid_py.keeper.utils import get_contract_abi_and_address
from squid_py.modules.v0_1.utils import (
    get_condition_contract_data,
    is_condition_fulfilled
    )
from squid_py.service_agreement.service_agreement_template import ServiceAgreementTemplate


def lockPayment(web3, contract_path, account, service_agreement_id,
                service_definition, *args, **kwargs):
    """ Checks if the lockPayment condition has been fulfilled and if not calls
        PaymentConditions.lockPayment smart contract function.

        The account is supposed to have sufficient amount of approved Ocean tokens.
    """
    payment_conditions, contract, abi, payment_condition_definition = get_condition_contract_data(
        web3,
        contract_path,
        service_definition,
        'lockPayment',
    )

    contract_name = service_definition['serviceAgreementContract']['contractName']
    service_agreement_address = get_contract_abi_and_address(web3, contract_path, contract_name)[1]
    if is_condition_fulfilled(web3, contract_path, service_definition[ServiceAgreementTemplate.TEMPLATE_ID_KEY],
                              service_agreement_id, service_agreement_address,
                              payment_conditions.address, abi, 'lockPayment'):
        return

    name_to_parameter = {param['name']: param for param in payment_condition_definition['parameters']}
    asset_id = name_to_parameter['assetId']['value']
    price = name_to_parameter['price']['value']
    transact = {'from': account.address, 'gas': DEFAULT_GAS_LIMIT}

    try:
        if account.password:
            web3.personal.unlockAccount(account.address, account.password)

        tx_hash = payment_conditions.lockPayment(service_agreement_id, asset_id, price, transact=transact)
    except Exception as e:
        print('error: ', e)
        # Asset id is getting manipulated somehow to bytes
        # TODO: NEED TO investigate and fix this.
        raise

    web3.eth.waitForTransactionReceipt(tx_hash)
    receipt = web3.eth.getTransactionReceipt(tx_hash)
    event = contract.events.PaymentLocked().processReceipt(receipt)
    print('payment locked event: ', event)


def releasePayment(web3, contract_path, account, service_agreement_id,
                   service_definition, *args, **kwargs):
    """ Checks if the releasePayment condition has been fulfilled and if not calls
        PaymentConditions.releasePayment smart contract function.
    """
    payment_conditions, contract, abi, payment_condition_definition = get_condition_contract_data(
        web3,
        contract_path,
        service_definition,
        'releasePayment',
    )

    contract_name = service_definition['serviceAgreementContract']['contractName']
    service_agreement_address = get_contract_abi_and_address(web3, contract_path, contract_name)[1]
    if is_condition_fulfilled(web3, contract_path, service_definition[ServiceAgreementTemplate.TEMPLATE_ID_KEY],
                              service_agreement_id, service_agreement_address,
                              payment_conditions.address, abi, 'releasePayment'):
        return

    name_to_parameter = {param['name']: param for param in payment_condition_definition['parameters']}
    asset_id = name_to_parameter['assetId']['value']
    price = name_to_parameter['price']['value']
    transact = {'from': account.address, 'gas': DEFAULT_GAS_LIMIT}
    try:
        if account.password:
            web3.personal.unlockAccount(account.address, account.password)

        tx_hash = payment_conditions.releasePayment(service_agreement_id, asset_id, price, transact=transact)
    except Exception as e:
        print('error: ', e)
        raise

    web3.eth.waitForTransactionReceipt(tx_hash)
    receipt = web3.eth.getTransactionReceipt(tx_hash)
    event = contract.events.PaymentReleased().processReceipt(receipt)
    print('payment released event: ', event)


def refundPayment(web3, contract_path, account, service_agreement_id,
                  service_definition, *args, **kwargs):
    """ Checks if the refundPayment condition has been fulfilled and if not calls
        PaymentConditions.refundPayment smart contract function.
    """
    function_name = 'refundPayment'
    payment_conditions, contract, abi, payment_condition_definition = get_condition_contract_data(
        web3,
        contract_path,
        service_definition,
        function_name,
    )

    contract_name = service_definition['serviceAgreementContract']['contractName']
    service_agreement_address = get_contract_abi_and_address(web3, contract_path, contract_name)[1]
    if is_condition_fulfilled(web3, contract_path, service_definition[ServiceAgreementTemplate.TEMPLATE_ID_KEY],
                              service_agreement_id, service_agreement_address,
                              payment_conditions.address, abi, function_name):
        return

    name_to_parameter = {param['name']: param for param in payment_condition_definition['parameters']}
    asset_id = name_to_parameter['assetId']['value']
    price = name_to_parameter['price']['value']
    transact = {'from': account.address, 'gas': DEFAULT_GAS_LIMIT}
    try:
        if account.password:
            web3.personal.unlockAccount(account.address, account.password)

        tx_hash = payment_conditions.refundPayment(service_agreement_id, asset_id, price, transact=transact)
    except Exception as e:
        print('error: ', e)
        raise

    web3.eth.waitForTransactionReceipt(tx_hash)
    receipt = web3.eth.getTransactionReceipt(tx_hash)
    event = contract.events.PaymentRefund().processReceipt(receipt)
    print('payment refund event: ', event)
