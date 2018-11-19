from squid_py.modules.v0_1.utils import (
    get_condition_contract_data,
    is_condition_fulfilled,
)


def grantAccess(web3, contract_path, account, service_agreement_id, service_definition,
                *args, **kwargs):
    """ Checks if grantAccess condition has been fulfilled and if not calls
        AccessConditions.grantAccess smart contract function.
    """
    access_conditions, abi, access_condition_definition = get_condition_contract_data(
        web3,
        contract_path,
        service_definition,
        'grantAccess',
    )

    service_agreement_address = service_definition['serviceAgreementContract']['address']
    if is_condition_fulfilled(web3, contract_path, service_definition['templateId'],
                              service_agreement_id, service_agreement_address,
                              access_conditions.address, abi, 'grantAccess'):
        return

    parameters = access_condition_definition['parameters']
    access_conditions.grantAccess(
        service_agreement_id.encode(),
        parameters['did'].encode(),
        parameters['did'].encode(),
        transact={'from': account},
    )
