import re
from urllib.parse import urlparse
from web3 import Web3

from squid_py.didresolver import (
    VALUE_TYPE_DID,
    VALUE_TYPE_URL,
    VALUE_TYPE_DDO,
)

from squid_py.did import did_to_id_bytes
from squid_py.ddo import DDO
from squid_py.exceptions import OceanDIDCircularReference
from squid_py.keeper.contract_base import ContractBase


class DIDRegistry(ContractBase):
    """
    Class to register and update Ocean DID's
    """

    def __init__(self, web3, contract_path):
        ContractBase.__init__(self, web3, contract_path, 'DIDRegistry')

    def register(self, did_source, url=None, ddo=None, did=None, key=None, account=None):
        """
        Register or update a DID on the block chain using the DIDRegistry smart contract

        :param did_source: DID to register/update, can be a 32 byte or hexstring
        :param url: URL of the resolved DID
        :param ddo: DDO string or DDO object to resolve too
        :param did: DID to resovlve too, can be a 32 byte value or 64 hex string
        :param key: Optional 32 byte key ( 64 char hex )
        :param account: instance of Account to use to register/update the DID
        """

        value_type = VALUE_TYPE_DID
        value = None

        did_source_id = did_to_id_bytes(did_source)

        if not did_source_id:
            raise ValueError('{} must be a valid DID to register'.format(did_source))

        if url:
            value_type = VALUE_TYPE_URL
            value = url
            if not urlparse(url):
                raise ValueError('Invalid URL {0} to register for DID {1}'.format(url, did_source))

        if ddo:
            value_type = VALUE_TYPE_DDO
            if isinstance(ddo, DDO):
                value = ddo.as_text()
            elif isinstance(ddo, str):
                value = ddo
            else:
                raise ValueError('Invalid DDO {0} to register for DID {1}'.format(ddo, did_source))

        if did:
            value_type = VALUE_TYPE_DID
            id_bytes = did_to_id_bytes(did)
            if not id_bytes:
                raise ValueError('Invalid DID {}'.format(did))

            if did_source_id == id_bytes:
                raise OceanDIDCircularReference('Cannot have the same DID that points to itself')

            value = re.sub('^0x', '', Web3.toHex(id_bytes))

        if isinstance(key, str):
            key = Web3.sha3(text=key)

        if key is None:
            key = Web3.toBytes(0)

        if not isinstance(key, bytes):
            raise ValueError('Invalid key value {}, must be bytes or string'.format(key))

        if account is None:
            raise ValueError('You must provide an account to use to register a DID')

        self.unlock_account(account)
        transaction = self.register_attribute(did_source_id, value_type, key, value, account.address)
        receipt = self.get_tx_receipt(transaction)
        return receipt

    def register_attribute(self, did_hash, value_type, key, value, account_address):
        """Register an DID attribute as an event on the block chain

            did_hash: 32 byte string/hex of the DID
            value_type: 0 = DID, 1 = DIDREf, 2 = URL, 3 = DDO
            key: 32 byte string/hex free format
            value: string can be anything, probably DDO or URL
            account_address: owner of this DID registration record
        """
        return self.contract_concise.registerAttribute(
            did_hash,
            value_type,
            key,
            value,
            transact={'from': account_address}
        )

    def get_update_at(self, did):
        """return the block number the last did was updated on the block chain"""
        return self.contract_concise.getUpdateAt(did)
