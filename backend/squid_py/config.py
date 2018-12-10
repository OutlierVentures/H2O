"""Config data

"""

import configparser
import logging
import os
import site


DEFAULT_KEEPER_HOST = 'localhost'
DEFAULT_KEEPER_PORT = 8545
DEFAULT_KEEPER_URL = 'http://localhost:8545'
DEFAULT_KEEPER_PATH = 'artifacts'
DEFAULT_GAS_LIMIT = 1000000
DEFAULT_NAME_AQUARIUS_URL = 'http://localhost:5000'
DEFAULT_STORAGE_PATH = 'squid_py.db'

NAME_KEEPER_URL = 'keeper.url'
NAME_KEEPER_PATH = 'keeper.path'
NAME_GAS_LIMIT = 'gas_limit'
NAME_AQUARIUS_URL = 'aquarius.url'
NAME_STORAGE_PATH = 'storage.path'

NAME_SECRET_STORE_URL = 'secret_store.url'
NAME_PARITY_URL = 'parity.url'
NAME_PARITY_ADDRESS = 'parity.address'
NAME_PARITY_PASSWORD = 'parity.password'

environ_names = {
    NAME_KEEPER_URL: ['KEEPER_URL', 'Keeper URL'],
    NAME_KEEPER_PATH: ['KEEPER_PATH', 'Path to the keeper contracts'],
    NAME_GAS_LIMIT: ['GAS_LIMIT', 'Gas limit'],
    NAME_AQUARIUS_URL: ['AQUARIUS_URL', 'Aquarius URL'],
    NAME_STORAGE_PATH: ['STORAGE_PATH', 'Path to the local database file'],
    NAME_SECRET_STORE_URL: ['SECRET_STORE_URL', 'Secret Store URL'],
    NAME_PARITY_URL: ['PARITY_URL', 'Parity URL'],
    NAME_PARITY_ADDRESS: ['PARITY_ADDRESS', 'Parity address'],
    NAME_PARITY_PASSWORD: ['PARITY_PASSWORD', 'Parity password'],
}

config_defaults = {
    'keeper-contracts': {
        NAME_KEEPER_URL: DEFAULT_KEEPER_URL,
        NAME_KEEPER_PATH: DEFAULT_KEEPER_PATH,
        NAME_GAS_LIMIT: DEFAULT_GAS_LIMIT,
        NAME_SECRET_STORE_URL: '',
        NAME_PARITY_URL: '',
        NAME_PARITY_ADDRESS: '',
        NAME_PARITY_PASSWORD: '',
    },
    'resources': {
        NAME_AQUARIUS_URL: DEFAULT_NAME_AQUARIUS_URL,
        NAME_STORAGE_PATH: DEFAULT_STORAGE_PATH
    }
}


class Config(configparser.ConfigParser):

    def __init__(self, filename=None, **kwargs):
        configparser.ConfigParser.__init__(self)

        self.read_dict(config_defaults)
        self._section_name = 'keeper-contracts'
        self._logger = kwargs.get('logger', logging.getLogger(__name__))
        self._logger.debug('Config: loading config file %s', filename)

        if filename:
            with open(filename) as fp:
                text = fp.read()
                self.read_string(text)
        else:
            if 'text' in kwargs:
                self.read_string(kwargs['text'])
        self._load_environ()

    def _load_environ(self):
        for option_name, environ_item in environ_names.items():
            value = os.environ.get(environ_item[0])
            if value is not None:
                self._logger.debug('Config: setting environ %s = %s', option_name, value)
                self.set(self._section_name, option_name, value)

    def set_arguments(self, items):
        for name, value in items.items():
            if value is not None:
                self._logger.debug('Config: setting argument %s = %s', name, value)
                self.set(self._section_name, name, value)

    @property
    def keeper_path(self):
        path = self.get(self._section_name, NAME_KEEPER_PATH)
        if os.path.exists(path):
            pass
        elif os.getenv('VIRTUAL_ENV'):
            path = os.path.join(os.getenv('VIRTUAL_ENV'), 'artifacts')
        else:
            path = os.path.join(site.PREFIXES[0], 'artifacts')
        return path

    @property
    def storage_path(self):
        return self.get('resources', NAME_STORAGE_PATH)

    @property
    def keeper_url(self):
        return self.get(self._section_name, NAME_KEEPER_URL)

    @property
    def gas_limit(self):
        return int(self.get(self._section_name, NAME_GAS_LIMIT))

    @property
    def aquarius_url(self):
        return self.get('resources', NAME_AQUARIUS_URL)

    @property
    def secret_store_url(self):
        return self.get(self._section_name, NAME_SECRET_STORE_URL)

    @property
    def parity_url(self):
        return self.get(self._section_name, NAME_PARITY_URL)

    @property
    def parity_address(self):
        return self.get(self._section_name, NAME_PARITY_ADDRESS)

    @property
    def parity_password(self):
        return self.get(self._section_name, NAME_PARITY_PASSWORD)

    # static methods

    @staticmethod
    def get_environ_help():
        result = []
        for option_name, environ_item in environ_names.items():
            # codacy fix
            assert option_name
            result.append("{:20}{:40}".format(environ_item[0], environ_item[1]))
        return "\n".join(result)
