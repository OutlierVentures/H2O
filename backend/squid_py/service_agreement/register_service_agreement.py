from datetime import datetime

from .event_listener import watch_service_agreement_events
from .storage import get_service_agreements, record_service_agreement


def register_service_agreement(web3, contract_path, storage_path, account, service_agreement_id,
                               did, service_definition, actor_type, service_index, price,
                               content_urls, consume_callback=None, num_confirmations=12, start_time=None):
    """ Registers the given service agreement in the local storage.
        Subscribes to the service agreement events.
    """
    if start_time is None:
        start_time = int(datetime.now().timestamp())

    record_service_agreement(storage_path, service_agreement_id, did, service_index, price, content_urls, start_time)
    watch_service_agreement_events(
        web3, contract_path, storage_path, account, did,
        service_agreement_id, service_definition, actor_type,
        start_time, consume_callback,
        num_confirmations
    )


def execute_pending_service_agreements(web3, contract_path, storage_path, account, actor_type,
                                       did_resolver_fn, num_confirmations=12):
    """ Iterates over pending service agreements recorded in the local storage,
        fetches their service definitions, and subscribes to service agreement events.
    """
    # service_agreement_id, did, service_index, price, content_urls, start_time, status
    for service_agreement_id, did, service_index, price, content_urls, start_time, _ in get_service_agreements(storage_path):
        ddo = did_resolver_fn(did)
        for service_definition in ddo['service']:
            if service_definition['type'] != 'Access':
                continue

            watch_service_agreement_events(web3, contract_path, storage_path, account, did,
                                           service_agreement_id, service_definition, actor_type,
                                           start_time, num_confirmations=num_confirmations)
