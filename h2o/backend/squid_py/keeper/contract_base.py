"""
    Keeper Contract Base

    All keeper contract inherit from this base class
"""
import json
import logging
import os

from web3.contract import ConciseContract
from squid_py.exceptions import OceanInvalidContractAddress
from squid_py.keeper.utils import get_contract_by_name
from squid_py.utils.utilities import network_name


class ContractBase(object):
    """
    Base class for all contract objects.
    """

    def __init__(self, web3, contract_path, contract_name):
        self.web3 = web3

        contract = self.load(contract_path, contract_name)
        self.contract_concise = contract[0]
        self.contract = contract[1]

        self.address = contract[2]
        self.name = contract_name

        logging.debug("Loaded {}".format(self))

    @property
    def events(self):
        return self.contract.events

    def load(self, contract_path, contract_name):
        """Retrieve a tuple with the concise contract and the contract definition."""
        contract_definition = get_contract_by_name(
            contract_path,
            network_name(self.web3),
            contract_name,
        )
        address = self.to_checksum_address(contract_definition['address'])
        abi = contract_definition['abi']

        concise_contract = self.web3.eth.contract(
            address=address,
            abi=abi,
            ContractFactoryClass=ConciseContract,
        )
        contract = self.web3.eth.contract(
            address=address,
            abi=abi,
        )

        return concise_contract, contract, address

    def to_checksum_address(self, address):
        """Validate the address provided."""
        return self.web3.toChecksumAddress(address)

    def get_tx_receipt(self, tx_hash):
        """Get the receipt of a tx."""
        self.web3.eth.waitForTransactionReceipt(tx_hash)
        return self.web3.eth.getTransactionReceipt(tx_hash)

    def get_event_signature(self, name):
        """Return the event signature from a named event. """
        signature = None
        for item in self.contract.abi:
            if 'name' in item and item['name'] == name and item['type'] == 'event':
                signature = item['signature']
                break

        return signature

    def __str__(self):
        return "{} at {}".format(self.name, self.address)
