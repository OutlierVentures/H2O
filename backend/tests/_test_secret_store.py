import json
import hashlib
import secrets
import os

from secret_store_client.client import Client

from squid_py.config import Config

secret_store_url = 'http://localhost:8010'
parity_client_publish_url = 'http://localhost:9545'
publisher_address = "0x594d9f933f4f2df6bb66bb34e7ff9d27acc1c019"
publisher_password = 'password'


def test_secret_store():

    config = Config('config_local.ini')
    test_document = os.path.join('tests', 'resources', 'metadata', 'sample_metadata1.json')
    with open(test_document, 'r') as file_handle:
        metadata = json.load(file_handle)

    publisher = Client(config.secret_store_url, config.parity_url,
                   config.parity_address, config.parity_password)

    metadata_json = json.dumps(metadata)
    document_id = hashlib.sha256((metadata_json + secrets.token_hex(32)).encode()).hexdigest()
    print(document_id)
    result = publisher.publish_document(document_id, metadata_json)
    print(result)
