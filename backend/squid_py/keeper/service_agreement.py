from squid_py.config import DEFAULT_GAS_LIMIT
from squid_py.keeper.contract_base import ContractBase
from web3 import Web3


class ServiceAgreement(ContractBase):
    SERVICE_AGREEMENT_ID = 'serviceAgreementId'

    def __init__(self, web3, contract_path):
        ContractBase.__init__(self, web3, contract_path, 'ServiceAgreement')
        self._defaultGas = DEFAULT_GAS_LIMIT

    def setup_agreement_template(self, template_id, contracts_addresses, fingerprints, dependencies_bits,
                                 service_description, fulfillment_indices, fulfillment_operator, owner_account):
        assert isinstance(service_description, str) and service_description.strip() != '', 'bad service description.'
        assert contracts_addresses and isinstance(contracts_addresses, list), \
            'contracts arg: expected list, got {0}'.format(type(contracts_addresses))
        assert fingerprints and isinstance(fingerprints, list), \
            'fingerprints arg: expected list, got {0}'.format(type(fingerprints))
        assert dependencies_bits and isinstance(dependencies_bits, list), \
            'dependencies_bits arg: expected list, got {0}'.format(type(dependencies_bits))
        for fin in fingerprints:
            assert isinstance(fin, (bytes, bytearray)), 'function finger print must be `bytes` or `bytearray`'

        assert len(contracts_addresses) == len(fingerprints), ''
        assert len(contracts_addresses) == len(dependencies_bits), ''
        for i in fulfillment_indices:
            assert i < len(contracts_addresses), ''
        assert isinstance(fulfillment_operator, int) and fulfillment_operator >= 0, ''

        self.unlock_account(owner_account)
        service_bytes = Web3.toHex(Web3.sha3(text=service_description))
        tx_hash = self.contract_concise.setupAgreementTemplate(
            template_id,
            contracts_addresses,
            fingerprints,
            dependencies_bits,
            service_bytes,
            fulfillment_indices,
            fulfillment_operator,
            transact={'from': owner_account.address, 'gas': DEFAULT_GAS_LIMIT}
        )
        return tx_hash

    def execute_service_agreement(self, template_id, signature, consumer, hashes, timeouts, service_agreement_id, did_id, publisher_account):
        assert len(hashes) == len(timeouts), ''
        assert did_id.startswith('0x'), ''

        self.unlock_account(publisher_account)
        tx_hash = self.contract_concise.executeAgreement(
            template_id, signature, consumer, hashes, timeouts, service_agreement_id, did_id,
            transact={'from': publisher_account.address, 'gas': DEFAULT_GAS_LIMIT}
        )
        # self.web3.eth.waitForTransactionReceipt(tx_hash)
        # receipt = self.web3.eth.getTransactionReceipt(tx_hash)
        # event = self.contract.events.ExecuteAgreement().processReceipt(receipt)

        return tx_hash

    def fulfill_agreement(self, service_agreement_id, from_account):
        self.unlock_account(from_account)
        return self.contract_concise.fulfillAgreement(service_agreement_id)

    def revoke_agreement_template(self, template_id, owner_account):
        self.unlock_account(owner_account)
        return self.contract_concise.revokeAgreementTemplate(template_id)

    def get_template_status(self, sa_template_id):
        return self.contract_concise.getTemplateStatus(sa_template_id)

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
