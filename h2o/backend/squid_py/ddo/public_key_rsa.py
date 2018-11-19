"""
    Public key RSA

"""

from .public_key_base import PublicKeyBase, PUBLIC_KEY_STORE_TYPE_PEM, PUBLIC_KEY_STORE_TYPE_BASE64

AUTHENTICATION_TYPE_RSA = 'RsaVerificationKey2018'
PUBLIC_KEY_TYPE_RSA = 'RsaSignatureAuthentication2018'


class PublicKeyRSA(PublicKeyBase):
    """Encode key value using RSA"""

    def __init__(self, key_id, **kwargs):
        PublicKeyBase.__init__(self, key_id, **kwargs)
        self._type = PUBLIC_KEY_TYPE_RSA

    def get_authentication_type(self):
        """return the type of authentication supported by this class"""
        return AUTHENTICATION_TYPE_RSA

    def set_encode_key_value(self, value, store_type=PUBLIC_KEY_STORE_TYPE_BASE64):
        """set the value based on the type of encoding supported by RSA"""
        if store_type == PUBLIC_KEY_STORE_TYPE_PEM:
            PublicKeyBase.set_encode_key_value(self, value.exportKey('PEM').decode(), store_type)
        else:
            PublicKeyBase.set_encode_key_value(self, value.exportKey('DER'), store_type)
