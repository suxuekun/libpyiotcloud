import random
import braintree
from payment.core import payment_client
from payment.scheduler.tasks.daily import daily_jobs
from payment.scheduler.tasks.monthly import monthly_jobs
from payment.webhook import handle_webhook
from shared.utils import timestamp_util

gateway = payment_client.gateway
TEST_NOTES = [braintree.WebhookNotification.Kind.SubscriptionCanceled,
              braintree.WebhookNotification.Kind.SubscriptionChargedSuccessfully,
              braintree.WebhookNotification.Kind.SubscriptionChargedUnsuccessfully,
              braintree.WebhookNotification.Kind.SubscriptionExpired,
              braintree.WebhookNotification.Kind.SubscriptionTrialEnded,
              braintree.WebhookNotification.Kind.SubscriptionWentActive,
              braintree.WebhookNotification.Kind.SubscriptionWentPastDue,
              ]

def dummy_webhook_body():
    fake_id = '5eeb3631a0948f6bcc5936f7'
    kind = TEST_NOTES[random.randint(0, len(TEST_NOTES)-1)]
    sample_notification = gateway.webhook_testing.sample_notification(
        kind,
        fake_id
    )
    return sample_notification['bt_signature'],sample_notification['bt_payload']

def dummy_webhook_body_with_param(bt_id,kind):
    sample_notification = gateway.webhook_testing.sample_notification(
        kind,
        bt_id
    )
    return sample_notification['bt_signature'], sample_notification['bt_payload']

def gen_dummy_webhooks():
    l = [
        # ['5f11361199fd1346b7396d53',braintree.WebhookNotification.Kind.SubscriptionChargedSuccessfully],
        ['5f11361199fd1346b7396d53', braintree.WebhookNotification.Kind.SubscriptionChargedUnsuccessfully],
        # ['5f11362599fd1346b7396d55', braintree.WebhookNotification.Kind.SubscriptionWentPastDue],
        # ['5f11475ff011688b2b300f88', braintree.WebhookNotification.Kind.SubscriptionChargedUnsuccessfully],
        # ['5f11475ff011688b2b300f88', braintree.WebhookNotification.Kind.SubscriptionCanceled],
    ]
    res =[]
    for x in l:
        item = dummy_webhook_body_with_param(*x)
        res.append(item)
    return res

def test_dummy_webhook():
    bt_signature,bt_payload = dummy_webhook_body()
    handle_webhook(bt_signature,bt_payload)

def gen_dummy_webhook():
    webhooks_nots = gen_dummy_webhooks()
    for noti in webhooks_nots:
        bt_signature, bt_payload = noti[0],noti[1]
        timestamp_util.timing(handle_webhook)(bt_signature, bt_payload)


def test_monthly():
    monthly_jobs()
    pass

def test_daily():
    daily_jobs()
    pass
