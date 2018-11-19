from squid_py.keeper.contract_base import (
    ContractBase,
)


class Token(ContractBase):

    def __init__(self, web3, contract_path):
        ContractBase.__init__(self, web3, contract_path, 'OceanToken')

    def get_token_balance(self, account_address):
        """Retrieve the amount of tokens of an account address"""
        return self.contract_concise.balanceOf(account_address)

    def token_approve(self, market_address, price, account_address):
        """Approve the passed address to spend the specified amount of tokens."""
        return self.contract_concise.approve(self._helper.to_checksum_address(market_address),
                                             price,
                                             transact={'from': account_address})

    # def get_ether_balance(self, account_address):
    #     try:
    #         return self._helper.get_balance(account_address, 'latest')
    #     except Exception as e:
    #         logging.error(e)
    #
    #         raise e

    def get_ether_balance(self, account_address, block_identifier='latest'):
        return self.web3.eth.getBalance(account_address, block_identifier)
