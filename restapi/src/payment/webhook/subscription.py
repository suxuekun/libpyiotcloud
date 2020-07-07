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

from payment.services import subscription_service


def subscription_canceled(webhook_notification):
    bt_sub_id = webhook_notification.subscription.id
    return subscription_service.cancel_subscription_by_bt_id(bt_sub_id)


def subscription_charge_success(webhook_notification):
    bt_sub_id = webhook_notification.subscription.id
    return subscription_service.subscription_recurring_paid_by_bt_id(bt_sub_id)

def subscription_charge_fail(webhook_notification):
    bt_sub_id = webhook_notification.subscription.id
    return subscription_service.subscription_recurring_fail_by_bt_id(bt_sub_id)

def subscription_went_active(webhook_notification):
    bt_sub_id = webhook_notification.subscription.id
    #TODO
    # return subscription_service.what_to_do_on_active(bt_sub_id)

def subscription_pass_due(webhook_notification):
    bt_sub_id = webhook_notification.subscription.id
    return subscription_service.subscription_recurring_overdue_by_bt_id(bt_sub_id)

HANDLERS={
    braintree.WebhookNotification.Kind.SubscriptionCanceled:subscription_canceled,
    braintree.WebhookNotification.Kind.SubscriptionChargedSuccessfully:subscription_charge_success,
    braintree.WebhookNotification.Kind.SubscriptionChargedUnsuccessfully:subscription_charge_fail,
    braintree.WebhookNotification.Kind.SubscriptionWentActive:subscription_went_active,
    braintree.WebhookNotification.Kind.SubscriptionWentPastDue:subscription_pass_due,
}