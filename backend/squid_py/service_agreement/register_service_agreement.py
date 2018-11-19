from .event_listener import watch_service_agreement_events
from .storage import get_service_agreements, record_service_agreement


def register_service_agreement(web3, contract_path, storage_path, account, service_agreement_id,
                               did, service_definition, actor_type, num_confirmations=12):
    """ Registers the given service agreement in the local storage.
        Subscribes to the service agreement events.
    """

    record_service_agreement(storage_path, service_agreement_id, did)
    watch_service_agreement_events(web3, contract_path, storage_path, account, did,
                                   service_agreement_id, service_definition, actor_type,
                                   num_confirmations)


def execute_pending_service_agreements(web3, contract_path, storage_path, account, actor_type,
                                       did_resolver_fn, num_confirmations=12):
    """ Iterates over pending service agreements recorded in the local storage,
        fetches their service definitions, and subscribes to service agreement events.
    """
    for service_agreement_id, did, _ in get_service_agreements(storage_path):
        ddo = did_resolver_fn(did)
        for service_definition in ddo['service']:
            if service_definition['type'] != 'Access':
                continue

            watch_service_agreement_events(web3, contract_path, storage_path, account,
                                           did, service_agreement_id, service_definition, actor_type,
                                           num_confirmations=num_confirmations)
