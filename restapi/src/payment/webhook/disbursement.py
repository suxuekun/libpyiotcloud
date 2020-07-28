'''
Disbursement
braintree.WebhookNotification.Kind.Disbursement
braintree.WebhookNotification.Kind.DisbursementException
# braintree.WebhookNotification.Kind.TransactionDisbursed
'''
import braintree

from payment.services import transaction_service


def disbursement(webhook_notification):
    print('handle transaction disbursement')
    # TODO
    # transaction_service
    return True
def disbursement_exception(webhook_notification):
    # TODO
    pass

HANDLERS={
    braintree.WebhookNotification.Kind.Disbursement:disbursement,
    braintree.WebhookNotification.Kind.DisbursementException:disbursement_exception,
}