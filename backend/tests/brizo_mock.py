import json
from unittest.mock import Mock


class BrizoMock(object):
    def __init__(self, ocean_instance):
        self.ocean_instance = ocean_instance

    def get(self, url, *args, **kwargs):
        response = Mock()
        response.data = b'good luck squiddo.'
        response.status_code = '200 OK'
        return response

    def post(self, url, data=None, **kwargs):
        response = Mock()
        if url.endswith('initialize'):
            payload = json.loads(data)
            did = payload['did']
            sa_id = payload['serviceAgreementId']
            sa_def_id = payload['serviceDefinitionId']
            signature = payload['signature']
            consumer = payload['consumerAddress']
            valid_signature = self.ocean_instance.verify_service_agreement_signature(did, sa_id, sa_def_id, consumer, signature)
            assert valid_signature, 'Service agreement signature seems invalid.'
            if valid_signature:
                self.ocean_instance.execute_service_agreement(did, sa_def_id, sa_id, signature, consumer, self.ocean_instance.main_account.address)
                response.status_code = '200 OK'
            else:
                response.status_code = '401 Unauthorized'
        else:
            response.status_code = '404 Not Found'

        return response
