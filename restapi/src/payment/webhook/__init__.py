import pytz
from flask import Response

from payment.core import payment_client
from payment.models.webhook import Webhook, WebhookStatus
from payment.repositories import webhook_repo
from payment.webhook import disbursement, dispute, payment_method, subscription
from payment.webhook.test import dummy_webhook_body
from shared.middlewares.request.permission.base import getRequest


HANDLERS = {}
HANDLERS.update(disbursement.HANDLERS)
HANDLERS.update(dispute.HANDLERS)
HANDLERS.update(payment_method.HANDLERS)
HANDLERS.update(subscription.HANDLERS)

def reset_utc_timestamp(dt):
    d = dt.replace(tzinfo=pytz.UTC)
    return str(int(d.timestamp()))

def webbhook():
    request = getRequest()
    bt_signature = str(request.form['bt_signature']),
    bt_payload = request.form['bt_payload']
    try:
        res = handle_webhook(bt_signature,bt_payload)
        if res:
            return Response(status=200)
        else:
            return Response(status=500)
    except Exception as e:
        print (e)
        return Response(status=500)

def handle_webhook(bt_signature,bt_payload):
    webhook_notification = payment_client.gateway.webhook_notification.parse(bt_signature,bt_payload)
    kind = webhook_notification.kind
    timestamp = reset_utc_timestamp(webhook_notification.timestamp)
    print(kind,timestamp)
    data ={
        'kind':kind,
        'timestamp':timestamp,
        'bt_signature':bt_signature,
        'bt_payload':bt_payload,
    }
    '''
    save it to db first then handle later 
    '''
    try:
        webhook = Webhook(data)
        webhook.validate()
        webhook_id = webhook_repo.create(webhook.to_primitive())
        '''
        fire a handle in another thread
        fire(webhook_id)
        #TODO
        '''
        return webhook_id
    except Exception as e:
        print(e)
        return None

def process_webhook(id):
    webhook = Webhook(webhook_repo.getById(id),strict=False)
    webhook_notification = payment_client.gateway.webhook_notification.parse(webhook.bt_signature, webhook.bt_payload)
    kind = webhook.kind
    handler = HANDLERS.get(kind)
    if handler:
        res = None
        try:
            webhook.status = WebhookStatus.PROCESSING
            res = handler(webhook_notification)
            webhook.status = WebhookStatus.PROCESSED
        except Exception as e:
            print(' process webhook error',e)
        finally:
            webhook_repo.update(webhook._id,webhook.to_primitive())
            return res


    return None

def test_dummy_webhook():
    bt_signature,bt_payload = dummy_webhook_body()
    handle_webhook(bt_signature,bt_payload)

