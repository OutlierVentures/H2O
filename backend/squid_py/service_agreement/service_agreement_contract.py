from squid_py.service_agreement.service_agreement_condition import Event


class ServiceAgreementContract(object):

    def __init__(self, contract_json=None):
        self.contract_address = ''
        self.fulfillmentOperator = 0

        self.events = []
        if contract_json:
            self.init_from_contract_json(contract_json)

    def init_from_contract_json(self, contract_json):
        self.contract_address = contract_json['address']
        self.fulfillmentOperator = contract_json['fulfillmentOperator']
        self.events = [Event(e) for e in contract_json['events']]

    def as_dictionary(self):
        return {
            'address': self.contract_address,
            'fulfillmentOperator': self.fulfillmentOperator,
            'events': [e.as_dictionary() for e in self.events]
        }

    @staticmethod
    def example_dict():
        return {
            "serviceAgreementContract": {
              "address": "0x...",
              "fulfillmentOperator": 0,
              "events": [{
                "name": "ExecuteAgreement",
                "actorType": "consumer",
                "handler": {
                  "moduleName": "payment",
                  "functionName": "lockPayment",
                  "version": "0.1"
                }
              }]
        }}
