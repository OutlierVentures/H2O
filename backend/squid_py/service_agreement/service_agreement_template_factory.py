from squid_py.service_agreement.service_types import ServiceTypes
from squid_py.service_agreement.templates.access_template import AccessServiceTemplate


class ServiceAgreementTemplateFactory(object):
    @staticmethod
    def build_service_agreement_template(service_type, contract_path, ):
        if service_type == ServiceTypes.ASSET_ACCESS:
            return ServiceAgreementTemplateFactory.build_access_service_template()
        elif service_type == ServiceTypes.ASSET_ACCESS:
            return ServiceAgreementTemplateFactory.build_cloud_compute_service_template()
        elif service_type == ServiceTypes.ASSET_ACCESS:
            return ServiceAgreementTemplateFactory.build_fitchain_compute_service_template()

    @staticmethod
    def build_access_service_template():
        AccessServiceTemplate.conditions
        return {}

    @staticmethod
    def build_cloud_compute_service_template():
        return {}

    @staticmethod
    def build_fitchain_compute_service_template():
        return {}
