from payment.core import payment_client
from payment.models.webhook import Webhook, WebhookStatus
from payment.repositories import webhook_repo
from payment.webhook import process_webhook


def update_subscriptions_payment():
    webhooks = [Webhook(x) for x in webhook_repo.gets({'status':WebhookStatus.PENDING},sort={'timestamp':-1})]
    res = []
    for webhook in webhooks:
        item = process_webhook(webhook)
        res.append(item)
    return res