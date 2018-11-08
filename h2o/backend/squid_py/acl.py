import jwt as jwt
from OpenSSL import crypto
from collections import namedtuple
from ecies.utils import generate_eth_key
import ecies as ecies

CryptoKeypair = namedtuple('CryptoKeypair', ('private_key', 'public_key'))


def generate_encryption_keys():
    k = generate_eth_key()
    prvhex = k.to_hex()
    pubhex = k.public_key.to_hex()
    return CryptoKeypair(prvhex, pubhex)


def generate_encoding_pair():
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 1024)
    return CryptoKeypair(crypto.dump_privatekey(crypto.FILETYPE_PEM, k),
                         crypto.dump_publickey(crypto.FILETYPE_PEM, k))


def encode(data, secret):
    return jwt.encode(data, secret, algorithm='HS256')


def decode(encoded):
    return jwt.decode(encoded, algorithms='HS256', verify=False)


def encrypt(data, public_key):
    return ecies.encrypt(public_key, data)


def decrypt(encrypted, private_key):
    return ecies.decrypt(private_key, encrypted)
