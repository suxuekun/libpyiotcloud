from payment.services import subscription_service


def update_subscriptions_monthly():
    subscriptions = subscription_service.list()
    for subscription in subscriptions:
        subscription_service.move_subscription_to_next_month(subscription)
    pass