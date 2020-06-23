import pytz
from flask import Response

from payment.core import payment_client
from shared.middlewares.request.permission.base import getRequest


HANDLERS = {}

def reset_utc_timestamp(dt):
    d = dt.replace(tzinfo=pytz.UTC)
    return d.timestamp()

def webbhook():
    request = getRequest()
    webhook_notification = payment_client.gateway.webhook_notification.parse(
        str(request.form['bt_signature']),
        request.form['bt_payload']
    )
    try:
        res = handle_webhook(webhook_notification)
        if res:
            return Response(status=200)
        else:
            return Response(status=404)
    except Exception as e:
        print (e)
        return Response(status=500)




    # Example values for webhook notification properties
    print(webhook_notification.kind)  # "subscription_went_past_due"
    print(webhook_notification.timestamp)  # "Sun Jan 1 00:00:00 UTC 2012"
    pass

def handle_webhook(webhook_notification):
    kind = webhook_notification.kind
    timestamp = reset_utc_timestamp(webhook_notification.timestamp)
    print(kind,timestamp)
    '''
    or maybe save it to db first then handle later 
    '''
    handler = HANDLERS.get(kind)
    if handler:
        res = handler(webhook_notification)
        return res
    return None