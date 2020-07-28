'''
braintree.WebhookNotification.Kind.SubscriptionCanceled
braintree.WebhookNotification.Kind.SubscriptionChargedSuccessfully
braintree.WebhookNotification.Kind.SubscriptionChargedUnsuccessfully
braintree.WebhookNotification.Kind.SubscriptionWentActive
braintree.WebhookNotification.Kind.SubscriptionWentPastDue
# braintree.WebhookNotification.Kind.SubscriptionExpired
# braintree.WebhookNotification.Kind.SubscriptionTrialEnded
'''
import braintree

from payment.services import subscription_service, transaction_service
from shared.utils import timestamp_util


def subscription_canceled(webhook_notification):
    print('handle subscription canceled')
    try:
        bt_sub_id = webhook_notification.subscription.id
        subscription_service.cancel_subscription_by_bt_id(bt_sub_id)
        return True
    except Exception as e:
        print(e)
        return False


def subscription_charge_success(webhook_notification):
    print('handle subscription success')
    try:
        timestamp = timestamp_util.reset_utc_timestamp(webhook_notification.timestamp)
        bt_sub_id = webhook_notification.subscription.id
        subscription = subscription_service.subscription_recurring_paid_by_bt_id(bt_sub_id)
        bt_sub_last_transaction = webhook_notification.subscription.transactions[0]
        tid = transaction_service.create_record_by_btraintree_transaction_object(bt_sub_last_transaction, subscription,timestamp)
        subscription.current.transactionID = tid
        subscription_service.update(subscription._id,subscription)
        return True
    except Exception as e:
        print(e)
        return False

def subscription_charge_fail(webhook_notification):
    print('handle subscription fail')
    try:
        timestamp = timestamp_util.reset_utc_timestamp(webhook_notification.timestamp)
        bt_sub_id = webhook_notification.subscription.id
        print(0)
        subscription = subscription_service.subscription_recurring_fail_by_bt_id(bt_sub_id)
        print(1)
        bt_sub_last_transaction = webhook_notification.subscription.transactions[0]
        print(2)
        tid = transaction_service.create_record_by_btraintree_transaction_object(bt_sub_last_transaction, subscription,timestamp,fail=True)
        print(3)
        subscription.current.transactionID = tid
        print(4)
        subscription_service.update(subscription._id,subscription)
        return True
    except Exception as e:
        print(e)
        return False

def subscription_went_active(webhook_notification):
    bt_sub_id = webhook_notification.subscription.id
    #TODO
    # no need record went active , went active means the first time charge recurring billing
    # return subscription_service.what_to_do_on_active(bt_sub_id)

def subscription_pass_due(webhook_notification):
    print('handle subscription past_due')
    bt_sub_id = webhook_notification.subscription.id
    return subscription_service.subscription_recurring_overdue_by_bt_id(bt_sub_id)

HANDLERS={
    braintree.WebhookNotification.Kind.SubscriptionCanceled:subscription_canceled,
    braintree.WebhookNotification.Kind.SubscriptionChargedSuccessfully:subscription_charge_success,
    braintree.WebhookNotification.Kind.SubscriptionChargedUnsuccessfully:subscription_charge_fail,
    # braintree.WebhookNotification.Kind.SubscriptionWentActive:subscription_went_active,
    braintree.WebhookNotification.Kind.SubscriptionWentPastDue:subscription_pass_due,
}