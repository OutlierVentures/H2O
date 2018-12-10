from collections import namedtuple

Condition = namedtuple('Condition', ('name', 'path', 'dependencies', 'dependencyTimeoutFlags', 'events'))
Event = namedtuple('Event', ('name', 'actorType', 'handler'))


class AccessServiceTemplate:
    path = 'ServiceAgreement.executeAgreement'
    fulfillment_operator = 1
    events = Event('ExecuteAgreement', 'consumer', {'handler': ()})
    conditions = [
        Condition('lockPayment', 'PaymentConditions.lockPayment', [], [],
                  [Event('PaymentLocked', ['publisher'], {})]),
        Condition('grantAccess', 'AccessConditions.grantAccess', ['lockPayment'], [0],
                  [Event('AccessGranted', ['consumer'], {})]),
        Condition('releasePayment', 'PaymentConditions.releasePayment', ['grantAccess'], [0],
                  [Event('PaymentReleased', ['publisher'], {})]),
        Condition('refundPayment', 'PaymentConditions.refundPayment', ['lockPayment', 'grantAccess'], [0, 1],
                  [Event('PaymentRefund', ['publisher'], {})])
    ]
