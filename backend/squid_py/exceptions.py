# Exceptions for squid-py


# Raised when an invalid address is passed to the contract loader
class OceanInvalidContractAddress(Exception):
    pass


class OceanKeeperContractsNotFound(Exception):
    pass


# Raised when an DID attribute is assigned to a DID in the same chain of DIDs
class OceanDIDCircularReference(Exception):
    pass


# raised when a requested DID or a DID in the chain cannot be found
class OceanDIDNotFound(Exception):
    pass


# raised when a requested DID or a DID in the chain cannot be found
class OceanDIDUnknownValueType(Exception):
    pass


# raised when a requested DID is already published in OceanDB
class OceanDIDAlreadyExist(Exception):
    pass

class OceanInvalidMetadata(Exception):
    pass
