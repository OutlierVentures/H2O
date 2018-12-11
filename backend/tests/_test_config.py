"""
    Test config class

"""

import os

from squid_py.config import (
    Config,
)

test_config_text = """

[keeper-contracts]

market.address = test_market_address
auth.address = test_auth_address
token.address = test_token_address
keeper.url = test_keeper_url
keeper.path = test_keeper_path
gas_limit = 200
aquarius.url = test_aquarius_url

"""


def test_load():
    config = Config(text=test_config_text)
    assert config
    assert config.address_list['market'] == 'test_market_address'
    assert config.address_list['auth'] == 'test_auth_address'
    assert config.address_list['token'] == 'test_token_address'
    assert config.keeper_url == 'test_keeper_url'
    if os.getenv('VIRTUAL_ENV'):
        assert config.keeper_path == os.path.join(os.getenv('VIRTUAL_ENV'), 'contracts')
    else:
        assert config.keeper_path == '/usr/contracts'

    assert config.aquarius_url == 'test_aquarius_url'
    assert config.gas_limit == 200
