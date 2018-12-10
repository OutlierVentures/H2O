from squid_py.service_agreement.service_agreement_condition import Event


class ServiceAgreementContract(object):

    def __init__(self, contract_json=None):
        self.contract_name = ''
        self.fulfillment_operator = 0

        self.events = []
        if contract_json:
            self.init_from_contract_json(contract_json)

    def init_from_contract_json(self, contract_json):
        self.contract_name = contract_json['contractName']
        self.fulfillment_operator = contract_json['fulfillmentOperator']
        self.events = [Event(e) for e in contract_json['events']]

    def as_dictionary(self):
        return {
            'contractName': self.contract_name,
            'fulfillmentOperator': self.fulfillment_operator,
            'events': [e.as_dictionary() for e in self.events]
        }

    @staticmethod
    def example_dict():
        return {
            "serviceAgreementContract": {
              "contractName": "ServiceAgreement",
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
