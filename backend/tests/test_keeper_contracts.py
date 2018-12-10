"""
    Test Keeper Contracts

    This tests basic contract loading and one call to the smart contract to prove
    that the contact can be loaded and used

"""
import os
import secrets

from squid_py.ocean.ocean import Ocean

def get_ocean_instance():
    path_config = 'config_local.ini'
    os.environ['CONFIG_FILE'] = path_config
    ocean = Ocean(os.environ['CONFIG_FILE'])
    return ocean

def test_auth_contract():

    ocean = get_ocean_instance()
    assert ocean

    assert ocean.keeper.auth

    test_id = secrets.token_hex(32)
    assert ocean.keeper.auth.get_order_status(test_id) == 0


def test_didresitry_contract():

    ocean = get_ocean_instance()
    assert ocean

    assert ocean.keeper.didregistry
    test_id = secrets.token_hex(32)
    # contract call does not work with docker
    assert ocean.keeper.didregistry.get_update_at(test_id) == 0

def test_market_contract():

    ocean = get_ocean_instance()
    assert ocean

    assert ocean.keeper.market
    test_id = secrets.token_hex(32)
    assert ocean.keeper.market.verify_order_payment(test_id)


def test_token_contract():

    ocean = get_ocean_instance()
    assert ocean

    token_account = list(ocean.accounts)[len(list(ocean.accounts)) - 1]
    assert ocean.keeper.token
    assert ocean.keeper.token.get_token_balance(token_account) == 0


