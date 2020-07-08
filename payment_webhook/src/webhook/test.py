import random
import braintree
from core import payment_client
payment_client
gateway = payment_client.gateway
TEST_NOTES = [braintree.WebhookNotification.Kind.SubscriptionCanceled,
              braintree.WebhookNotification.Kind.SubscriptionChargedSuccessfully,
              braintree.WebhookNotification.Kind.SubscriptionChargedUnsuccessfully,
              braintree.WebhookNotification.Kind.SubscriptionExpired,
              braintree.WebhookNotification.Kind.SubscriptionTrialEnded,
              braintree.WebhookNotification.Kind.SubscriptionWentActive,
              braintree.WebhookNotification.Kind.SubscriptionWentPastDue,
braintree.WebhookNotification.Kind.Disbursement,
braintree.WebhookNotification.Kind.DisbursementException,
              ]

def dummy_webhook_body():
    fake_id = '5eeb3631a0948f6bcc5936f7'
    kind = TEST_NOTES[random.randint(0, len(TEST_NOTES)-1)]
    sample_notification = gateway.webhook_testing.sample_notification(
        kind,
        fake_id
    )
    return sample_notification['bt_signature'],sample_notification['bt_payload']
