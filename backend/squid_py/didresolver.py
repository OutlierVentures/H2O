"""
     DID Resolver Class

"""
import logging

from eth_abi import (
    decode_single,
)

from web3 import (
    Web3,
)

from squid_py.exceptions import (
    OceanDIDCircularReference,
    OceanDIDNotFound,
    OceanDIDUnknownValueType
)

from squid_py.did import (
    did_to_id_bytes,
    id_to_did
)

DIDREGISTRY_EVENT_NAME = 'DIDAttributeRegistered'

VALUE_TYPE_DID = 0
VALUE_TYPE_DID_REF = 1
VALUE_TYPE_URL = 2
VALUE_TYPE_DDO = 3

logger = logging.getLogger()


class DIDResolved:
    """
    Class that handles the resolved DID information
    """

    def __init__(self):
        """init the object with an empty set of hops"""
        self._items = []
        self._value = None

    def add_data(self, data, value):
        """
        Add a resolved event data item to the list of resolved items
        as this could be the last item in the chain.

        :param data: dictionary of the DIDRegistry event data
        :param value: formated value depending on the data['value_type'] string, bytes32

        """
        self._items.append(data)
        if data['value_type'] == VALUE_TYPE_DID:
            self._value = id_to_did(value)
        else:
            self._value = value

    @property
    def did_bytes(self):
        """return the resolved did in bytes"""
        if self._items:
            return self._items[-1]['did_bytes']
        return None

    @property
    def owner(self):
        """return the resolved owner address"""
        if self._items:
            return self._items[-1]['owner']
        return None

    @property
    def key(self):
        """return the resolved key"""
        if self._items:
            return self._items[-1]['key']
        return None

    @property
    def block_number(self):
        """return the resolved block number"""
        if self._items:
            return self._items[-1]['block_number']
        return None

    @property
    def value(self):
        """return the resolved value can be a URL/DDO(on chain)/DID(string)"""
        return self._value

    @property
    def value_type(self):
        """return the resolved value type"""
        if self._items:
            return self._items[-1]['value_type']
        return None

    @property
    def is_url(self):
        """return True if the resolved value is an URL"""
        return self._items and self._items[-1]['value_type'] == VALUE_TYPE_URL

    @property
    def url(self):
        """return the resolved URL"""
        if self.is_url:
            return self._value
        return None

    @property
    def is_ddo(self):
        """return True if the resolved value is a DDO JSON string"""
        return self._items and self._items[-1]['value_type'] == VALUE_TYPE_DDO

    @property
    def ddo(self):
        """return the resolved DDO JSON string"""
        if self.is_ddo:
            return self._value
        return None

    @property
    def is_did(self):
        """return True if the resolved value is a DID"""
        return self._items and self._items[-1]['value_type'] == VALUE_TYPE_DID

    @property
    def did(self):
        """return the resolved DID value as a string"""
        if self.is_did:
            return self._value
        return None

    @property
    def items(self):
        """return the list of DIDRegistry items used to get to this resolved value
        the last item is the resolved item"""
        return self._items

    @property
    def hop_count(self):
        """return the number of hops needed to resolve the DID"""
        if self._items:
            return len(self._items)
        return 0


