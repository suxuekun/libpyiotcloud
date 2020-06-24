import pytz
from flask import Response

from payment.core import payment_client
from payment.models.webhook import Webhook
from payment.repositories import webhook_repo
from payment.webhook.test import dummy_webhook_body
from shared.middlewares.request.permission.base import getRequest


HANDLERS = {}

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
        webhook_repo.create(webhook.to_primitive())
        return True
    except Exception as e:
        print (e)
        return None
    # '''
    # if handle immediately
    # '''
    # handler = HANDLERS.get(kind)
    # if handler:
    #     res = handler(webhook_notification)
    #     return res
    # return None

def test_dummy_webhook():
    bt_signature,bt_payload = dummy_webhook_body()
    handle_webhook(bt_signature,bt_payload)

