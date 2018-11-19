import importlib

from squid_py.keeper.service_agreement import ServiceAgreement
from squid_py.keeper.utils import get_contract_abi_by_address
from squid_py.utils import watch_event

from .storage import record_service_agreement


def watch_service_agreement_events(web3, contract_path, storage_path, account, did,
                                   service_agreement_id, service_definition, actor_type,
                                   num_confirmations=12):
    """ Subscribes to the events defined in the given service definition, targeted
        for the given actor type. Filters events by the given service agreement ID.

        The service definition format is described in OEP-11.
    """

    filters = {ServiceAgreement.SERVICE_AGREEMENT_ID: service_agreement_id.encode()}

    # subscribe cleanup
    def _cleanup(event):
        record_service_agreement(storage_path, service_agreement_id, did, 'fulfilled')

    watch_service_agreement_fulfilled(web3, contract_path, service_agreement_id, service_definition,
                                      _cleanup, num_confirmations=num_confirmations)

    # collect service agreement and condition events
    events = []

    for event in service_definition['serviceAgreementContract']['events']:
        if event['actorType'] != actor_type:
                continue

        events.append((service_definition['serviceAgreementContract']['address'], event))

    for condition in service_definition['conditions']:
        for event in condition['events']:
            if event['actorType'] != actor_type:
                continue
            events.append((condition['conditionKey']['contractAddress'], event))

    # subscribe to the events
    for contract_address, event in events:
        event_handler = event['handler']
        version = event_handler['version'].replace('.', '_')
        import_path = 'squid_py.modules.v{}.{}'.format(version, event_handler['moduleName'])
        module = importlib.import_module(import_path, 'squid_py')
        fn = getattr(module, event_handler['functionName'])

        def _get_callback(fn):
            def _callback(payload):
                fn(web3, contract_path, account, service_agreement_id, service_definition, payload)

            return _callback

        contract_abi = get_contract_abi_by_address(contract_path, contract_address)
        contract = web3.eth.contract(address=contract_address, abi=contract_abi)

        # FIXME change this after AccessConditions contract is fixed
        _filters = filters \
                   if event_handler['functionName'] == 'lockPayment' \
                   else {'serviceId': service_agreement_id.encode()}
        watch_event(
            contract,
            event['name'],
            _get_callback(fn),
            fromBlock='latest',
            interval=0.5,
            filters=_filters,
            num_confirmations=num_confirmations,
        )


def watch_service_agreement_fulfilled(web3, contract_path, service_agreement_id, service_definition,
                                      callback, num_confirmations=12):
    """ Subscribes to the service agreement fulfilled event, filtering by the given
        service agreement ID.
    """
    contract_address = service_definition['serviceAgreementContract']['address']
    contract_abi = get_contract_abi_by_address(contract_path, contract_address)
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)

    filters = {ServiceAgreement.SERVICE_AGREEMENT_ID: service_agreement_id.encode()}
    watch_event(
        contract,
        'AgreementFulfilled',
        callback,
        fromBlock='latest',
        interval=0.5,
        filters=filters,
        num_confirmations=num_confirmations,
    )
