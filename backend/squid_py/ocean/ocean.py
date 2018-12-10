import json
import os
import os.path

from web3 import Web3, HTTPProvider

from squid_py.ddo.metadata import Metadata
from squid_py.ocean.account import Account
from squid_py.ocean.asset import Asset
from squid_py.aquariuswrapper import AquariusWrapper
from squid_py.config import Config
from squid_py.ddo import DDO
from squid_py.ddo.public_key_rsa import PUBLIC_KEY_TYPE_RSA
from squid_py.keeper import Keeper
from squid_py.log import setup_logging
from squid_py.didresolver import DIDResolver
from squid_py.exceptions import OceanDIDAlreadyExist, OceanInvalidMetadata
from squid_py.service_agreement.register_service_agreement import register_service_agreement
from squid_py.service_agreement.service_agreement import ServiceAgreement
from squid_py.service_agreement.service_agreement_template import ServiceAgreementTemplate
from squid_py.service_agreement.service_factory import ServiceFactory, ServiceDescriptor
from squid_py.service_agreement.service_types import ServiceTypes
from squid_py.service_agreement.utils import make_public_key_and_authentication, register_service_agreement_template
from squid_py.utils.utilities import generate_prefixed_id, prepare_prefixed_hash, prepare_purchase_payload, get_metadata_url
from squid_py.did import did_to_id, did_generate

CONFIG_FILE_ENVIRONMENT_NAME = 'CONFIG_FILE'

setup_logging()


