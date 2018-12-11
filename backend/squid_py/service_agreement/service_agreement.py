from eth_utils import add_0x_prefix
from web3 import Web3

from squid_py.service_agreement.service_agreement_condition import ServiceAgreementCondition
from squid_py.service_agreement.service_agreement_contract import ServiceAgreementContract
from squid_py.service_agreement.service_agreement_template import ServiceAgreementTemplate
from squid_py.service_agreement.utils import get_conditions_with_updated_keys


class ServiceAgreement(object):
    SERVICE_DEFINITION_ID_KEY = 'serviceDefinitionId'
    SERVICE_CONTRACT_KEY = 'serviceAgreementContract'
    SERVICE_CONDITIONS_KEY = 'conditions'
    PURCHASE_ENDPOINT_KEY = 'purchaseEndpoint'
    SERVICE_ENDPOINT_KEY = 'serviceEndpoint'

    def __init__(self, sa_definition_id, template_id, conditions, service_agreement_contract, purchase_endpoint=None, service_endpoint=None):
        self.sa_definition_id = sa_definition_id
        self.template_id = add_0x_prefix(template_id)
        self.conditions = conditions
        self.service_agreement_contract = service_agreement_contract
        self.purchase_endpoint = purchase_endpoint
        self.service_endpoint = service_endpoint

    def get_price(self):
        for cond in self.conditions:
            for p in cond.parameters:
                if p.name == 'price':
                    return p.value

    @property
    def conditions_params_value_hashes(self):
        value_hashes = []
        for cond in self.conditions:
            value_hashes.append(cond.values_hash)

        return value_hashes

    @property
    def conditions_timeouts(self):
        return [cond.timeout for cond in self.conditions]

    @property
    def conditions_keys(self):
        return [cond.condition_key for cond in self.conditions]

    @property
    def conditions_contracts(self):
        return [cond.contract_address for cond in self.conditions]

    @property
    def conditions_fingerprints(self):
        return [cond.function_fingerprint for cond in self.conditions]

    @classmethod
    def from_service_dict(cls, service_dict):
        return cls(
            service_dict[cls.SERVICE_DEFINITION_ID_KEY], service_dict[ServiceAgreementTemplate.TEMPLATE_ID_KEY],
            [ServiceAgreementCondition(cond) for cond in service_dict[cls.SERVICE_CONDITIONS_KEY]],
            ServiceAgreementContract(service_dict[cls.SERVICE_CONTRACT_KEY]),
            service_dict.get(cls.PURCHASE_ENDPOINT_KEY), service_dict.get(cls.SERVICE_ENDPOINT_KEY)
        )

    @staticmethod
    def generate_service_agreement_hash(web3, sa_template_id, condition_keys, values_hash_list, timeouts, service_agreement_id):
        return web3.soliditySha3(
            ['bytes32', 'bytes32[]', 'bytes32[]', 'uint256[]', 'bytes32'],
            [sa_template_id, condition_keys, values_hash_list, timeouts, service_agreement_id]
        )

    def get_service_agreement_hash(self, web3, contract_path, service_agreement_id):
        """Return the hash of the service agreement values to be signed by a consumer.

        :param web3: Web3 instance
        :param contract_path: str -- path to keeper contracts artifacts (abi files)
        :param service_agreement_id: hex str identifies an executed service agreement on-chain
        :return:
        """
        self.update_conditions_keys(web3, contract_path)
        agreement_hash = ServiceAgreement.generate_service_agreement_hash(
            web3, self.template_id, self.conditions_keys,
            self.conditions_params_value_hashes, self.conditions_timeouts, service_agreement_id
        )
        return agreement_hash

    def get_signed_agreement_hash(self, web3, contract_path, service_agreement_id, consumer_address):
        """Return the consumer-signed service agreement hash and the raw hash.

        :param web3: Object -- instance of web3.Web3 to use for signing the message
        :param contract_path: str -- path to keeper contracts artifacts (abi files)
        :param service_agreement_id: hex str -- a new service agreement id for this service transaction
        :param consumer_address: hex str -- address of consumer to sign the message with

        :return: signed_msg_hash, msg_hash
        """
        agreement_hash = self.get_service_agreement_hash(web3, contract_path, service_agreement_id)
        return web3.eth.sign(consumer_address, agreement_hash).hex(), agreement_hash.hex()

    def update_conditions_keys(self, web3, contract_path):
        """Update the conditions keys based on the current keeper contracts.

        :param web3:
        :param contract_path:
        :return:
        """
        self.conditions = get_conditions_with_updated_keys(web3, contract_path, self.conditions, self.template_id)

    def as_dictionary(self):
        return {
            ServiceAgreement.SERVICE_DEFINITION_ID_KEY: self.sa_definition_id,
            ServiceAgreementTemplate.TEMPLATE_ID_KEY: self.template_id,
            ServiceAgreement.SERVICE_CONTRACT_KEY: self.service_agreement_contract.as_dictionary(),
            ServiceAgreement.SERVICE_CONDITIONS_KEY: [cond.as_dictionary() for cond in self.conditions]
        }

