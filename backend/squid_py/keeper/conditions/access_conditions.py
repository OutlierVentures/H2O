from squid_py.keeper.contract_base import ContractBase


class AccessConditions(ContractBase):

    def __init__(self, web3, contract_path):
        super().__init__(web3, contract_path, 'AccessConditions')

    def check_permissions(self, address, asset_id, sender_address):
        return self.contract_concise.checkPermissions(address, asset_id, call={'from': sender_address})
