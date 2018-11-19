
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

    def as_dictionary(self):
        return self.values_dict


class ServiceAgreementCondition(object):
    def __init__(self, condition_json=None):
        self.name = ''
        self.condition_key = ''
        self.contract_address = ''
        self.function_fingerprint = ''
        self.function_name = ''
        self.is_terminal = False
        self.dependencies = []
        self.timeout_flags = []
        self.parameters = []
        self.events = []
        self.timeout = 0
        if condition_json:
            self.init_from_condition_json(condition_json)

    def init_from_condition_json(self, condition_json):
        self.name = condition_json['name']
        self.timeout = condition_json['timeout']
        self.contract_address = condition_json['contractAddress']
        self.condition_key = condition_json['conditionKey']
        self.function_name = condition_json['functionName']
        self.is_terminal = condition_json['isTerminalCondition']
        self.events = [Event(e) for e in condition_json['events']]
        if 'fingerprint' in condition_json:
            self.function_fingerprint = condition_json['fingerprint']
            self.dependencies = condition_json['dependencies']
            self.timeout_flags = condition_json['dependencyTimeoutFlags']
            assert len(self.dependencies) == len(self.timeout_flags)
            if self.dependencies:
                assert sum(self.timeout_flags) == 0 or self.timeout > 0, 'timeout must be set when any dependency is set to rely on a timeout.'

            self.parameters = [Parameter(p) for p in condition_json['parameters']]

    def as_dictionary(self):
        condition_dict = {
            "name": self.name,
            "timeout": self.timeout,
            "conditionKey": self.condition_key,
            "contractAddress": self.contract_address,
            "functionName": self.function_name,
            "isTerminalCondition": self.is_terminal,
            "events": [e.as_dictionary() for e in self.events]
        }
        if self.function_fingerprint:
            condition_dict.update({
                "fingerprint": self.function_fingerprint,
                "dependencies": self.dependencies,
                "dependencyTimeoutFlags": self.timeout_flags,
                "parameters": [p.as_dictionary() for p in self.parameters]
            }),

        return condition_dict

    @property
    def param_types(self):
        return [parameter.type for parameter in self.parameters]

    @property
    def param_values(self):
        return [parameter.value for parameter in self.parameters]

    @staticmethod
    def example_dict():
        return {
            "name": "lockPayment",
            "dependencies": [],
            "isTerminalCondition": False,
            "canBeFulfilledBeforeTimeout": True,
            "conditionKey": {
                "contractAddress": "0x...",
                "fingerprint": "0x..."
            },
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
