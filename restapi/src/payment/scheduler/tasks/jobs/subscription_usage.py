from payment.services import subscription_service


def reset_subscriptions_usage():
    subscriptions = subscription_service.list()
    for subscription in subscriptions:
        subscription_service.subscription_reset_usage(subscription)
    pass