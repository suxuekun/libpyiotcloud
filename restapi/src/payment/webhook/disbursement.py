'''
Disbursement
braintree.WebhookNotification.Kind.Disbursement
braintree.WebhookNotification.Kind.DisbursementException
# braintree.WebhookNotification.Kind.TransactionDisbursed
'''
import braintree

def disbursement(webhook_notification):
    # TODO
    pass

def disbursement_exception(webhook_notification):
    # TODO
    pass

HANDLERS={
    braintree.WebhookNotification.Kind.Disbursement:disbursement,
    braintree.WebhookNotification.Kind.DisbursementException:disbursement_exception,
}