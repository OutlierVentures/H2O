import logging
import uuid
import json
import hashlib
import time
from collections import namedtuple
from threading import Thread

from web3 import Web3
from eth_keys import KeyAPI

Signature = namedtuple('Signature', ('v', 'r', 's'))


def get_publickey_from_address(web3, address):
    _hash = Web3.sha3(text='verify signature.')
    signature = web3.eth.sign(address, _hash)
    return KeyAPI.PublicKey.recover_from_msg_hash(_hash, KeyAPI.Signature(signature))


def generate_new_id(metadata):
    return uuid.uuid4().hex + uuid.uuid4().hex


def get_id_from_did(did):
    return convert_to_bytes(Web3, did.split(':')[-1])


def sign(web3, account_address, message):
    return web3.eth.sign(account_address, message)


def get_balance(web3, account_address, block_identifier):
    return web3.eth.getBalance(account_address, block_identifier)


def watch_event(contract_name, event_name, callback, interval, fromBlock=0, toBlock='latest',
                filters=None, num_confirmations=12):
    event_filter = install_filter(
        contract_name, event_name, fromBlock, toBlock, filters
    )
    event_filter.poll_interval = interval
    Thread(
        target=watcher,
        args=(event_filter, callback),
        kwargs={'num_confirmations': num_confirmations},
        daemon=True,
    ).start()
    return event_filter


def install_filter(contract, event_name, fromBlock=0, toBlock='latest', filters=None):
    # contract_instance = self.contracts[contract_name][1]
    event = getattr(contract.events, event_name)
    event_filter = event.createFilter(
        fromBlock=fromBlock, toBlock=toBlock, argument_filters=filters
    )
    return event_filter


def to_32byte_hex(web3, val):
    return web3.toBytes(val).rjust(32, b'\0')


def split_signature(web3, signature):
    v = web3.toInt(signature[-1])
    r = to_32byte_hex(web3, int.from_bytes(signature[:32], 'big'))
    s = to_32byte_hex(web3, int.from_bytes(signature[32:64], 'big'))
    if v != 27 and v != 28:
        v = 27 + v % 2
    return Signature(v, r, s)


# properties

def network_name(web3):
    """Give the network name."""
    network_id = web3.version.network
    switcher = {
        1: 'Main',
        2: 'orden',
        3: 'Ropsten',
        4: 'Rinkeby',
        42: 'Kovan',
    }
    return switcher.get(network_id, 'development')


def watcher(event_filter, callback, num_confirmations=12):
    while True:
        try:
            events = event_filter.get_new_entries()
        except ValueError as err:
            # ignore error, but log it
            print('Got error grabbing keeper events: ', str(err))
            events = []

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

        # always take a rest
        time.sleep(0.1)


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


def convert_to_bytes(web3, data):
    return web3.toBytes(text=data)


def convert_to_string(web3, data):
    return web3.toHex(data)


def convert_to_text(web3, data):
    return web3.toText(data)
