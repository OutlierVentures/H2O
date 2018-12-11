import hashlib
import json
import logging

from squid_py.ddo import DDO
from squid_py.did import did_to_id, id_to_did
from squid_py.ocean.ocean_base import OceanBase
from squid_py.service_agreement.service_types import ServiceTypes

DDO_SERVICE_METADATA_KEY = 'metadata'


class Asset(OceanBase):
    def __init__(self, ddo, publisher_id=None):
        """
        Represent an asset in the MetaData store

        Constructor methods:
            1. Direct instantiation Asset(**kwargs)
                - Use this method to manually build an asset
            2. From a json DDO file Asset.from_ddo_json_file()
                - Create an asset based on a DDO file
            3.

        :param did: `did:op:0x...`, the 0x id portion must be of length 64 (or 32 bytes)
        :param publisher_id:
        :param ddo: DDO instance
        """

        self._ddo = ddo
        self.publisher_id = publisher_id
        self.asset_id = None
        if self._ddo and self._ddo.is_did_assigend() and self._ddo.is_valid:
            self.assign_did_from_ddo()
        else:
            self.asset_id = hashlib.sha256('assetId'.encode('utf-8')).hexdigest()

        OceanBase.__init__(self, self.asset_id)

    def __str__(self):
        return "Asset {}, publisher: {}".format(self.did, self.publisher_id)

    def assign_did_from_ddo(self):
        """
        #TODO: This is a temporary hack, need to clearly define how DID is assigned!
        :return:
        """
        self.asset_id = did_to_id(self._ddo.did)

    @property
    def did(self):
        """return the DID for this asset"""
        if not self._ddo:
            raise AttributeError("No DDO object in {}".format(self))
        if not self._ddo.is_valid:
            raise ValueError("Invalid DDO object in {}".format(self))

        return self._ddo.did

    @property
    def ddo(self):
        """return ddo object assigned for this asset"""
        return self._ddo

    @classmethod
    def from_ddo_json_file(cls, json_file_path):
        this_asset = cls(DDO(json_filename=json_file_path))
        logging.debug("Asset {} created from ddo file {} ".format(this_asset.did, json_file_path))
        return this_asset

    @classmethod
    def from_ddo_dict(cls, dictionary):
        """return a new Asset object from DDO dictionary"""
        this_asset = cls(ddo=DDO(dictionary=dictionary))
        logging.debug("Asset {} created from ddo dict {} ".format(this_asset.asset_id, dictionary))
        return this_asset

    @classmethod
    def create_from_metadata_file(cls, filename, service_endpoint):
        """return a new Asset object from a metadata JSON file"""
        if filename:
            with open(filename, 'r') as file_handle:
                metadata = json.load(file_handle)
                return Asset.create_from_metadata(metadata, service_endpoint)
        return None

    @classmethod
    def create_from_metadata(cls, metadata, service_endpoint):
        """return a new Asset object from a metadata dictionary"""
        # calc the asset id
        asset_id = hashlib.sha256(json.dumps(metadata['base']).encode('utf-8')).hexdigest()

        # generate a DID from an asset_id
        new_did = id_to_did(asset_id)

        # create a new DDO
        new_ddo = DDO(new_did)
        # add a signature
        private_password = new_ddo.add_signature()
        # add the service endpoint with the meta data
        new_ddo.add_service(ServiceTypes.METADATA, service_endpoint, values={DDO_SERVICE_METADATA_KEY: metadata})
        # add the static proof
        new_ddo.add_proof(0, private_password)
        # create the asset object
        this_asset = cls(ddo=new_ddo)
        logging.debug("Asset {} created from metadata {} ".format(this_asset.asset_id, metadata))
        return this_asset


    @property
    def metadata(self):
        assert self.has_metadata
        return self._get_metadata()

    @property
    def has_metadata(self):
        """return True if this asset has metadata"""
        return not self._get_metadata() is None

    def _get_metadata(self):
        """ protected property to read the metadata from the DDO object"""
        result = None
        metadata_service = self._ddo.get_service(ServiceTypes.METADATA)
        if metadata_service:
            values = metadata_service.get_values()
            if DDO_SERVICE_METADATA_KEY in values:
                result = values[DDO_SERVICE_METADATA_KEY]
        return result

    def get_metadata(self):
        result = None
        metadata_service = self._ddo.get_service(ServiceTypes.METADATA)
        if metadata_service:
            values = metadata_service.get_values()
            if 'metadata' in values:
                result = values['metadata']
        return result


    @property
    def is_valid(self):
        """return True if this asset has a valid DDO and DID"""
        return self._ddo and self._ddo.is_valid

    def assign_metadata(self):
        pass

    def purchase(self, consumer, timeout):
        """
        Generate an order for purchase of this Asset

        :param timeout:
        :param consumer: Account object of the requester
        :return: Order object
        """
        # Check if asset exists

        # Approve the token transfer

        # Submit access request

        return

    def consume(self, order, consumer):
        """

        :param order: Order object
        :param consumer: Consumer Account
        :return: access_url
        :rtype: string
        """

        # Get access token (jwt)

        # Download the asset from the aquarius using the URL in access token
        # Decode the the access token, get service_endpoint and request_id

        return

    def publish_metadata(self):
        pass

    def update_metadata(self):
        pass

    def retire_metadata(self):
        pass

    def get_service_agreements(self):
        pass

    def getId(self):
        return self.asset_id

    def generate_did(self):
        """
        During development, the DID can be generated here for convenience.
        """
        if not self.ddo:
            raise AttributeError("No DDO object in {}".format(self))
        if not self.ddo.is_valid:
            raise ValueError("Invalid DDO object in {}".format(self))

        metadata = self._get_metadata()
        if not metadata:
            raise ValueError("No metedata in {}".format(self))

        if not 'base' in metadata:
            raise ValueError("Invalid metedata in {}".format(self))

        self.asset_id = hashlib.sha256(json.dumps(metadata['base']).encode('utf-8')).hexdigest()
        self._ddo = self._ddo.create_new('did:op:%s' % self.asset_id)

