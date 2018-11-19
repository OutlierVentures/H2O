from squid_py.service_agreement.service_agreement_condition import ServiceAgreementCondition
from squid_py.service_agreement.service_agreement_contract import ServiceAgreementContract


class ServiceAgreementTemplate(object):
    DOCUMENT_TYPE = 'OceanProtocolServiceAgreementTemplate'
    TEMPLATE_ID_KEY = 'slaTemplateId'

    def __init__(self, template_json=None):
        self.template_id = ''
        self.name = ''
        self.description = ''
        self.creator = ''
        self.conditions = []
        self.service_agreement_contract = None
        if template_json:
            self.parse_template_json(template_json)

    def parse_template_json(self, template_json):
        assert template_json['type'] == self.DOCUMENT_TYPE, ''
        self.template_id = template_json['id']
        self.name = template_json['name']
        self.description = template_json['description']
        self.creator = template_json['creator']
        self.conditions = [ServiceAgreementCondition(cond_json) for cond_json in template_json['conditions']]
        self.service_agreement_contract = ServiceAgreementContract(template_json['serviceAgreementContract'])

    def as_dictionary(self):
        return {
            'type': self.DOCUMENT_TYPE,
            'id': self.template_id,
            'name': self.name,
            'description': self.description,
            'creator': self.creator,
            'serviceAgreementContract': self.service_agreement_contract.as_dictionary(),
            'conditions': [cond.as_dictionary() for cond in self.conditions],
        }

    @staticmethod
    def example_dict():
        return {
            "type": "OceanProtocolServiceAgreementTemplate",
            "id": "0x419d158c3a5d81d15b0160cf8929916089218bdb4aa78c3ecd16633afd44b8ae",
            "name": "dataAssetAccessServiceAgreement",
            "description": "This service agreement defines the flow for accessing a data asset on the ocean network. Any file or bundle of files can be accessed using this service agreement",
            "creator": "",
            "conditions": [
                {
                    "name": "executeAgreement",
                    "timeout": 0,
                    "conditionKey": "0x123",
                    "contractAddress": "",
                    "functionName": "executeAgreement",
                    "events": [{
                        "name": "ExecuteAgreement",
                        "actorType": "consumer",
                        "handler": {
                            "moduleName": "payment",
                            "functionName": "lockPayment",
                            "version": "0.1"
                        }
                    }]
                }, {
                    "name": "lockPayment",
                    "timeout": 0,
                    "conditionKey": "0x...",
                    "contractAddress": "0x...",
                    "fingerprint": "0x...",
                    "functionName": "lockPayment",
                    "parameters": [
                        {
                            "name": "assetId",
                            "type": "bytes32",
                            "value": ""
                        }, {
                            "name": "price",
                            "type": "uint256",
                            "value": ""
                        }
                    ],
                    "events": [
                        {
                            "name": "PaymentLocked",
                            "actorType": [
                                "publisher"
                            ],
                            "handlers": {
                                "moduleName": "accessControl",
                                "functionName": "grantAccess",
                                "version": "0.1"
                            }
                        }
                    ],
                    "dependencies": [],
                    "dependencyTimeoutFlags": []
                }, {
                    "name": "grantAccess",
                    "timeout": 0,
                    "conditionKey": "0x...",
                    "contractAddress": "0x...",
                    "fingerprint": "0x...",
                    "functionName": "grantAccess",
                    "parameters": [
                        {
                            "name": "assetId",
                            "type": "bytes32",
                            "value": ""
                        }
                    ],
                    "events": [
                        {
                            "name": "AccessGranted",
                            "actorType": [
                                "consumer"
                            ],
                            "handlers": {
                                "moduleName": "paymentProcessing",
                                "functionName": "releasePayment",
                                "version": "0.1"
                            }
                        }
                    ],
                    "dependencies": ["lockPayment"],
                    "dependencyTimeoutFlags": [0]
                }, {
                    "name": "releasePayment",
                    "timeout": 0,
                    "conditionKey": "0x...",
                    "contractAddress": "0x...",
                    "fingerprint": "0x...",
                    "functionName": "releasePayment",
                    "parameters": [
                        {
                            "name": "assetId",
                            "type": "bytes32",
                            "value": ""
                        }, {
                            "name": "price",
                            "type": "uint256",
                            "value": ""
                        }
                    ],
                    "events": [
                        {
                            "name": "PaymentReleased",
                            "actorType": [
                                "consumer"
                            ],
                            "handlers": {
                                "moduleName": "serviceAgreement",
                                "functionName": "fulfillAgreement",
                                "version": "0.1"
                            }
                        }
                    ],
                    "dependencies": ["grantAccess"],
                    "dependencyTimeoutFlags": [0]
                }, {
                    "name": "refundPayment",
                    "timeout": 1,
                    "conditionKey": "0x...",
                    "contractAddress": "0x...",
                    "fingerprint": "0x...",
                    "functionName": "refundPayment",
                    "parameters": [
                        {
                            "name": "assetId",
                            "type": "bytes32",
                            "value": ""
                        }, {
                            "name": "price",
                            "type": "uint256",
                            "value": ""
                        }
                    ],
                    "events": [
                        {
                            "name": "PaymentRefund",
                            "actorType": [
                                "consumer", "publisher"
                            ],
                            "handlers": {
                                "moduleName": "serviceAgreement",
                                "functionName": "terminateAgreement",
                                "version": "0.1"
                            }
                        }
                    ],
                    "dependencies": ["lockPayment", "grantAccess"],
                    "dependencyTimeoutFlags": [0, 1]
                }
            ]
        }