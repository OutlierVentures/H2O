from squid_py.acl import encode, decode, encrypt, decrypt, generate_encryption_keys, generate_encoding_pair

token = {
    "iss": "resourceowner.com",
    "sub": "WorldCupDatasetForAnalysis",
    "iat": 1516239022,
    "exp": 1826790800,
    "consumer_pubkey": "public_key",
    "temp_pubkey": "Temp. Public Key for Encryption",
    "request_id": "Request Identifier",
    "consent_hash": "Consent Hash",
    "resource_id": "Resource Identifier",
    "timeout": "Timeout comming from AUTH contract",
    "response_type": "Signed_URL",
    "resource_server_plugin": "Azure",
}


def test_encode_decode():
    pubprivkey = generate_encoding_pair()
    encod = encode({"metadata": "example"}, pubprivkey.private_key)
    assert {"metadata": "example"} == decode(encod)


def test_encrypt_decrypt():
    provider_keypair = generate_encoding_pair()
    consumer_keypair = generate_encryption_keys()
    encoded = encode(token, provider_keypair.private_key)
    encrypted = encrypt(encoded, consumer_keypair.public_key)
    decrypted = decrypt(encrypted, consumer_keypair.private_key)
    assert token == decode(decrypted)
