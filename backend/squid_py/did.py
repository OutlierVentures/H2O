"""
    DID Lib to do DID's and DDO's

"""

import re
from urllib.parse import urlparse
from web3 import Web3

OCEAN_DID_METHOD = 'op'


def did_generate(did_id, path=None, fragment=None, method=OCEAN_DID_METHOD):
    """generate a DID based in it's id, path, fragment and method"""

    method = re.sub('[^a-z0-9]', '', method.lower())
    did_id = re.sub('[^a-zA-Z0-9-.]', '', did_id)
    did = ['did:', method, ':', did_id]
    if path:
        did.append('/')
        did.append(path)
    if fragment:
        did.append('#')
        did.append(fragment)
    return "".join(did)


def did_generate_base_id(did_id, ddo):
    """generate a base did-id, using user defined id, and ddo"""
    values = []
    values.append(did_id)
    # remove the leading '0x' on the DDO hash
    values.append(Web3.toHex(ddo.calculate_hash())[2:])
    # return the hash as a string with no leading '0x'
    return Web3.toHex(Web3.sha3(text="".join(values)))[2:]


def did_generate_from_ddo(did_id, ddo, path=None, fragment=None, method=OCEAN_DID_METHOD):
    """
    generate a new DID from a configured DDO, returns the new DID, and a
    new DDO with the id values already assigned
    """
    base_id = did_generate_base_id(did_id, ddo)
    did = did_generate(base_id, method=method)
    assigned_ddo = ddo.create_new(did)
    return did_generate(base_id, path, fragment, method), assigned_ddo


def did_validate(did, did_id, ddo):
    """validate a DID and check to see it matches the user defined 'id', and DDO"""
    base_id = did_generate_base_id(did_id, ddo)
    did_items = did_parse(did)
    if did_items:
        return did_items['id'] == base_id
    return False


def did_parse(did):
    """parse a DID into it's parts"""
    result = None
    if not isinstance(did, str):
        raise TypeError('DID must be a string')

    match = re.match('^did:([a-z0-9]+):([a-zA-Z0-9-.]+)(.*)', did)
    if match:
        result = {
            'method': match.group(1),
            'id': match.group(2),
            'path': None,
            'fragment': None,
            'id_hex': None
        }
        uri_text = match.group(3)
        if uri_text:
            uri = urlparse(uri_text)
            result['fragment'] = uri.fragment
            if uri.path:
                result['path'] = uri.path[1:]

        if result['method'] == OCEAN_DID_METHOD and re.match('^[0-9A-Fa-f]{1,64}$', result['id']):
            result['id_hex'] = Web3.toHex(hexstr=result['id'])

        if not result['id_hex'] and result['id'].startswith('0x'):
            result['id_hex'] = result['id']

    return result


def is_did_valid(did):
    """
        Return True if the did is a valid DID with the method name 'op' and the id
        in the Ocean format
    """
    result = did_parse(did)
    if result:
        return result['id_hex'] is not None
    return False


def id_to_did(did_id, method='op'):
    """returns an Ocean DID from given a hex id"""
    if isinstance(did_id, bytes):
        did_id = Web3.toHex(did_id)

    # remove leading '0x' of a hex string
    if isinstance(did_id, str):
        did_id = re.sub('^0x', '', did_id)
    else:
        raise TypeError("did id must be a hex string or bytes")

    # test for zero address
    if Web3.toBytes(hexstr=did_id) == b'':
        did_id = '0'
    return 'did:{0}:0x{1}'.format(method, did_id)


def did_to_id(did):
    """return an id extracted from a DID string"""
    result = did_parse(did)
    if result and result['id_hex'] is not None:
        return result['id_hex']
    return None


def did_to_id_bytes(did):
    """
    return an Ocean DID to it's correspondng hex id in bytes
    So did:op:<hex>, will return <hex> in byte format
    """
    id_bytes = None
    if isinstance(did, str):
        if re.match('^[0x]?[0-9A-Za-z]+$', did):
            raise ValueError('{} must be a DID not a hex string'.format(did))
        else:
            did_result = did_parse(did)
            if not did_result:
                raise ValueError('{} is not a valid did'.format(did))
            if not did_result['id_hex']:
                raise ValueError('{} is not a valid ocean did'.format(did))
            id_bytes = Web3.toBytes(hexstr=did_result['id_hex'])
    elif isinstance(did, bytes):
        id_bytes = did
    else:
        raise ValueError('{} must be a valid DID to register'.format(did))
    return id_bytes
