from collections import namedtuple

Condition = namedtuple('Condition', ('name', 'path', 'dependencies', 'timeout_flags'))


class ComputeServiceTemplate:
    conditions = [
        Condition('lockPayment', 'PaymentConditions.lockPayment', [], []),
        Condition('uploadModel', 'AccessConditions.uploadModel', ['lockPayment'], [0]),
        Condition('grantAccess', 'AccessConditions.grantAccess', ['uploadModel'], [0]),
        Condition('releasePayment', 'PaymentConditions.releasePayment', ['grantAccess'], [0]),
        Condition('refundPayment', 'PaymentConditions.refundPayment', ['lockPayment', 'grantAccess'], [0, 1])
    ]
