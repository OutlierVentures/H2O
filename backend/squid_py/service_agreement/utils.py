import json

from web3 import Web3

from squid_py.service_agreement.service_agreement_template import ServiceAgreementTemplate


def load_service_agreement_template_json(path):
    with open(path) as jsf:
        template_json = json.load(jsf)
        return ServiceAgreementTemplate(template_json=template_json)


def get_condition_value_hash(value_types, values):
    # TODO: update  `value_types` to whatever is actually in the condition_def in the DDO.
    return Web3.soliditySha3(value_types, values)


def generate_condition_keys(web3, template_id, contracts, fingerprints):
    keys = []
    for i in range(len(contracts)):
        keys.append(web3.soliditySha3(
            ['bytes32', 'address', 'bytes4'],
            [template_id, contracts[i], fingerprints[i]]
        ))
    return keys


def get_service_agreement_params(web3, ddo, service_definition_id, timeout, values_per_condition):
    template_id = ddo.sla_template_id
    conditions_def = ddo.get_service_conditions(service_definition_id)
    contracts = [cond_def.contract_address for cond_def in conditions_def]
    fingerprints = [cond_def.fingerprint for cond_def in conditions_def]
    condition_keys = generate_condition_keys(web3, template_id, contracts, fingerprints)
    timeouts = [timeout if condition_def.has_timeout else 0 for  condition_def in conditions_def]
    hashes = [get_condition_value_hash(web3, condition_def, values_per_condition[i])
              for i, condition_def in enumerate(conditions_def)]
    return template_id, condition_keys, hashes, timeouts, ddo.did


def generate_service_agreement_hash(web3, sa_template_id, condition_keys, values_hash_list, timeouts, service_def_id, did):
    return web3.web3.soliditySha3(
        ['bytes32', 'bytes32[]', 'bytes32[]', 'bytes32[]', 'bytes32', 'bytes32'],
        [sa_template_id, condition_keys, values_hash_list, timeouts, service_def_id, did]
    )


def sign_service_agreement(web3, consumer, ddo, service_definition_id, timeout, values_per_condition):
    template_id, condition_keys, hashes, timeouts, did = get_service_agreement_params(
        web3, ddo, service_definition_id, timeout, values_per_condition
    )
    agreement_hash = generate_service_agreement_hash(
        web3, template_id, condition_keys, hashes, timeouts, service_definition_id, did
    )
    return web3.sign(consumer, agreement_hash)
