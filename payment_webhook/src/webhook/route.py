from flask import Blueprint, Response

from shared.wrapper.response import IotHttpResponseWrapper
from webhook import webbhook, test_dummy_webhook, list_webhooks, list_raw_webhooks

webhook_blueprint = Blueprint('webhook_blueprint', __name__)

'''
-----------------------
webhook
-----------------------
'''
@webhook_blueprint.route("/payment/", methods=['POST'],endpoint="webhooks")
def payment_webhook():
    return webbhook()

@webhook_blueprint.route("/test/", methods=['GET'],endpoint="test")
def test():
    return IotHttpResponseWrapper().success('test ok')

'''
TEST
'''
@webhook_blueprint.route("/test_dummy_webhook/", methods=['GET'],endpoint="test_dummy_webhook")
def test_dummy_webhook_api():
    test_dummy_webhook()
    return Response(status=200)

@webhook_blueprint.route("/list/", methods=['GET'],endpoint="list")
def list():
    data = list_webhooks()
    return IotHttpResponseWrapper(data=data).to_json_response()

@webhook_blueprint.route("/list_raw/", methods=['GET'],endpoint="list_raw")
def list_raw():
    data = list_raw_webhooks()
    return IotHttpResponseWrapper(data=data).to_json_response()




