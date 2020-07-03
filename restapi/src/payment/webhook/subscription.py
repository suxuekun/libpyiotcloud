'''
braintree.WebhookNotification.Kind.SubscriptionCanceled
braintree.WebhookNotification.Kind.SubscriptionChargedSuccessfully
braintree.WebhookNotification.Kind.SubscriptionChargedUnsuccessfully
braintree.WebhookNotification.Kind.SubscriptionWentActive
braintree.WebhookNotification.Kind.SubscriptionWentPastDue
# braintree.WebhookNotification.Kind.SubscriptionExpired
# braintree.WebhookNotification.Kind.SubscriptionTrialEnded
'''
from payment.services import subscription_service


def subscription_canceled(webhook_notification):
    bt_sub_id = webhook_notification.subscription.id
    subscription_service.cancel_subscription_by_bt_id(bt_sub_id)
    pass

def subscription_charge_success(webhook_notification):
    bt_sub_id = webhook_notification.subscription.id
    # subscription_service.cancel_subscription_by_bt_id(bt_sub_id)
    pass

def subscription_charge_fail(webhook_notification):
    bt_sub_id = webhook_notification.subscription.id
    # TODO
    pass
def subscription_went_active(webhook_notification):
    bt_sub_id = webhook_notification.subscription.id
    # TODO
    pass
def subscription_pass_due(webhook_notification):
    bt_sub_id = webhook_notification.subscription.id
    # TODO
    pass