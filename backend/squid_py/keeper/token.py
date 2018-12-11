from squid_py.keeper.contract_base import (
    ContractBase,
)


class Token(ContractBase):

    def __init__(self, web3, contract_path):
        ContractBase.__init__(self, web3, contract_path, 'OceanToken')

    def get_ether_balance(self, account_address, block_identifier='latest'):
        return self.web3.eth.getBalance(account_address, block_identifier)

    def get_token_balance(self, account_address):
        """Retrieve the amount of tokens of an account address"""
        return self.contract_concise.balanceOf(account_address)

    def get_allowance(self, owner_address, spender_address):
        return self.contract_concise.allowance(owner_address, spender_address)

    def token_approve(self, spender_address, price, from_account):
        """Approve the passed address to spend the specified amount of tokens."""
        if not self.web3.isChecksumAddress(spender_address):
            spender_address = self.web3.toChecksumAddress(spender_address)

        self.unlock_account(from_account)
        return self.contract_concise.approve(spender_address, price, transact={'from': from_account.address})
