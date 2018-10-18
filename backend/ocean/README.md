[![banner](https://raw.githubusercontent.com/oceanprotocol/art/master/github/repo-banner%402x.png)](https://oceanprotocol.com)

# squid-py

> 💧 Python wrapper, allowing to integrate the basic Ocean/web3.py capabilities
> [oceanprotocol.com](https://oceanprotocol.com)

[![Travis (.com)](https://img.shields.io/travis/com/oceanprotocol/squid-py.svg)](https://travis-ci.com/oceanprotocol/squid-py)
[![Codacy coverage](https://img.shields.io/codacy/coverage/7084fbf528934327904a49d458bc46d1.svg)](https://app.codacy.com/project/ocean-protocol/squid-py/dashboard)
[![PyPI](https://img.shields.io/pypi/v/squid-py.svg)](https://pypi.org/project/squid-py/)
[![GitHub contributors](https://img.shields.io/github/contributors/oceanprotocol/squid-py.svg)](https://github.com/oceanprotocol/squid-py/graphs/contributors)

---

## Table of Contents

  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Quick-start](#quick-start)
  - [Code style](#code-style)
  - [Testing](#testing)
  - [New Version](#new-version)
  - [License](#license)

---

## Features

Squid-py include the methods to make easy the connection with contracts deployed in different networks.
This repository include also the methods to encrypt and decrypt information.

## Prerequisites

You should have running an instance of BigchainDB and ganache-cli. To get started quickly,
you can start the docker instance in the docker directory:

`docker-compose -f ./docker/docker-compose.yml up`

The docker container has three main service images running;

1. [bigchaindb/bigchaindb](https://hub.docker.com/r/bigchaindb/bigchaindb/):2.0.0-beta1 (with tendermint)
1. [oceanprotocol/keeper-contracts](https://hub.docker.com/r/oceanprotocol/keeper-contracts/):0.1
1. [oceanprotocol/provider](https://hub.docker.com/r/oceanprotocol/provider/):0.1 (API documentation exposed at http://localhost:5000/api/v1/docs/)

Mac: 
if you are running on mac, gnu-sed needs to be installed
```
brew install --with-default-names gnu-sed
```

## Quick-start

When you want to interact with the contracts you have to instantiate this class:

```python
from squid_py.ocean_contracts import OceanContractsWrapper
ocean = OceanContractsWrapper(host='http://localhost', port=8545, config_path='config.ini')    
ocean.init_contracts()
```

If you do not pass the config_path you can pass using **$CONFIG_FILE** environment variable.

It is possible do not pass the config file, but you should be sure of provide the host, port and addresses.
If you opt for this you can pass the addresses using the following environment variables:


- **MARKET_ADDRESS**  Address of your market contract deployed in the network
- **AUTH_ADDRESS**    Address of your auth contract deployed in the network.
- **TOKEN_ADDRESS**   Address of your token contract deployed in the network.
- **KEEPER_HOST**     You can pass the host of your keeper instead of call it explicitly in class.
- **KEEPER_PORT**     You can pass the port of your keeper instead of call it explicitly in class.


After that you have to init the contracts. And you can start to use the methods in the different contracts.

You will find as well two methods that allow you to register and consume an asset.
```python
from squid_py.consumer import register, consume
register(publisher_account=ocean.web3.eth.accounts[1],
         provider_account=ocean.web3.eth.accounts[0],
         price=10,
         ocean_contracts_wrapper=ocean,
         json_metadata=json_consume
                          )
consume(resource=resouce_id,
        consumer_account=ocean.web3.eth.accounts[1],
        provider_account=ocean.web3.eth.accounts[0],
        ocean_contracts_wrapper=ocean,
        json_metadata=json_request_consume)

```

## Configuration

```yaml
[keeper-contracts]
market.address = # Address of your market contract deployed in the network. [Mandatory]
auth.address = # Address of your auth contract deployed in the network. [Mandatory]
token.address = # Address of your token contract deployed in the network. [Mandatory]
keeper.host = # You can pass the host of your keeper instead of call it explicitly in class.
keeper.port = 8545  # You can pass the port of your keeper instead of call it explicitly in class.
contracts.folder =  # You can pass the directory of your contracts instead of use the library.

```

## Code style

The information about code style in python is documented in this two links [python-developer-guide](https://github.com/oceanprotocol/dev-ocean/blob/master/doc/development/python-developer-guide.md)
and [python-style-guide](https://github.com/oceanprotocol/dev-ocean/blob/master/doc/development/python-style-guide.md).
    
## Testing

Automatic tests are setup via Travis, executing `tox`.
Our test use pytest framework.

## New Version

The `bumpversion.sh` script helps to bump the project version. You can execute the script using as first argument {major|minor|patch} to bump accordingly the version.

## License

```
Copyright 2018 Ocean Protocol Foundation Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