class DIDResolver:
    """
    DID Resolver class
    Resolve DID to a URL/DDO
    """

    def __init__(self, web3, didregistry):
        self._web3 = web3
        self._didregistry = didregistry

        if not self._didregistry:
            raise ValueError('No didregistry contract object provided')

        self._event_signature = self._didregistry.get_event_signature(DIDREGISTRY_EVENT_NAME)
        if not self._event_signature:
            raise ValueError('Cannot find Event {} signature'.format(DIDREGISTRY_EVENT_NAME))

    def resolve(self, did, max_hop_count=0):
        """
        Resolve a DID to an URL/DDO or later an internal/extrenal DID

        :param did: 32 byte value or DID string to resolver, this is part of the ocean DID did:op:<32 byte value>
        :param max_hop_count: max number of hops allowed to find the destination URL/DDO
        :return string: URL or DDO of the resolved DID
        :return None: if the DID cannot be resolved
        :raises TypeError: on non 32byte value as the DID
        :raises TypeError: on any of the resolved values are not string/DID bytes.
        :raises OceanDIDCircularReference: on the chain being pointed back to itself.
        :raises OceanDIDNotFound: if no DID can be found to resolve.
        """

        did_bytes = did_to_id_bytes(did)

        if not isinstance(did_bytes, bytes):
            raise TypeError('You must provide a 32 Byte value')

        resolved = DIDResolved()
        result = None
        did_visited = {}

        # resolve a DID to a URL or DDO
        data = self.get_did(did_bytes)
        while data and (max_hop_count == 0 or resolved.hop_count < max_hop_count):
            if data['value_type'] == VALUE_TYPE_URL or data['value_type'] == VALUE_TYPE_DDO:
                logger.debug('found did {0} -> {1}'.format(Web3.toHex(did_bytes), data['value']))
                if data['value']:
                    try:
                        result = data['value'].decode('utf8')
                    except:
                        raise TypeError(
                            'Invalid string (URL or DDO) data type for a DID value at {}'.format(Web3.toHex(did_bytes)))
                resolved.add_data(data, result)
                data = None
                break
            elif data['value_type'] == VALUE_TYPE_DID:
                logger.debug('found did {0} -> did:op:{1}'.format(Web3.toHex(did_bytes), data['value']))
                try:
                    did_bytes = Web3.toBytes(hexstr=data['value'].decode('utf8'))
                except:
                    raise TypeError('Invalid data type for a DID value at {}. Got "{}" which '
                                    'does not seem like a valid did.'.format(Web3.toHex(did_bytes), data['value'].decode('utf8')))
                resolved.add_data(data, did_bytes)
                result = did_bytes
            elif data['value_type'] == VALUE_TYPE_DID_REF:
                # at the moment the same method as DID, get the hexstr and convert to bytes
                logger.debug('found did {0} -> #{1}'.format(Web3.toHex(did_bytes), data['value']))
                try:
                    did_bytes = Web3.toBytes(hexstr=data['value'].decode('utf8'))
                except:
                    raise TypeError('Invalid data type for a DID value at {}'.format(Web3.toHex(did_bytes)))
                resolved.add_data(data, did_bytes)
                result = did_bytes
            else:
                raise OceanDIDUnknownValueType('Unknown value type {}'.format(data['value_type']))

            data = None
            if did_bytes:
                if did_bytes not in did_visited:
                    did_visited[did_bytes] = True
                else:
                    raise OceanDIDCircularReference('circular reference found at did {}'.format(Web3.toHex(did_bytes)))
                data = self.get_did(did_bytes)

        if resolved.hop_count > 0:
            return resolved
        return None

    def get_did(self, did_bytes):
        """return a did value and value type from the block chain event record using 'did'"""
        result = None

        block_number = self._didregistry.get_update_at(did_bytes)
        logger.debug('block_number %d', block_number)
        if block_number == 0:
            raise OceanDIDNotFound('cannot find DID {}'.format(Web3.toHex(did_bytes)))

        block_filter = self._web3.eth.filter({
            'fromBlock': block_number,
            'toBlock': block_number,
            'topics': [self._event_signature, Web3.toHex(did_bytes)]
        })
        log_items = block_filter.get_all_entries()
        if log_items:
            log_item = log_items[-1]
            value, value_type, block_number = decode_single('(string,uint8,uint256)', \
                Web3.toBytes(hexstr=log_item['data']))
            topics = log_item['topics']
            logger.debug('topics {}'.format(topics))
            result = {
                'value_type': value_type,
                'value': value,
                'block_number': block_number,
                'did_bytes': Web3.toBytes(topics[1]),
                'owner': Web3.toChecksumAddress(topics[2][-20:]),
                'key': Web3.toBytes(topics[3]),
            }
        return result
