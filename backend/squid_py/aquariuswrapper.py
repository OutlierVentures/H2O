import json
import logging

import requests


class AquariusWrapper(object):

    def __init__(self, aquarius_url):
        """
        The Metadata class is a wrapper on the Metadata Store, which has exposed a REST API

        :param aquarius_url:
        """
        if '/api/v1/aquarius/assets' in aquarius_url:
            aquarius_url = aquarius_url[:aquarius_url.find('/api/v1/aquarius/assets')]

        self._base_url = '{}/api/v1/aquarius/assets'.format(aquarius_url)
        self._headers = {'content-type': 'application/json'}

        logging.debug("Metadata Store connected at {}".format(aquarius_url))
        logging.debug("Metadata Store API documentation at {}/api/v1/docs".format(aquarius_url))
        logging.debug("Metadata assets at {}".format(self._base_url))

    def get_service_endpoint(self, did):
        return self._base_url + '/ddo/%s' % did

    def list_assets(self):
        asset_list = json.loads(requests.get(self._base_url).content)
        if asset_list and 'ids' in asset_list:
            return asset_list['ids']
        return []

    def get_asset_metadata(self, asset_did):
        response = requests.get(self._base_url + '/ddo/%s' % asset_did).content
        if not response:
            return {}

        try:
            parsed_response = json.loads(response)
        except TypeError:
            parsed_response = None

        if parsed_response is None:
            return {}
        return parsed_response

    def list_assets_metadata(self):
        return json.loads(requests.get(self._base_url + '/ddo').content)

    def publish_asset_metadata(self, asset_ddo):
        asset_did = asset_ddo.did
        response = requests.post(self._base_url + '/ddo', data=asset_ddo.as_text(), headers=self._headers)
        if response.status_code == 500:
            raise ValueError("This Asset ID already exists! \n\tHTTP Error message: \n\t\t{}".format(response.text))
        elif response.status_code == 400:
            raise Exception("400 ERROR Full error: \n{}".format(response.text))
        elif response.status_code != 201:
            raise Exception("{} ERROR Full error: \n{}".format(response.status_code, response.text))
        elif response.status_code == 201:
            response = json.loads(response.content)
            logging.debug("Published asset DID {}".format(asset_did))
            return response
        else:
            raise Exception("ERROR")

    def update_asset_metadata(self, asset_did, asset_ddo):
        return json.loads(
            requests.put(self._base_url + '/ddo/%s' % asset_did, data=asset_ddo.as_text(),
                         headers=self._headers).content)

    def text_search(self, text, sort=None, offset=100, page=0):
        payload = {"text": text, "sort": sort, "offset": offset, "page": page}
        response = requests.get(
            self._base_url + '/ddo/query',
            params=payload,
            headers=self._headers
        ).content

        if not response:
            return {}

        try:
            parsed_response = json.loads(response)
        except TypeError:
            parsed_response = None

        if parsed_response is None:
            return []
        elif isinstance(parsed_response, list):
            return parsed_response
        else:
            raise ValueError('Unknown search response, expecting a list got "%s.' % type(parsed_response))

    def query_search(self, search_query):
        response = requests.post(
            self._base_url + '/ddo/query',
            data=json.dumps(search_query),
            headers=self._headers
        ).content

        if not response:
            return {}

        try:
            parsed_response = json.loads(response)
        except TypeError:
            parsed_response = None

        if parsed_response is None:
            return []
        elif isinstance(parsed_response, list):
            return parsed_response
        else:
            raise ValueError('Unknown search response, expecting a list got "%s.' % type(parsed_response))

    def retire_asset_metadata(self, asset_did):
        response = requests.delete(self._base_url + '/ddo/%s' % asset_did, headers=self._headers)
        logging.debug("Removed asset DID: {} from metadata store".format(asset_did))
        return response
