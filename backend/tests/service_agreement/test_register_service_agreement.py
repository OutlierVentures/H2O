import os
import time
import unittest
import uuid
from datetime import datetime

from web3 import Web3, HTTPProvider

from squid_py.config import Config
from squid_py.keeper.utils import (
    get_fingerprint_by_name,
    hexstr_to_bytes,
    get_contract_abi_and_address,
    get_network_name)
from squid_py.ocean.ocean import Ocean
from squid_py.service_agreement.register_service_agreement import (
    execute_pending_service_agreements,
    record_service_agreement,
    register_service_agreement
)
from squid_py.service_agreement.storage import get_service_agreements
from squid_py.service_agreement.utils import build_condition_key
from squid_py.utils.utilities import generate_new_id

CONFIG_PATH = 'config_local.ini'
NUM_WAIT_ITERATIONS = 20


class TestRegisterServiceAgreement(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = Config(CONFIG_PATH)
        cls.web3 = Web3(HTTPProvider(cls.config.keeper_url))

        cls.ocean = Ocean(CONFIG_PATH)
        cls.keeper = cls.ocean.keeper
        cls.market = cls.ocean.keeper.market
        cls.token = cls.ocean.keeper.token
        cls.payment_conditions = cls.ocean.keeper.payment_conditions
        cls.access_conditions = cls.ocean.keeper.access_conditions
        cls.service_agreement = cls.ocean.keeper.service_agreement

        cls.consumer_acc = cls.ocean.main_account
        cls.consumer = cls.consumer_acc.address
        cls.web3.eth.defaultAccount = cls.consumer

        cls.price = 7
        cls._setup_service_agreement()
        cls._setup_token()

        cls.storage_path = 'test_squid_py.db'
        cls.content_url = '/content/url'
        cls.start_time = int(datetime.now().timestamp())

    def tearDown(self):
        if os.path.exists(self.storage_path):
            os.remove(self.storage_path)

    def _consume_dummy(self, *args):
        pass

    def _register_agreement(self, agreement_id, did, service_definition, actor_type='consumer', num_confirmations=3):
        register_service_agreement(
            self.web3,
            self.config.keeper_path,
            self.storage_path,
            self.consumer_acc,
            agreement_id,
            did,
            service_definition,
            actor_type,
            0,
            self.price,
            self.content_url,
            consume_callback=self._consume_dummy,
            num_confirmations=num_confirmations,
            start_time=self.start_time
        )

    def get_simple_service_agreement_definition(self, did, price, include_refund=False, timeout=3):
        grant_access_fingerprint = get_fingerprint_by_name(
            self.access_conditions.contract.abi,
            'grantAccess',
        )
        lock_payment_fingerprint = get_fingerprint_by_name(
            self.payment_conditions.contract.abi,
            'lockPayment',
        )
        release_payment_fingerprint = get_fingerprint_by_name(
            self.payment_conditions.contract.abi,
            'releasePayment',
        )
        refund_payment_fingerprint = get_fingerprint_by_name(
            self.payment_conditions.contract.abi,
            'refundPayment',
        )

        sa_def = {
            'type': 'Access',
            'templateId': self.template_id,
            'serviceAgreementContract': {
                'contractName': 'ServiceAgreement',
                'events': [{
                    'name': 'ExecuteAgreement',
                    'actorType': 'consumer',
                    'handler': {
                        'moduleName': 'payment',
                        'functionName': 'lockPayment',
                        'version': '0.1'
                    }
                }],
            },
            'conditions': [
                {
                'name': 'grantAccess',
                'timeout': timeout,
                'isTerminalCondition': 0,
                'dependencies': [
                    {
                        'name': 'lockPayment',
                        'timeout': 0
                    }
                ],
                'conditionKey': "",
                'contractName': 'AccessConditions',
                'functionName': 'grantAccess',
                'parameters': [
                    {
                        'name': 'assetId',
                        'type': 'bytes32',
                        'value': did,
                    },
                    {
                        'name': 'documentKeyId',
                        'type': 'bytes32',
                        'value': did,
                    }
                ],
                'events': [
                    {
                    'name': 'AccessGranted',
                    'actorType': 'publisher',
                    'handler': {
                        'moduleName': 'payment',
                        'functionName': 'releasePayment',
                        'version': '0.1'
                    }},
                    {
                    'name': 'AccessGranted',
                    'actorType': 'consumer',
                    'handler': {
                        'moduleName': 'accessControl',
                        'functionName': 'consumeAsset',
                        'version': '0.1'
                    }},
                    {
                      "name": "AccessTimeout",
                      "actorType": "consumer",
                      "handler": {
                        "moduleName": "payment",
                        "functionName": "refundPayment",
                        "version": "0.1"
                      }
                    }

                ],
            },                 {
                'name': 'lockPayment',
                'timeout': 0,
                'isTerminalCondition': 0,
                'dependencies': [],
                'conditionKey': "",
                'contractName': 'PaymentConditions',
                'functionName': 'lockPayment',
                'parameters': [
                    {
                        'name': 'assetId',
                        'type': 'bytes32',
                        'value': did,
                    },
                    {
                        'name': 'price',
                        'type': 'uint256',
                        'value': price,
                    }
                ],
                'events': [{
                    'name': 'PaymentLocked',
                    'actorType': 'publisher',
                    'handler': {
                        'moduleName': 'accessControl',
                        'functionName': 'grantAccess',
                        'version': '0.1'
                    }
                }],
            }, {
                'name': 'releasePayment',
                'timeout': 0,
                'isTerminalCondition': 1,
                'dependencies': [
                     {
                         'name': 'grantAccess',
                         'timeout': 0
                     }
                 ],
                'conditionKey': "",
                'contractName': 'PaymentConditions',
                'functionName': 'releasePayment',
                'parameters': [
                    {
                        'name': 'assetId',
                        'type': 'bytes32',
                        'value': did,
                    },
                    {
                        'name': 'price',
                        'type': 'uint256',
                        'value': price,
                    }
                ],
                "events": [
                    {
                        "name": "PaymentReleased",
                        "actorType": "consumer",
                        "handler": {
                            "moduleName": "serviceAgreement",
                            "functionName": "fulfillAgreement",
                            "version": "0.1"
                        }
                    }
                ]
            }]
        }
        if include_refund:
            sa_def['conditions'].append(
                {
                "name": "refundPayment",
                "timeout": timeout,
                "conditionKey": "",
                "contractName": "PaymentConditions",
                "functionName": "refundPayment",
                "index": 3,
                "parameters": [
                    {
                        "name": "assetId",
                        "type": "bytes32",
                        "value": did
                    }, {
                        "name": "price",
                        "type": "uint256",
                        "value": price
                    }
                ],
                "events": [
                    {
                        "name": "PaymentRefund",
                        "actorType": "consumer",
                        "handler": {
                            "moduleName": "serviceAgreement",
                            "functionName": "terminateAgreement",
                            "version": "0.1"
                        }
                    }
                ],
                "dependencies": [
                     {
                         'name': 'lockPayment',
                         'timeout': 0
                     },
                     {
                         'name': 'grantAccess',
                         'timeout': 1
                     }
                 ],
                "isTerminalCondition": 1
                }
            )
        for i, cond_dict in enumerate(sa_def['conditions']):
            cond_dict['conditionKey'] = self.condition_keys[i]

        for i, cond_dict in enumerate(sa_def['conditions']):
            assert cond_dict['conditionKey'] == self.condition_keys[i]

        return sa_def

    def test_register_service_agreement_stores_the_record(self):
        service_agreement_id = '0x%s' % generate_new_id()
        did = '0x%s' % generate_new_id()

        self._register_agreement(
            service_agreement_id,
            did,
            {
                'serviceAgreementContract': {
                    'contractName': 'ServiceAgreement',
                    'events': []
                },
                'conditions': []
            },
        )
        expected_agreements = (service_agreement_id, did, 0, self.price, self.content_url, self.start_time, 'pending')
        stored_agreements = get_service_agreements(self.storage_path)[0]
        assert sorted([str(i) for i in expected_agreements]) == sorted([str(i) for i in stored_agreements])

    def test_register_service_agreement_subscribes_to_events(self):
        service_agreement_id = '0x%s' % generate_new_id()
        did = '0x%s' % generate_new_id()
        price = self.price

        self._register_agreement(
            service_agreement_id,
            did,
            self.get_simple_service_agreement_definition(did, price),
            num_confirmations=1,
        )

        self._execute_service_agreement(service_agreement_id, did, price)
        payment_locked = self._wait_for_event(self.payment_conditions.events.PaymentLocked)
        assert payment_locked, 'Expected PaymentLocked to be emitted'

    def test_register_service_agreement_updates_fulfilled_agreements(self):
        service_agreement_id = '0x%s' % generate_new_id()
        did = '0x%s' % generate_new_id()
        price = self.price

        self._register_agreement(
            service_agreement_id,
            did,
            self.get_simple_service_agreement_definition(did, price),
            num_confirmations=0,
        )

        self._register_agreement(
            service_agreement_id,
            did,
            self.get_simple_service_agreement_definition(did, price),
            'publisher',
            num_confirmations=0,
        )

        self._execute_service_agreement(service_agreement_id, did, price)

        payment_locked = self._wait_for_event(self.payment_conditions.events.PaymentLocked)
        assert payment_locked, 'Payment was not locked'

        access_granted = self._wait_for_event(self.access_conditions.events.AccessGranted)
        assert access_granted, 'Access was not granted'

        payment_released = self._wait_for_event(self.payment_conditions.events.PaymentReleased)
        assert payment_released, 'Payment was not released'

        agreement_fulfilled = self._wait_for_event(self.service_agreement.events.AgreementFulfilled)
        assert agreement_fulfilled, 'Agreement was not fulfilled.'

        expected_agreements = (service_agreement_id, did, 0, price, self.content_url, self.start_time, 'fulfilled')
        expected_agreements = sorted([str(i) for i in expected_agreements])
        agreements = []
        for i in range(5):
            agreements = get_service_agreements(self.storage_path, 'fulfilled')
            if agreements and expected_agreements == sorted([str(i) for i in agreements[0]]):
                break

            time.sleep(0.5)

        assert agreements and expected_agreements == sorted([str(i) for i in agreements[0]])
        assert not get_service_agreements(self.storage_path)

    def test_refund_terminates_agreements(self):
        return
        service_agreement_id = '0x%s' % generate_new_id()
        did = '0x%s' % generate_new_id()
        price = self.price

        self._register_agreement(
            service_agreement_id,
            did,
            self.get_simple_service_agreement_definition(did, price, include_refund=True),
            num_confirmations=0,
        )

        self._register_agreement(
            service_agreement_id,
            did,
            self.get_simple_service_agreement_definition(did, price, include_refund=True),
            'publisher',
            num_confirmations=0,
        )

        self._execute_service_agreement(service_agreement_id, did, price)

        def get_condition_key(i):
            return self.web3.soliditySha3(['bytes32', 'address', 'bytes4'], [self.template_id, self.contracts[i], self.fingerprints[i]]).hex()

        payment_locked = self._wait_for_event(self.payment_conditions.events.PaymentLocked)
        lock_cond_status = self.service_agreement.contract_concise.getConditionStatus(service_agreement_id, get_condition_key(1))
        assert lock_cond_status > 0
        grant_access_cond_status = self.service_agreement.contract_concise.getConditionStatus(service_agreement_id, get_condition_key(0))
        release_cond_status = self.service_agreement.contract_concise.getConditionStatus(service_agreement_id, get_condition_key(2))
        assert grant_access_cond_status == 0 and release_cond_status == 0, 'grantAccess and/or releasePayment is fulfilled but not expected to.'

        payment_refund = self._wait_for_event(self.payment_conditions.events.PaymentRefund)
        if not payment_refund:
            refund_cond_status = self.service_agreement.contract_concise.getConditionStatus(service_agreement_id, get_condition_key(3))
            assert refund_cond_status > 0, 'refundPayment not fulfilled'

        agreement_fulfilled = self._wait_for_event(self.service_agreement.events.AgreementFulfilled)
        assert agreement_fulfilled, 'Agreement was not fulfilled.'

        expected_agreements = (service_agreement_id, did, 0, price, self.content_url, self.start_time, 'fulfilled')
        expected_agreements = sorted([str(i) for i in expected_agreements])
        agreements = []
        for i in range(5):
            agreements = get_service_agreements(self.storage_path, 'fulfilled')
            if agreements and expected_agreements == sorted([str(i) for i in agreements[0]]):
                break

            time.sleep(0.5)

        assert agreements and expected_agreements == sorted([str(i) for i in agreements[0]])
        assert not get_service_agreements(self.storage_path)

    def test_execute_pending_service_agreements_subscribes_to_events(self):
        service_agreement_id = '0x%s' % generate_new_id()
        did = '0x%s' % generate_new_id()
        price = self.price

        record_service_agreement(self.storage_path, service_agreement_id, did, 0, price, self.content_url, self.start_time)

        def _did_resolver_fn(did):
            return {
                'service': [
                    self.get_simple_service_agreement_definition(did, price),
                ]
            }

        execute_pending_service_agreements(
            self.web3,
            self.config.keeper_path,
            self.storage_path,
            self.consumer_acc,
            'consumer',
            _did_resolver_fn,
            num_confirmations=0,
        )

        self._execute_service_agreement(service_agreement_id, did, price)

        flt = self.payment_conditions.events.PaymentLocked.createFilter(fromBlock='latest')
        for _ in range(20):
            events = flt.get_new_entries()
            if events:
                break
            time.sleep(0.5)

        assert events, 'Expected PaymentLocked to be emitted'

    @classmethod
    def _setup_service_agreement(cls):
        cls.template_id = '0x%s' % generate_new_id()
        cls.contract_names = [cls.access_conditions.name, cls.payment_conditions.name, cls.payment_conditions.name, cls.payment_conditions.name]
        cls.contract_abis = [
            cls.access_conditions.contract.abi,
            cls.payment_conditions.contract.abi,
            cls.payment_conditions.contract.abi,
            cls.payment_conditions.contract.abi
        ]
        cls.contracts = [
            cls.access_conditions.contract.address,
            cls.payment_conditions.contract.address,
            cls.payment_conditions.contract.address,
            cls.payment_conditions.contract.address
        ]
        cls.fingerprints = [
            hexstr_to_bytes(
                cls.web3,
                get_fingerprint_by_name(cls.access_conditions.contract.abi, 'grantAccess'),
            ),
            hexstr_to_bytes(
                cls.web3,
                get_fingerprint_by_name(cls.payment_conditions.contract.abi, 'lockPayment'),
            ),
            hexstr_to_bytes(
                cls.web3,
                get_fingerprint_by_name(cls.payment_conditions.contract.abi, 'releasePayment'),
            ),
            hexstr_to_bytes(
                cls.web3,
                get_fingerprint_by_name(cls.payment_conditions.contract.abi, 'refundPayment'),
            )
        ]
        cls.condition_keys = [
            cls.web3.soliditySha3(
                ['bytes32', 'address', 'bytes4'],
                [cls.template_id,
                 contract,
                 fingerprint]
            ).hex() for contract, fingerprint in zip(cls.contracts, cls.fingerprints)
        ]

        # lockPayment -> grantAccess -> releasePayment -> refundPayment
        # 4, 8           1, 2           16, 32            64, 128
        cls.dependencies = [4, 0, 1, 4 | 1 | 2]

        template_name = uuid.uuid4().hex.encode()
        setup_args = [
            cls.template_id,
            cls.contracts,
            cls.fingerprints,
            cls.dependencies,
            template_name,
            [2, 3],  # root condition
            1,  # AND
        ]
        cls.consumer_acc.unlock()
        receipt = cls.service_agreement.contract_concise.setupAgreementTemplate(
            *setup_args,
            transact={'from': cls.consumer}
        )
        cls.web3.eth.waitForTransactionReceipt(receipt)

    def _get_conditions_data(self, did, price):
        hashes = [
            self.web3.soliditySha3(
                ['bytes32', 'bytes32'],
                [did, did]
            ).hex(),
            self.web3.soliditySha3(
                ['bytes32', 'uint256'],
                [did, price]
            ).hex(),
            self.web3.soliditySha3(
                ['bytes32', 'uint256'],
                [did, price]
            ).hex(),
            self.web3.soliditySha3(
                ['bytes32', 'uint256'],
                [did, price]
            ).hex()
        ]
        function_names = ['grantAccess', 'lockPayment', 'releasePayment', 'refundPayment']
        _network_name = get_network_name(self.web3)
        for i, key in enumerate(self.condition_keys):
            fn_name = function_names[i]
            abi, address = get_contract_abi_and_address(self.web3, self.keeper.contract_path, self.contract_names[i], _network_name)
            assert abi == self.contract_abis[i], 'abi does not match.'
            assert address == self.contracts[i], 'address does not match'
            f = hexstr_to_bytes(self.web3, get_fingerprint_by_name(abi, fn_name))
            assert f == self.fingerprints[i], 'fingerprint mismatch %s vs %s' % (f, self.fingerprints[i])
            _key = build_condition_key(self.web3, self.contracts[i], f, self.template_id)
            assert _key == key, 'condition key does not match: %s vs %s' % (_key, key)

        timeouts = [3, 0, 0, 3]

        return hashes, timeouts

    def _execute_service_agreement(self, service_agreement_id, did, price):
        hashes, timeouts = self._get_conditions_data(did, price)
        self.consumer_acc.unlock()
        signature = self.web3.eth.sign(
            self.consumer,
            hexstr=self.web3.soliditySha3(
                ['bytes32', 'bytes32[]', 'bytes32[]', 'uint256[]', 'bytes32'],
                [self.template_id,
                 self.condition_keys,
                 hashes,
                 timeouts,
                 service_agreement_id]
            ).hex()
        ).hex()

        execute_args = [
            self.template_id,
            signature,
            self.consumer,
            hashes,
            timeouts,
            service_agreement_id,
            did,
        ]
        self.consumer_acc.unlock()
        self.service_agreement.contract_concise.executeAgreement(
            *execute_args,
            transact={'from': self.consumer}
        )

    @classmethod
    def _setup_token(cls):
        cls.market.contract_concise.requestTokens(100, transact={'from': cls.consumer})

        cls.token.contract_concise.approve(
            cls.payment_conditions.address,
            100,
            transact={'from': cls.consumer},
        )

    def _wait_for_event(self, event):
        _filter = event.createFilter(fromBlock=0)
        for check in range(NUM_WAIT_ITERATIONS):
            events = _filter.get_new_entries()
            if events:
                return events[0]
            time.sleep(0.5)
