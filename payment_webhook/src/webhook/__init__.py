import flask
import pytz
from flask import Response

from core import payment_client
from shared.client.db.mongo.default import DefaultMongoDB
from webhook.models import Webhook
from webhook.repository import WebhookRepository
from webhook.test import dummy_webhook_body

payment_db = DefaultMongoDB()#TestMongoDB()
WEBHOOK = 'payment_webhook_test'
webhook_repo = WebhookRepository(payment_db,WEBHOOK)

def reset_utc_timestamp(dt):
    d = dt.replace(tzinfo=pytz.UTC)
    return int(d.timestamp())

def webbhook():
    request = flask.request
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

        webhook = Webhook(data,strict=False)
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

def parse_webhook(dic):
    # print(dic)
    webhook_notification = payment_client.gateway.webhook_notification.parse(dic['bt_signature'], dic['bt_payload'])
    print(webhook_notification)
    res = {}
    for key in webhook_notification.__dict__:
        item = webhook_notification.__dict__[key]
        if (hasattr(item,'__dict__')):
            # res[key] = item.__dict__
            pass
        else:
            res[key] = item
    return res


def list_webhooks():
    print('list web hook')
    return [parse_webhook(x) for x in webhook_repo.gets()]

def list_raw_webhooks():
    return webhook_repo.gets()

def test_dummy_webhook():
    bt_signature,bt_payload = dummy_webhook_body()
    handle_webhook(bt_signature,bt_payload)