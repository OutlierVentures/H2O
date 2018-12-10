from secret_store_client.client import Client


class SecretStoreClientMock(Client):
    def __init__(self, *args, **kwargs):
        pass

    def publish_document(self, document_id, document, threshold=0):
        return '!!%s!!' % document

    def decrypt_document(self, document_id, encrypted_document):
        return encrypted_document[2: -2]