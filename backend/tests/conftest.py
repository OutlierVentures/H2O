import os

import pytest
from web3 import Web3, HTTPProvider

from squid_py.config import Config
from tests.secret_store_mock import SecretStoreClientMock
from tests.test_utils import get_publisher_ocean_instance, get_consumer_ocean_instance, get_registered_ddo


@pytest.fixture
def secret_store():
    return SecretStoreClientMock


@pytest.fixture
def publisher_ocean_instance():
    return get_publisher_ocean_instance()


@pytest.fixture
def consumer_ocean_instance():
    return get_consumer_ocean_instance()


@pytest.fixture
def registered_ddo():
    return get_registered_ddo(get_publisher_ocean_instance())


@pytest.fixture
def web3_instance():
    path_config = 'config_local.ini'
    os.environ['CONFIG_FILE'] = path_config
    config = Config(path_config)
    return Web3(HTTPProvider(config.keeper_url))
