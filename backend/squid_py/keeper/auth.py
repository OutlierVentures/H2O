from squid_py.keeper.contract_base import (
    ContractBase,
)


class Auth(ContractBase):

    def __init__(self, web3, contract_path):
        ContractBase.__init__(self, web3, contract_path, 'OceanAuth')

    def cancel_access_request(self, order_id, sender_address):
        """You can cancel consent and do refund only after consumer makes the payment and timeout."""
        return self.contract_concise.cancelAccessRequest(order_id, call={'from': sender_address})

    def initiate_access_request(self, asset_id, aquarius_address, pubkey, expiry, sender_address):
        """Consumer initiates access request of service"""
        return self.contract_concise.initiateAccessRequest(asset_id,
                                                           aquarius_address,
                                                           pubkey,
                                                           expiry,
                                                           transact={'from': sender_address})

    def commit_access_request(self, order_id, is_available, expiration_date, discovery, permissions,
                              access_agreement_ref, accesss_agreement_type, sender_address, gas_amount):
        """Aquarius commits the access request of service"""
        return self.contract_concise.commitAccessRequest(order_id,
                                                         is_available,
                                                         expiration_date,
                                                         discovery,
                                                         permissions,
                                                         access_agreement_ref,
                                                         accesss_agreement_type,
                                                         transact={
                                                             'from': sender_address,
                                                             'gas': gas_amount}
                                                         )

    def deliver_access_token(self, order_id, enc_jwt, sender_address):
        """Aquarius delivers the access token of service to on-chain"""
        return self.contract_concise.deliverAccessToken(order_id,
                                                        enc_jwt,
                                                        transact={'from': sender_address,
                                                                  'gas': 4000000})

    def get_order_status(self, order_id):
        return self.contract_concise.statusOfAccessRequest(order_id)

    def get_encrypted_access_token(self, order_id, sender_address):
        return self.contract_concise.getEncryptedAccessToken(order_id, call={'from': sender_address})

    def get_event(self, event):
        return