class Ocean:

    def __init__(self, config_file, http_client=None, secret_store_client=None):
        """
        The Ocean class is the entry point into Ocean Protocol.
        This class is an aggregation of
         * the smart contracts via the Keeper class
         * the metadata store
         * and utilities
        Ocean is also a wrapper for the web3.py interface (https://github.com/ethereum/web3.py)
        An instance of Ocean is parameterized by a configuration file.

        :param config_file: path to configuration file
        :param http_client: http client used for sending http requests such as `requests`
        :param secret_store_client: reference to `secret_store_client.client.Client` class or similar
        """

        # Configuration information for the market is stored in the Config class
        self.config = Config(config_file)

        # For development, we use the HTTPProvider Web3 interface
        self._web3 = Web3(HTTPProvider(self.config.keeper_url))

        # With the interface loaded, the Keeper node is connected with all contracts
        self.keeper = Keeper(self._web3, self.config.keeper_path)

        # Add the Metadata store to the interface
        if self.config.aquarius_url:
            self.metadata_store = AquariusWrapper(self.config.aquarius_url)
        else:
            self.metadata_store = None

        downloads_path = os.path.join(os.getcwd(), 'downloads')
        if self.config.has_option('resources', 'downloads.path'):
            downloads_path = self.config.get('resources', 'downloads.path') or downloads_path
        self._downloads_path = downloads_path

        # Collect the accounts
        self.accounts = self.get_accounts()
        assert self.accounts

        parity_address = self._web3.toChecksumAddress(self.config.parity_address) if self.config.parity_address else None
        if parity_address and parity_address in self.accounts:
            self.main_account = self.accounts[parity_address]
            self.main_account.password = self.config.parity_password
        else:
            self.main_account = self.accounts[self._web3.eth.accounts[0]]

        self.did_resolver = DIDResolver(self._web3, self.keeper.didregistry)

        self._http_client = http_client
        if not http_client:
            import requests
            self._http_client = requests

        self._secret_store_client = secret_store_client
        if not secret_store_client:
            from secret_store_client.client import Client
            self._secret_store_client = Client

    def get_accounts(self):
        """
        Returns all available accounts loaded via a wallet, or by Web3.
        :return:
        """
        accounts_dict = dict()
        for account_address in self._web3.eth.accounts:
            accounts_dict[account_address] = Account(self.keeper, account_address)
        return accounts_dict

    def get_asset(self, asset_did):
        """
        Given an asset_did, return the Asset
        :return: Asset object
        """

        return Asset.from_ddo_dict(self.resolve_did(asset_did))

    def search_assets_by_text(self, text, sort=None, offset=100, page=0, aquarius_url=None):
        """
        Search an asset in oceanDB using aquarius.
        :param text String with the value that you are searching.
        :param sort Dictionary to choose order base in some value.
        :param offset Number of elements shows by page.
        :param page Page number.
        :param aquarius_url Url of the aquarius where you want to search. If there is not provided take the default.
        :return: List of assets that match with the query.
        """
        if aquarius_url is not None:
            aquarius = AquariusWrapper(aquarius_url)
            return [Asset.from_ddo_dict(i) for i in aquarius.text_search(text, sort, offset, page)]
        else:
            return [Asset.from_ddo_dict(i) for i in self.metadata_store.text_search(text, sort, offset, page)]

    def search_assets(self, query):
        """
        Search an asset in oceanDB using search query.
        :param query dict with query parameters
            (e.g.) {"offset": 100, "page": 0, "sort": {"value": 1},
                    query: {"service:{$elemMatch:{"metadata": {$exists : true}}}}}
                    Here, OceanDB instance of mongodb can leverage power of mongo queries in 'query' attribute.
                    For more info - https://docs.mongodb.com/manual/reference/method/db.collection.find
        :return: List of assets that match with the query.
        """
        aquarius_url = self.config.aquarius_url

        if aquarius_url is not None:
            aquarius = AquariusWrapper(aquarius_url)
            return [Asset.from_ddo_dict(i) for i in aquarius.query_search(query)]
        else:
            return [Asset.from_ddo_dict(i) for i in self.metadata_store.query_search(query)]

    def register_asset(self, metadata, publisher_address, service_descriptors, threshold=None):
        """
        Register an asset in both the keeper's DIDRegistry (on-chain) and in the Meta Data store (Aquarius)

        :param metadata: dict conforming to the Metadata accepted by Ocean Protocol.
        :param publisher_address: Account of the publisher registering this asset
        :param service_descriptors: list of ServiceDescriptor tuples of length 2. The first item must be one of ServiceTypes and the second
            item is a dict of parameters and values required by the service.
        :return:
        """
        assert publisher_address and self._web3.isChecksumAddress(publisher_address), 'Invalid publisher address "%s"' % publisher_address
        assert publisher_address in self.accounts, 'Unrecognized publisher address %s' % publisher_address
        assert isinstance(metadata, dict), 'Expected metadata of type dict, got "%s"' % type(metadata)
        if not metadata or not Metadata.validate(metadata):
            raise OceanInvalidMetadata('Metadata seems invalid. Please make sure the required metadata values are filled in.')

        asset_id = generate_prefixed_id()
        # Check if it's already registered first!
        if asset_id in self.metadata_store.list_assets():
            raise OceanDIDAlreadyExist('Asset id "%s" is already registered to another asset.' % asset_id)

        # copy metadata so we don't change the original
        metadata_copy = metadata.copy()

        # Create a DDO object
        did = did_generate(asset_id)
        ddo = DDO(did)

        # Add public key and authentication
        pub_key, auth = make_public_key_and_authentication(did, publisher_address, self._web3)
        ddo.add_public_key(pub_key)
        ddo.add_authentication(auth, PUBLIC_KEY_TYPE_RSA)

        # Setup metadata service
        # First replace `contentUrls` with encrypted `contentUrls`
        assert metadata_copy['base']['contentUrls'], 'contentUrls is required in the metadata base attributes.'
        assert Metadata.validate(metadata), 'metadata seems invalid.'

        content_urls_encrypted = self._encrypt_metadata_content_urls(did, json.dumps(metadata_copy['base']['contentUrls']))
        # only assign if the encryption worked
        if content_urls_encrypted:
            metadata_copy['base']['contentUrls'] = content_urls_encrypted
        else:
            raise AssertionError('Encrypting the contentUrls failed. Make sure the secret store is setup properly in your config file.')

        # DDO url and `Metadata` service
        ddo_service_endpoint = self.metadata_store.get_service_endpoint(did)
        metadata_service_desc = ServiceDescriptor.metadata_service_descriptor(metadata_copy, ddo_service_endpoint)

        # Add all services to ddo
        _service_descriptors = service_descriptors + [metadata_service_desc]
        for service in ServiceFactory.build_services(did, _service_descriptors):
            ddo.add_service(service)

        # publish the new ddo in ocean-db/Aquarius
        self.metadata_store.publish_asset_metadata(ddo)

        # register on-chain
        self.keeper.didregistry.register(
            Web3.toBytes(hexstr=asset_id),
            key=Web3.sha3(text='Metadata'),
            url=ddo_service_endpoint,
            account=self.accounts[publisher_address]
        )

        return ddo

    def _approve_token_transfer(self, amount):
        if self.keeper.token.get_token_balance(self.main_account.address) < amount:
            raise ValueError('Account "%s" does not have sufficient tokens to approve for transfer.' % self.main_account.address)

        self.keeper.token.token_approve(self.keeper.payment_conditions.address, amount, self.main_account)

    def _get_ddo_and_service_agreement(self, did, service_index):
        ddo = self.resolve_did(did)
        # Extract all of the params necessary for execute agreement from the ddo
        service = ddo.find_service_by_key_value(ServiceAgreement.SERVICE_DEFINITION_ID_KEY, service_index)
        if not service:
            raise ValueError('Service with definition id "%s" is not found in this DDO.' % service_index)
        service = service.as_dictionary()
        sa = ServiceAgreement.from_service_dict(service)
        sa.update_conditions_keys(self._web3, self.keeper.contract_path)
        service[ServiceAgreement.SERVICE_CONDITIONS_KEY] = [cond.as_dictionary() for cond in sa.conditions]
        return ddo, sa, service

    def _get_service_agreement_to_sign(self, did, service_index):
        ddo, service_agreement, service_def = self._get_ddo_and_service_agreement(did, service_index)
        return generate_prefixed_id(), service_agreement, service_def, ddo

    def sign_service_agreement(self, did, service_index, consumer_address):
        assert consumer_address in self.accounts, 'Unrecognized consumer address %s' % consumer_address
        assert consumer_address == self.main_account.address, \
            'consumer address must be already set as the main account in this instance of Ocean.'

        agreement_id, service_agreement, service_def, ddo = self._get_service_agreement_to_sign(did, service_index)
        self.main_account.unlock()
        signature = service_agreement.get_signed_agreement_hash(
            self._web3, self.keeper.contract_path, agreement_id, consumer_address
        )[0]

        # Must approve token transfer for this purchase
        self._approve_token_transfer(service_agreement.get_price())

        # subscribe to events related to this service_agreement_id before sending the request.
        register_service_agreement(self._web3, self.keeper.contract_path, self.config.storage_path, self.main_account,
                                   agreement_id, did, service_def, 'consumer', service_index,
                                   service_agreement.get_price(), get_metadata_url(ddo), self.consume_service, 0)

        payload = prepare_purchase_payload(did, agreement_id, service_index, signature, consumer_address)
        self._http_client.post(service_agreement.purchase_endpoint, data=payload, headers={'content-type': 'application/json'})

        return agreement_id

    def execute_service_agreement(self, did, service_index, service_agreement_id,
                                  service_agreement_signature, consumer_address, publisher_address):
        """
        Execute the service agreement on-chain using keeper's ServiceAgreement contract.
        The on-chain executeAgreement method requires the following arguments:
        templateId, signature, consumer, hashes, timeouts, serviceAgreementId, did

        `agreement_message_hash` is necessary to verify the signature.
        The consumer `signature` includes the conditions timeouts and parameters value which is used on-chain to verify the values actually
        match the signed hashes.

        :param did: str representation fo the asset DID. Use this to retrieve the asset DDO.
        :param service_index: int identifies the specific service in the ddo to use in this agreement.
        :param service_agreement_id: 32 bytes identifier created by the consumer and will be used on-chain for the executed agreement.
        :param service_agreement_signature: str the signed agreement message hash which includes conditions and their parameters
            values and other details of the agreement.
        :param consumer_address: ethereum account address of consumer
        :param publisher_address: ethereum account address of publisher
        :return:
        """
        assert consumer_address and self._web3.isChecksumAddress(consumer_address), 'Invalid consumer address "%s"' % consumer_address
        assert publisher_address and self._web3.isChecksumAddress(publisher_address), 'Invalid publisher address "%s"' % publisher_address
        assert publisher_address in self.accounts, 'Unrecognized publisher address %s' % publisher_address

        asset_id = did_to_id(did)
        ddo, service_agreement, service_def = self._get_ddo_and_service_agreement(did, service_index)
        content_urls = get_metadata_url(ddo)

        self.verify_service_agreement_signature(
            did, service_agreement_id, service_index,
            consumer_address, service_agreement_signature, ddo=ddo
        )

        # subscribe to events related to this service_agreement_id
        register_service_agreement(self._web3, self.keeper.contract_path, self.config.storage_path, self.main_account,
                                   service_agreement_id, did, service_def, 'publisher', service_index,
                                   service_agreement.get_price(), content_urls, None, 0)

        receipt = self.keeper.service_agreement.execute_service_agreement(
            service_agreement.template_id,
            service_agreement_signature,
            consumer_address,
            service_agreement.conditions_params_value_hashes,
            service_agreement.conditions_timeouts,
            service_agreement_id,
            asset_id,
            self.main_account
        )

        return receipt

    def check_permissions(self, service_agreement_id, did, consumer_address):
        """
        Verify on-chain that the `consumer_address` has permission to access the given `asset_did` according to the `service_agreement_id`.

        :param service_agreement_id:
        :param did:
        :param consumer_address:
        :return: bool True if user has permission
        """
        agreement_consumer = self.keeper.service_agreement.get_service_agreement_consumer(service_agreement_id)
        if agreement_consumer != consumer_address:
            print('Invalid consumer address and/or service agreement id.')
            return False

        document_id = did_to_id(did)
        return self.keeper.access_conditions.check_permissions(consumer_address, document_id, self.main_account.address)

    def verify_service_agreement_signature(self, did, service_agreement_id, service_index, consumer_address, signature, ddo=None):
        if not ddo:
            ddo = self.resolve_did(did)

        service = ddo.find_service_by_key_value(ServiceAgreement.SERVICE_DEFINITION_ID_KEY, service_index)
        if not service:
            raise ValueError('Service with definition id "%s" is not found in this DDO.' % service_index)

        service = service.as_dictionary()
        sa = ServiceAgreement.from_service_dict(service)

        agreement_hash = sa.get_service_agreement_hash(
            self._web3, self.keeper.contract_path, service_agreement_id
        )
        prefixed_hash = prepare_prefixed_hash(agreement_hash)
        # :NOTE: An alternative to `web3.eth.account.recoverHash`, we can
        # use `eth_keys.KeyAPI.PublicKey.recover_from_msg_hash()` just like we do
        # in `squid_py.utils.utilities.get_public-key_from_address`. When using that, make sure
        # to manipulate the `v` value because KeyAPI only supports `v` values of 0 or 1
        # but some eth clients can produce a `v` of 27 or 28. This is why we have to use
        # the `recover_from_msg_hash` method with the `vrs` argument instead of `signature` unless we
        # reassemble the signature from the split `(v,r,s)` tuple. Also must use the prefixed hash
        # message to get an accurate recovery of public-key and address.
        recovered_address = self._web3.eth.account.recoverHash(prefixed_hash, signature=signature)
        return recovered_address == consumer_address

    def _register_service_agreement_template(self, template_dict, owner_account=None):
        if not owner_account:
            owner_account = self.main_account

        sla_template = ServiceAgreementTemplate(template_json=template_dict)
        return register_service_agreement_template(
            self.keeper.service_agreement, self.keeper.contract_path, owner_account, sla_template
        )

    def resolve_did(self, did):
        """
        When you pass a did retrieve the ddo associated.
        :param did:
        :return:
        """
        resolver = self.did_resolver.resolve(did)
        if resolver.is_ddo:
            return self.did_resolver.resolve(did).ddo
        elif resolver.is_url:
            aquarius = AquariusWrapper(resolver.url)
            return DDO(json_text=json.dumps(aquarius.get_asset_metadata(did)))
        else:
            return None

    def _encrypt_metadata_content_urls(self, did, data):
        """
        encrypt string data using the DID as an secret store id,
        if secret store is enabled then return the result from secret store encryption

        return None for no encryption performed
        """
        result = None
        if self.config.secret_store_url and self.config.parity_url and self.main_account:
            publisher = self._secret_store_client(self.config.secret_store_url, self.config.parity_url,
                               self.main_account.address, self.main_account.password)

            document_id = did_to_id(did)
            # :FIXME: -- modify the secret store lib to handle this.
            if document_id.startswith('0x'):
                document_id = document_id[2:]

            result = publisher.publish_document(document_id, data)
        return result

    def _decrypt_content_urls(self, did, encrypted_data):
        result = None
        if self.config.secret_store_url and self.config.parity_url and self.main_account:
            consumer = self._secret_store_client(self.config.secret_store_url, self.config.parity_url,
                              self.main_account.address, self.main_account.password)

            document_id = did_to_id(did)
            # :FIXME: -- modify the secret store lib to handle this.
            if document_id.startswith('0x'):
                document_id = document_id[2:]

            result = consumer.decrypt_document(document_id, encrypted_data)

        return result

    def consume_service(self, service_agreement_id, did, service_index, consumer_account):
        ddo = self.resolve_did(did)

        metadata_service = ddo.get_service(service_type=ServiceTypes.METADATA)
        content_urls = metadata_service.get_values()['metadata']['base']['contentUrls']
        service = ddo.find_service_by_key_value(ServiceAgreement.SERVICE_DEFINITION_ID_KEY, service_index)
        sa = ServiceAgreement.from_service_dict(service.as_dictionary())
        service_url = sa.service_endpoint
        if not service_url:
            print('Consume asset failed, service definition is missing the "serviceEndpoint".')
            raise AssertionError('Consume asset failed, service definition is missing the "serviceEndpoint".')

        # decrypt the contentUrls
        decrypted_content_urls = json.loads(self._decrypt_content_urls(did, content_urls))
        if isinstance(decrypted_content_urls, str):
            decrypted_content_urls = [decrypted_content_urls]
        print('got decrypted contentUrls: ', decrypted_content_urls)

        asset_folder = 'datafile.%s.%s' % (did_to_id(did), service_index)
        asset_folder = os.path.join(self._downloads_path, asset_folder)
        if not os.path.exists(self._downloads_path):
            os.mkdir(self._downloads_path)
        if not os.path.exists(asset_folder):
            os.mkdir(asset_folder)

        for url in decrypted_content_urls:
            if url.startswith('"') or url.startswith("'"):
                url = url[1:-1]

            print('invoke consume endpoint for this url: %s' % url)
            consume_url = (
                    '%s?url=%s&serviceAgreementId=%s&consumerAddress=%s'
                    % (service_url, url, service_agreement_id, consumer_account.address)
            )
            response = self._http_client.get(consume_url)
            if response.status_code == 200:
                download_url = response.url.split('?')[0]
                file_name = os.path.basename(download_url)
                with open(os.path.join(asset_folder, file_name), 'wb') as f:
                    f.write(response.content)
                    print('Saved downloaded file in "%s"' % f.name)
            else:
                print('consume failed: %s' % response.reason)

    def set_main_account(self, address, password):
        self.main_account = Account(self.keeper, self._web3.toChecksumAddress(address), password)
        self.keeper.web3.eth.defaultAccount = self.main_account.address

    def get_order(self):
        pass

    def get_orders_by_account(self):
        pass

    def search_orders(self):
        pass

    def get_service_agreement(self):
        pass
