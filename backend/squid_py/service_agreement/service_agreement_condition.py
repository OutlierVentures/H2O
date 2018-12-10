from web3 import Web3


class Parameter:
    def __init__(self, param_json):
        self.name = param_json['name']
        self.type = param_json['type']
        self.value = param_json['value']

    def as_dictionary(self):
        return {
            "name": self.name,
            "type": self.type,
            "value": self.value
        }


class Event:
    """
    Example: (formatted to make Sphinx happy!)

    {
    "name": "PaymentLocked",
    "actorType": ["publisher"],
    "handlers": {
    "moduleName": "accessControl",
    "functionName": "grantAccess",
    "version": "0.1"
    }
    }
    """
    def __init__(self, event_json):
        self.values_dict = dict(event_json)

    @property
    def name(self):
        return self.values_dict['name']

    @property
    def actor_type(self):
        return self.values_dict['actorType']

    @property
    def handler_module_name(self):
        return self.values_dict['handler']['moduleName']

    @property
    def handler_function_name(self):
        return self.values_dict['handler']['functionName']

    @property
    def handler_version(self):
        return self.values_dict['handler']['version']

    def as_dictionary(self):
        return self.values_dict


class ServiceAgreementCondition(object):
    def __init__(self, condition_json=None):
        self.name = ''
        self.timeout = 0
        self.condition_key = ''
        self.contract_name = ''
        self.function_name = ''
        self.is_terminal = False
        self.dependencies = []
        self.timeout_flags = []
        self.parameters = []
        self.events = []
        if condition_json:
            self.init_from_condition_json(condition_json)

    def _read_dependencies(self, dependencies):
        dep_list = []
        timeout_flags = []
        for dep in dependencies:
            dep_list.append(dep['name'])
            timeout_flags.append(dep['timeout'])

        return dep_list, timeout_flags

    def _build_dependencies(self):
        dependencies = [{'name': dep_name, 'timeout': self.timeout_flags[i]} for i, dep_name in enumerate(self.dependencies)]
        return dependencies

    def init_from_condition_json(self, condition_json):
        self.name = condition_json['name']
        self.timeout = condition_json['timeout']
        self.condition_key = condition_json['conditionKey']
        self.contract_name = condition_json['contractName']
        self.function_name = condition_json['functionName']
        self.is_terminal = bool(condition_json['isTerminalCondition'])
        self.dependencies, self.timeout_flags = self._read_dependencies(condition_json['dependencies'])
        assert len(self.dependencies) == len(self.timeout_flags)
        if self.dependencies:
            assert sum(self.timeout_flags) == 0 or self.timeout > 0, 'timeout must be set when any dependency is set to rely on a timeout.'

        self.parameters = [Parameter(p) for p in condition_json['parameters']]
        self.events = [Event(e) for e in condition_json['events']]

    def as_dictionary(self):
        condition_dict = {
            "name": self.name,
            "timeout": self.timeout,
            "conditionKey": self.condition_key,
            "contractName": self.contract_name,
            "functionName": self.function_name,
            "isTerminalCondition": int(self.is_terminal),
            "events": [e.as_dictionary() for e in self.events],
            "parameters": [p.as_dictionary() for p in self.parameters],
            "dependencies": self._build_dependencies(),
        }

        return condition_dict

    @property
    def param_types(self):
        return [parameter.type for parameter in self.parameters]

    @property
    def param_values(self):
        return [parameter.value for parameter in self.parameters]

    @property
    def values_hash(self):
        return Web3.soliditySha3(self.param_types, self.param_values).hex()

    @staticmethod
    def example_dict():
        return {
            "name": "lockPayment",
            "timeout": 0,
            "dependencies": [],
            "isTerminalCondition": 0,
            "conditionKey": "",
            "contractName": "PaymentConditions",
            "functionName": "lockPayment",
            "parameters": [
                {
                    "name": "assetId",
                    "type": "bytes32",
                    "value": "08a429b8529856d59867503f8056903a680935a76950bb9649785cc97869a43d"
                }, {
                    "name": "price",
                    "type": "uint",
                    "value": 10
                }
            ],
            "events": [{
                "name": "PaymentLocked",
                "actorType": "publisher",
                "handler": {
                    "moduleName": "accessControl",
                    "functionName": "grantAccess",
                    "version": "0.1"
                }
            }]
        }
