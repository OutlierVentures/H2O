import unittest
import os.path
import time
import json
import pathlib
import uuid


from web3 import Web3, HTTPProvider

from squid_py.config import Config
from squid_py.ddo import DDO
from squid_py.keeper.utils import get_fingerprint_bytes_by_name
from squid_py.ocean.ocean import Ocean
from squid_py.service_agreement.service_agreement_template import ServiceAgreementTemplate

CONFIG_PATH = 'config_local.ini'


SAMPLE_METADATA_PATH = os.path.join(pathlib.Path.cwd(), 'tests', 'resources', 'metadata', 'sample_metadata1.json')
assert os.path.exists(SAMPLE_METADATA_PATH), 'sample metadata is not found: "%s"' % SAMPLE_METADATA_PATH
with open(SAMPLE_METADATA_PATH) as f:
    SAMPLE_METADATA = json.load(f)


class TestServiceAgreement(unittest.TestCase):

    def setUp(self):
        self.config = Config(CONFIG_PATH)
        self.web3 = Web3(HTTPProvider(self.config.keeper_url))

        self.ocean = Ocean(CONFIG_PATH)
        self.market = self.ocean.keeper.market
        self.token = self.ocean.keeper.token
        self.payment_conditions = self.ocean.keeper.payment_conditions
        self.access_conditions = self.ocean.keeper.access_conditions
        self.service_agreement = self.ocean.keeper.service_agreement

        self.asset_ddo = None

        self.publisher = self.web3.eth.accounts[0]
        self.consumer = self.web3.eth.accounts[1]
        self.web3.eth.defaultAccount = self.consumer

        # self._load_sla_template()
        # self._setup_service_agreement()
        # self._load_and_build_ddo()
        # self._setup_token(1000)

    def get_events(self, event_filter, max_iterations=100, pause_duration=0.1):
        events = event_filter.get_new_entries()
        i = 0
        while not events and i < max_iterations:
            i += 1
            time.sleep(pause_duration)
            events = event_filter.get_new_entries()

        if not events:
            print('no events found in %s events filter.' % str(event_filter))
        return events

    def process_enc_token(self, event):
        # should get accessId and encryptedAccessToken in the event
        print("token published event: %s" % event)

    def _setup_service_agreement(self):
        self.contracts = [self.payment_conditions.address, self.access_conditions.address, self.payment_conditions.address,
                          self.payment_conditions.address]
        self.fingerprints = [
            get_fingerprint_bytes_by_name(self.web3, self.payment_conditions.contract.abi, 'lockPayment'),
            get_fingerprint_bytes_by_name(self.web3, self.access_conditions.contract.abi, 'grantAccess'),
            get_fingerprint_bytes_by_name(self.web3, self.payment_conditions.contract.abi, 'releasePayment'),
            get_fingerprint_bytes_by_name(self.web3, self.payment_conditions.contract.abi, 'refundPayment'),
        ]
        self.dependencies = [0, 1, 4, 1 | 2 ** 2 | 2 ** 3]
        timeouts = [0, 0, 0, 3]

        template_name = uuid.uuid4().hex
        serviceTemplateId = Web3.sha3(hexstr=template_name)
        encoded_template_name = template_name.encode()
        setup_args = [serviceTemplateId, self.contracts, self.fingerprints, self.dependencies, encoded_template_name, [0], 0]
        print('***** ', setup_args)
        receipt = self.service_agreement.contract_concise.setupAgreementTemplate(
            *setup_args,
            transact={'from': self.consumer}
        )

        tx = self.web3.eth.waitForTransactionReceipt(receipt)
        # print('******** ', self.service_agreement.events.SetupAgreementTemplate().processReceipt(tx))
        # if not self.service_agreement.events.SetupAgreementTemplate().processReceipt(tx):
        #     event = self.service_agreement.events.SetupAgreementTemplate()
        #     filter = self.service_agreement.events.SetupAgreementTemplate().createFilter(fromBlock='0')
        #     print('>>>> ', filter.get_new_entries())
        #     print('>>>> ', filter.get_all_entries())
        self.template_id = Web3.toHex(self.service_agreement.events.
                                      SetupAgreementTemplate().processReceipt(tx)[0].args.
                                      serviceTemplateId)

    def _setup_token(self, amount):
        self.market.contract_concise.requestTokens(amount, transact={'from': self.publisher})
        self.market.contract_concise.requestTokens(amount, transact={'from': self.consumer})

    def _approve_token_transfer(self, amount):
        self.token.contract_concise.approve(
            self.payment_conditions.address,
            amount,
            transact={'from': self.consumer},
        )

    def _load_and_build_ddo(self):
        ddo = DDO(json_filename=os.path.join(pathlib.Path.cwd(), 'tests', 'resources', 'ddo', 'ddo_sa_sample.json'))
        self.asset_ddo = ddo

    def _load_sla_template(self):
        with open(os.path.join(pathlib.Path.cwd(), 'tests', 'resources', 'access_sla_template.json')) as jsf:
            template_json = json.load(jsf)
            self.sla_template = ServiceAgreementTemplate(template_json=template_json)

    def test_keeper(self, ):
        return
        expire_seconds = 5
        asset_price = 100

        publisher_account = self.publisher
        consumer_account = self.consumer
        assert self.market.request_tokens(2000, publisher_account)
        assert self.market.request_tokens(2000, consumer_account)

        # 1. Aquarius register an asset
        asset_id = self.market.register_asset(SAMPLE_METADATA['base']['name'], SAMPLE_METADATA['base']['description'], asset_price, publisher_account)
        assert self.market.check_asset(asset_id)
        assert asset_price == self.market.get_asset_price(asset_id)

        SAMPLE_METADATA['assetId'] = Web3.toHex(asset_id)
        # ocean.metadata.register_asset(json_dict)
        expiry = int(time.time() + expire_seconds)

        # token.token_approve(Web3.toChecksumAddress(market.address), asset_price, consumer_account)

        # buyer_balance_start = token.get_token_balance(consumer_account)
        # seller_balance_start = token.get_token_balance(publisher_account)
        # print('starting buyer balance = ', buyer_balance_start)
        # print('starting seller balance = ', seller_balance_start)
        #
        # print('buyer balance = ', token.get_token_balance(consumer_account))
        # print('seller balance = ', token.get_token_balance(publisher_account))
        # ocean.metadata.retire_asset_metadata(convert_to_string(asset_id))


        #####################################
        # Service Agreement Template
        #
        # Setup a service agreement template


        # prepare ddo to use in service agreement
        service_agreement_id = 1000
        ddo = self.asset_ddo

        #####################################
        # Service Agreement
        service_definition_id = ''
        timeout = 0
        # execute service agreement
        values_per_condition = []
        for condition in ddo.conditions:
            values = []
            values_per_condition.append(values)
        service_agreement.execute_service_agreement(ddo, consumer_account, service_definition_id, timeout, values_per_condition)

        # process ExecuteAgreement event
        # verify consumer balance
        # lockPayment
        # process PaymentLocked event
        # verify consumer balance
        # verify PaymentConditions contract balance

        # grantAccess
        # process AccessGranted event

        # releasePayment
        # process PaymentReleased event
        # verify publisher balance

        # verify consumer balance
        # Repeate execute agreement, lock payment
        # process events
        # verify consumer balance
        # try refundPayment before timeout, should fail
        # wait until timeout occurs
        # refundPayment, should get refund processed
        # process PaymentRefund event
        # verify consumer funds has the original funds returned.

