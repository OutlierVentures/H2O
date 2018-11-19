from squid_py.service_agreement.service_agreement_template import ServiceAgreementTemplate
from squid_py.service_agreement.utils import get_condition_value_hash


class ServiceAgreement(object):
    SERVICE_DEFINITION_ID_KEY = 'serviceDefinitionId'
    SERVICE_CONTRACT_KEY = 'serviceAgreementContract'
    SERVICE_CONDITIONS_KEY = 'conditions'

    def __init__(self, sa_definition_id, sla_template_id, conditions, service_agreement_contract):
        self.sa_definition_id = sa_definition_id
        self.sla_template_id = sla_template_id
        self.conditions = conditions
        self.service_agreement_contract = service_agreement_contract

    def as_dictionary(self):
        return {
            ServiceAgreement.SERVICE_DEFINITION_ID_KEY: self.sa_definition_id,
            ServiceAgreementTemplate.TEMPLATE_ID_KEY: self.sla_template_id,
            ServiceAgreement.SERVICE_CONTRACT_KEY: self.service_agreement_contract.as_dictionary(),
            ServiceAgreement.SERVICE_CONDITIONS_KEY: [cond.as_dictionary() for cond in self.conditions]
        }

    @property
    def conditions_params_value_hashes(self):
        value_hashes = []
        for cond in self.conditions:
            value_hashes.append(get_condition_value_hash(cond.param_types, cond.param_values))

        return value_hashes

    @property
    def conditions_keys(self):
        return [cond.condition_key for cond in self.conditions]

    @property
    def conditions_contracts(self):
        return [cond.contract_address for cond in self.conditions]

    @property
    def conditions_fingerprints(self):
        return [cond.function_fingerprint for cond in self.conditions]

    @property
    def conditions_dependencies(self):
        name_to_i = {cond.name: i for i, cond in enumerate(self.conditions)}
        i_to_name = {i: cond.name for i, cond in enumerate(self.conditions)}
        for i, cond in enumerate(self.conditions):
            dep = []
            for j in range(len(self.conditions)):
                if i == j:
                    dep.append(0)
                elif self.conditions[j].name in cond.dependencies:
                    dep.append(1)
        # TODO:

        return

    def get_signed_agreement_hash(self, web3, consumer, did, sla_template_id):
        """

        :param web3:
        :param consumer: address
        :param ddo: DDO object
        :param service_definition_id: identifier of a specific service in the ddo
        :param timeout: timeout value of the service agreement

        :return: signed_msg_hash, msg_hash
        """
        # template_id, condition_keys, hashes, timeouts, did = get_service_agreement_params(
        #     ddo, service_definition_id, timeout, values_per_condition
        # )
        # sa = ServiceAgreement(service_definition_id, service.get_values()['conditions'])
        # sla_template_id = service.get_values()[ServiceAgreementTemplate.TEMPLATE_ID_KEY]
        # TODO:
        # condition_keys = generate_condition_keys(sla_template_id, self.conditions_contracts, self.conditions_fingerprints)
        #
        # agreement_hash = generate_service_agreement_hash(
        #     sla_template_id, conditions_keys, hashes, timeouts, self.sa_definition_id, did
        # )
        agreement_hash = ''
        return web3.sign(consumer, agreement_hash), agreement_hash
