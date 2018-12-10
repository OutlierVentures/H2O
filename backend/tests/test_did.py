"""
    Test did_lib
"""
import json
import pathlib
import pytest
import secrets
from web3 import Web3

from squid_py.did import (
    did_generate,
    did_generate_from_ddo,
    did_parse,
    did_validate,
    is_did_valid,
    id_to_did,
    did_to_id,
    did_to_id_bytes,
)


TEST_SERVICE_TYPE = 'ocean-meta-storage'
TEST_SERVICE_URL = 'http://localhost:8005'


def test_did():
    test_id = '0x%s' % secrets.token_hex(32)
    test_path = 'test_path'
    test_fragment = 'test_fragment'
    test_method = 'abcdefghijklmnopqrstuvwxyz0123456789'
    all_id = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-.'
    valid_did = 'did:op:{0}'.format(test_id)

    assert did_generate(test_id) == valid_did
    assert did_parse(valid_did)['id'] == test_id

    # all valid method values are supported
    valid_method_did = 'did:{0}:{1}'.format(test_method, test_id)
    assert did_generate(test_id, method=test_method) == valid_method_did

    # split method
    assert did_parse(valid_method_did)['method'] == test_method

    # invalid method chars are removed
    assert did_generate(test_id, method=test_method + '!@#$%^&') == valid_method_did

    # all valid method and id's are accepted
    valid_id_method_did = 'did:{0}:{1}'.format(test_method, all_id)
    assert did_generate(all_id, method=test_method) == valid_id_method_did

    # split id and method
    assert did_parse(valid_id_method_did)['method'] == test_method
    assert did_parse(valid_id_method_did)['id'] == all_id

    # invalid id values are masked out
    assert did_generate(all_id + '%^&*()_+=', method=test_method) == valid_id_method_did

    # path can be appended
    valid_path_did = 'did:op:{0}/{1}'.format(test_id, test_path)
    assert did_generate(test_id, test_path) == valid_path_did

    assert did_parse(valid_path_did)['path'] == test_path

    # append path and fragment
    valid_path_fragment_did = 'did:op:{0}/{1}#{2}'.format(test_id, test_path, test_fragment)
    assert did_generate(test_id, test_path, test_fragment) == valid_path_fragment_did

    # assert split of path and fragment
    assert did_parse(valid_path_fragment_did)['path'] == test_path
    assert did_parse(valid_path_fragment_did)['fragment'] == test_fragment

    # append fragment
    valid_fragment_did = 'did:op:{0}#{1}'.format(test_id, test_fragment)
    assert did_generate(test_id, fragment=test_fragment) == valid_fragment_did

    # assert split offragment
    assert did_parse(valid_fragment_did)['fragment'] == test_fragment

    with pytest.raises(TypeError):
        did_parse(None)

    # test invalid in bytes
    with pytest.raises(TypeError):
        assert did_parse(valid_did.encode())


    # test is_did_valid
    assert is_did_valid(valid_did)
    assert not is_did_valid('did:op:{}'.format(all_id))
    assert is_did_valid('did:eth:{}'.format(test_id))
    assert not is_did_valid('op:{}'.format(test_id))

    with pytest.raises(TypeError):
        is_did_valid(None)


    # test invalid in bytes
    with pytest.raises(TypeError):
        assert is_did_valid(valid_did.encode())


    valid_did_text = 'did:op:{}'.format(test_id)
    assert id_to_did(test_id) == valid_did_text

    # accept hex string from Web3 py
    assert id_to_did(Web3.toHex(hexstr=test_id)) == valid_did_text

    #accepts binary value
    assert id_to_did(Web3.toBytes(hexstr=test_id)) == valid_did_text

    with pytest.raises(TypeError):
        id_to_did(None)

    with pytest.raises(TypeError):
        id_to_did({'bad': 'value'})

    assert id_to_did('') == 'did:op:0x0'
    assert did_to_id(valid_did_text) == test_id
    assert did_to_id('did:op1:011') == None
    assert did_to_id('did:op:0x0') == '0x0'


def test_did_to_bytes():
    id_test = secrets.token_hex(32)
    did_test = 'did:op:{}'.format(id_test)
    id_bytes = Web3.toBytes(hexstr=id_test)

    assert did_to_id_bytes(did_test) == id_bytes
    assert did_to_id_bytes(id_bytes) == id_bytes

    with pytest.raises(ValueError):
        assert did_to_id_bytes(id_test) == id_bytes

    with pytest.raises(ValueError):
        assert did_to_id_bytes('0x' + id_test)

    with pytest.raises(ValueError):
        did_to_id_bytes('did:opx:{}'.format(id_test))

    with pytest.raises(ValueError):
        did_to_id_bytes('did:opx:Somebadtexstwithnohexvalue0x123456789abcdecfg')

    with pytest.raises(ValueError):
        did_to_id_bytes('')

    with pytest.raises(ValueError):
        did_to_id_bytes(None)

    with pytest.raises(ValueError):
        did_to_id_bytes({})


    with pytest.raises(ValueError):
        did_to_id_bytes(42)
