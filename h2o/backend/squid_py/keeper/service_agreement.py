from squid_py.config import DEFAULT_GAS_LIMIT
from squid_py.keeper.contract_base import ContractBase
from web3 import Web3


class ServiceAgreement(ContractBase):
    """
    """
    SERVICE_AGREEMENT_ID = 'serviceAgreementId'

    def __init__(self, web3, contract_path):
        ContractBase.__init__(self, web3, contract_path, 'ServiceAgreement')
        self._defaultGas = DEFAULT_GAS_LIMIT

    def setup_agreement_template(self, contracts, fingerprints, dependencies_bits, service_description):
        assert isinstance(service_description, str) and service_description.strip() != '', 'bad service description.'
        assert contracts and isinstance(contracts, list), 'contracts arg: expected list, got {0}'.format(type(contracts))
        assert fingerprints and isinstance(fingerprints, list), 'fingerprints arg: expected list, got {0}'.format(type(fingerprints))
        assert dependencies_bits and isinstance(dependencies_bits, list), 'dependencies_bits arg: expected list, got {0}'.format(type(dependencies_bits))

        service_hash = Web3.toHex(Web3.sha3(text=service_description))
        self.contract_concise.setupAgreementTemplate(contracts, fingerprints, dependencies_bits, service_hash)

    def execute_service_agreement(self, ddo, consumer, service_definition_id, timeout, values_per_condition):
        sa_id, templateId, publisher, status = (None,) * 4

        return sa_id

    def fulfill_agreement(self, service_agreement_id):
        self.contract_concise.fulfillAgreement(service_agreement_id)

    def get_template_status(self, sa_template_id):
        return self.contract_concise.getTemplateStatus(sa_template_id)

    def revoke_agreement_template(self, sa_template_id):
        self.contract_concise.revokeAgreementTemplate(sa_template_id)
        return True

    def get_template_owner(self, sa_template_id):
        return self.contract_concise.getTemplateOwner(sa_template_id)

    def get_template_id(self, service_agreement_id):
        return self.contract_concise.getTemplateId(service_agreement_id)

    def get_agreement_status(self, service_agreement_id):
        return self.contract_concise.getAgreementStatus(service_agreement_id)

    def get_service_agreement_publisher(self, service_agreement_id):
        return self.contract_concise.getAgreementPublisher(service_agreement_id)

    def get_service_agreement_consumer(self, service_agreement_id):
        return self.contract_concise.getServiceAgreementConsumer(service_agreement_id)

    def get_condition_by_fingerprint(self, service_agreement_id, contract_address, function_fingerprint):
        return self.contract_concise.getConditionByFingerprint(service_agreement_id, contract_address, function_fingerprint)

    @staticmethod
    def get_condition_value_hash(web3, condition_def, values):
        # TODO: update  `value_types` to whatever is actually in the condition_def in the DDO.
        return web3.web3.soliditySha3(condition_def.value_types, values)

    @staticmethod
    def generate_condition_keys(web3, template_id, contracts, fingerprints):
        keys = []
        for i in range(len(contracts)):
            keys.append(web3.soliditySha3(
                ['bytes32', 'address', 'bytes4'],
                [template_id, contracts[i], fingerprints[i]]
            ))
        return keys

    @staticmethod
    def get_service_agreement_params(web3, ddo, service_definition_id, timeout, values_per_condition):
        template_id = ddo.sa_template_id
        conditions_def = ddo.get_service_conditions(service_definition_id)
        contracts = [cond_def.contract_address for cond_def in conditions_def]
        fingerprints = [cond_def.fingerprint for cond_def in conditions_def]
        condition_keys = ServiceAgreement.generate_condition_keys(template_id, contracts, fingerprints)
        timeouts = [timeout if condition_def.has_timeout else 0 for  condition_def in conditions_def]
        hashes = [ServiceAgreement.get_condition_value_hash(web3, condition_def, values_per_condition[i])
                  for i, condition_def in enumerate(conditions_def)]
        return template_id, condition_keys, hashes, timeouts, ddo.did

    @staticmethod
    def generate_service_agreement_hash(web3, sa_template_id, condition_keys, values_hash_list, timeouts, service_def_id, did):
        return web3.web3.soliditySha3(
            ['bytes32', 'bytes32[]', 'bytes32[]', 'bytes32[]', 'bytes32', 'bytes32'],
            [sa_template_id, condition_keys, values_hash_list, timeouts, service_def_id, did]
        )

    @staticmethod
    def sign_service_agreement(web3, consumer, ddo, service_definition_id, timeout, values_per_condition):
        template_id, condition_keys, hashes, timeouts, did = ServiceAgreement.get_service_agreement_params(
            web3, ddo, service_definition_id, timeout, values_per_condition
        )
        agreement_hash = ServiceAgreement.generate_service_agreement_hash(
            web3, template_id, condition_keys, hashes, timeouts, service_definition_id, did
        )
        return web3.sign(consumer, agreement_hash)
