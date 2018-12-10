from squid_py.ddo.service import Service
from squid_py.did import did_to_id
from squid_py.service_agreement.service_agreement import ServiceAgreement
from squid_py.service_agreement.service_agreement_template import ServiceAgreementTemplate
from squid_py.service_agreement.service_types import ServiceTypes
from squid_py.service_agreement.utils import get_sla_template_path


class ServiceDescriptor(object):
    @staticmethod
    def metadata_service_descriptor(metadata, service_endpoint):
        return (ServiceTypes.METADATA,
                {'metadata': metadata, 'serviceEndpoint': service_endpoint})

    @staticmethod
    def access_service_descriptor(price, purchase_endpoint, service_endpoint, timeout, template_id):
        return (ServiceTypes.ASSET_ACCESS,
                {'price': price, 'purchaseEndpoint': purchase_endpoint, 'serviceEndpoint': service_endpoint,
                 'timeout': timeout, 'templateId': template_id})

    @staticmethod
    def compute_service_descriptor(price, purchase_endpoint, service_endpoint, timeout):
        return (ServiceTypes.CLOUD_COMPUTE,
                {'price': price, 'purchaseEndpoint': purchase_endpoint, 'serviceEndpoint': service_endpoint,
                 'timeout': timeout})


class ServiceFactory(object):
    @staticmethod
    def build_services(did, service_descriptors):
        services = []
        sa_def_key = ServiceAgreement.SERVICE_DEFINITION_ID_KEY
        for i, service_desc in enumerate(service_descriptors):
            service = ServiceFactory.build_service(service_desc, did)
            # set serviceDefinitionId for each service
            service.update_value(sa_def_key, str(i+1))
            services.append(service)

        return services

    @staticmethod
    def build_service(service_descriptor, did):
        assert isinstance(service_descriptor, tuple) and len(
            service_descriptor) == 2, 'Unknown service descriptor format.'
        service_type, kwargs = service_descriptor
        if service_type == ServiceTypes.METADATA:
            return ServiceFactory.build_metadata_service(did, kwargs['metadata'], kwargs['serviceEndpoint'])

        elif service_type == ServiceTypes.ASSET_ACCESS:
            return ServiceFactory.build_access_service(
                did, kwargs['price'], kwargs['purchaseEndpoint'], kwargs['serviceEndpoint'], kwargs['timeout'], kwargs['templateId']
            )

        elif service_type == ServiceTypes.CLOUD_COMPUTE:
            return ServiceFactory.build_compute_service(
                did, kwargs['price'], kwargs['purchaseEndpoint'], kwargs['serviceEndpoint'], kwargs['timeout']
            )

        raise ValueError('Unknown service type "%s"' % service_type)

    @staticmethod
    def build_metadata_service(did, metadata, service_endpoint):
        return Service(did, service_endpoint, ServiceTypes.METADATA, values={'metadata': metadata})

    @staticmethod
    def build_access_service(did, price, purchase_endpoint, service_endpoint, timeout, template_id):
        param_map = {
            'assetId': did_to_id(did),
            'price': price,
            'documentKeyId': did_to_id(did)
        }
        sla_template_path = get_sla_template_path()
        sla_template = ServiceAgreementTemplate.from_json_file(sla_template_path)
        sla_template.template_id = template_id
        conditions = sla_template.conditions[:]
        conditions_json_list = []
        for cond in conditions:
            for param in cond.parameters:
                param.value = param_map[param.name]

            if cond.timeout > 0:
                cond.timeout = timeout

            conditions_json_list.append(cond)

        sa = ServiceAgreement(1, sla_template.template_id, sla_template.conditions,
                              sla_template.service_agreement_contract)
        other_values = {
            ServiceAgreement.SERVICE_DEFINITION_ID_KEY: sa.sa_definition_id,
            ServiceAgreementTemplate.TEMPLATE_ID_KEY: sla_template.template_id,
            ServiceAgreement.SERVICE_CONTRACT_KEY: sa.service_agreement_contract,
            ServiceAgreement.SERVICE_CONDITIONS_KEY: conditions,
            'purchaseEndpoint': purchase_endpoint
        }

        return Service(did, service_endpoint, ServiceTypes.ASSET_ACCESS, values=other_values)

    @staticmethod
    def build_compute_service(did, price, purchase_endpoint, service_endpoint, timeout):
        # TODO: implement this once the compute flow is ready
        return
