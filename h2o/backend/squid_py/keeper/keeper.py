"""
    Collection of Keeper contracts

"""

import logging

from squid_py.keeper.conditions.access_conditions import AccessConditions
from squid_py.keeper.conditions.payment_conditions import PaymentConditions
from squid_py.keeper.service_agreement import ServiceAgreement
from squid_py.keeper.auth import Auth
from squid_py.keeper.didregistry import DIDRegistry
from squid_py.keeper.market import Market
from squid_py.keeper.token import Token


class Keeper(object):

    def __init__(self, web3, contract_path):
        """
        The Keeper class aggregates all contracts in the Ocean Protocol node

        :param web3: The common web3 object
        :param contract_path: Path for
        :param address_list:
        """

        self.web3 = web3
        self.contract_path = contract_path

        logging.debug("Keeper contract artifacts (JSON) at: {}".format(self.contract_path))

        # The contract objects
        self.market = Market(web3, contract_path)
        self.auth = Auth(web3, contract_path)
        self.token = Token(web3, contract_path)
        self.didregistry = DIDRegistry(web3, contract_path)
        self.service_agreement = ServiceAgreement(web3, contract_path)
        self.payment_conditions = PaymentConditions(web3, contract_path)
        self.access_conditions = AccessConditions(web3, contract_path)
