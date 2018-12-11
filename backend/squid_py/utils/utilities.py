import json
import uuid
import time
from collections import namedtuple
from datetime import datetime
from threading import Thread

from web3 import Web3
from eth_keys import KeyAPI
from eth_utils import big_endian_to_int

from squid_py.service_agreement.service_types import ServiceTypes

Signature = namedtuple('Signature', ('v', 'r', 's'))


def prepare_purchase_payload(did, agreement_id, service_index, signature, consumer_address):
    # Prepare a payload to send to `Brizo`
    return json.dumps({
        'did': did,
        'serviceAgreementId': agreement_id,
        'serviceDefinitionId': service_index,
        'signature': signature,
        'consumerAddress': consumer_address
    })


def get_brizo_url(config):
    brizo_url = 'http://localhost:8030'
    if config.has_option('resources', 'brizo.url'):
        brizo_url = config.get('resources', 'brizo.url') or brizo_url

    brizo_path = '/api/v1/brizo'
    return '{}{}'.format(brizo_url, brizo_path)


def get_purchase_endpoint(config):
    return '{}/services/access/initialize'.format(get_brizo_url(config))


def get_service_endpoint(config):
    service_endpoint = '{}/services/consume'.format(get_brizo_url(config))
    return service_endpoint


def get_metadata_url(ddo):
    metadata_service = ddo.get_service(service_type=ServiceTypes.METADATA)
    url = metadata_service.get_values()['metadata']['base']['contentUrls']
    return url if isinstance(url, str) else url[0]


def prepare_prefixed_hash(msg_hash):
    prefixed_hash = Web3.soliditySha3(['string', 'bytes32'], ["\x19Ethereum Signed Message:\n32", msg_hash])
    return prefixed_hash


def get_publickey_from_address(web3, address):
    _hash = Web3.sha3(text='verify signature.')
    signature = split_signature(web3, web3.eth.sign(address, _hash))
    signature_vrs = Signature(signature.v % 27,
                              big_endian_to_int(signature.r),
                              big_endian_to_int(signature.s))
    prefixed_hash = prepare_prefixed_hash(_hash)
    pub_key = KeyAPI.PublicKey.recover_from_msg_hash(prefixed_hash, KeyAPI.Signature(vrs=signature_vrs))
    assert pub_key.to_checksum_address() == address, 'recovered address does not match signing address.'
    return pub_key


def generate_new_id():
    return uuid.uuid4().hex + uuid.uuid4().hex


def generate_prefixed_id():
    return '0x%s' % generate_new_id()


def get_id_from_did(did):
    return convert_to_bytes(Web3, did.split(':')[-1])


def to_32byte_hex(web3, val):
    return web3.toBytes(val).rjust(32, b'\0')


def convert_to_bytes(web3, data):
    return web3.toBytes(text=data)


def convert_to_string(web3, data):
    return web3.toHex(data)


def convert_to_text(web3, data):
    return web3.toText(data)


def split_signature(web3, signature):
    assert len(signature) == 65, 'invalid signature, expecting bytes of length 65, got %s' % len(signature)
    v = web3.toInt(signature[-1])
    r = to_32byte_hex(web3, int.from_bytes(signature[:32], 'big'))
    s = to_32byte_hex(web3, int.from_bytes(signature[32:64], 'big'))
    if v != 27 and v != 28:
        v = 27 + v % 2

    return Signature(v, r, s)


def watch_event(contract_name, event_name, callback, interval,
                start_time, timeout=None, timeout_callback=None,
                fromBlock=0, toBlock='latest',
                filters=None, num_confirmations=12):

    event_filter = install_filter(
        contract_name, event_name, fromBlock, toBlock, filters
    )
    event_filter.poll_interval = interval
    Thread(
        target=watcher,
        args=(event_filter, callback, start_time, timeout, timeout_callback),
        kwargs={'num_confirmations': num_confirmations},
        daemon=True,
    ).start()
    return event_filter


def install_filter(contract, event_name, fromBlock=0, toBlock='latest', filters=None):
    # contract_instance = self.contracts[contract_name][1]
    event = getattr(contract.events, event_name)
    event_filter = event().createFilter(
        fromBlock=fromBlock, toBlock=toBlock, argument_filters=filters
    )
    return event_filter


def watcher(event_filter, callback, start_time, timeout, timeout_callback, num_confirmations=12):
    timed_out = False
    while True:
        try:
            events = event_filter.get_new_entries()
        except ValueError as err:
            # ignore error, but log it
            print('Got error grabbing keeper events: ', str(err))
            events = []

        processed = False
        for event in events:
            if num_confirmations > 0:
                Thread(
                    target=await_confirmations,
                    args=(
                        event_filter,
                        event['blockNumber'],
                        event['blockHash'].hex(),
                        num_confirmations,
                        callback,
                        event,
                    ),
                    daemon=True,
                ).start()
            else:
                callback(event)
            processed = True

        if processed:
            break

        # always take a rest
        time.sleep(0.1)
        if timeout_callback:
            now = int(datetime.now().timestamp())
            if (start_time + timeout) < now:
                # timeout exceeded, break out of this loop and trigger the timeout callback
                timed_out = True
                break

    if timed_out and timeout_callback:
        timeout_callback((start_time, timeout, int(datetime.now().timestamp())))


def await_confirmations(event_filter, block_number, block_hash, num_confirmations, callback, event):
    while True:
        latest_block = event_filter.web3.eth.getBlock('latest')

        if latest_block['number'] >= block_number + num_confirmations:
            block = event_filter.web3.eth.getBlock(block_number)
            if block['hash'].hex() == block_hash:
                callback(event)

            # if hashes do not match, it means the event did not end up in the longest chain
            # after the given number of confirmations
            #
            # we stop listening for blocks cause it is now unlikely that the event's chain will
            # be the longest again; ideally though, we should only stop listening for blocks after
            # the alternative chain reaches a certain height
            break

        time.sleep(0.1)
