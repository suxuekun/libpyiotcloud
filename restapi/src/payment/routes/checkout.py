from flask_restful import Resource

from payment.dtos.checkout import CheckoutDTO
from payment.services import payment_service
from shared.middlewares.request import informations
from shared.middlewares.request.informations import requestWrap, get_entityname_query
from shared.middlewares.request.permission.base import getRequest
from shared.middlewares.response import make_custom_error_response
from shared.simple_api.resource import BaseResource
from shared.wrapper.response import IotHttpResponseWrapper


class CheckoutResource(Resource,BaseResource):
    FILTER = requestWrap(get_entityname_query)
    service = payment_service
    wrapper_class = IotHttpResponseWrapper
    POSTDTO = CheckoutDTO
    def post(self):
        request = getRequest()
        data = request.get_json()
        print(data)
        username = informations.get_entityname(request)
        # query = informations.get_entityname_query(request)
        dto =self.to_valid_request_data(data)
        dto.validate()
        print(dto.to_primitive())
        data = self.service.checkout(username,dto.nonce,dto.items)
        if data:
            res = self.to_api_data(data)
            return self.to_result(res)
        else:
            return make_custom_error_response({'status':'NG','message':'check out fail'},400)

class CancelSubscriptionResource(Resource,BaseResource):
    FILTER = requestWrap(get_entityname_query)
    service = payment_service
    wrapper_class = IotHttpResponseWrapper

    def post(self):
        request = getRequest()
        data = request.get_json()
        print(data)
        subscription_id = data.get('subscription_id')
        data = self.service.cancel_subscription(subscription_id)
        if data:
            res = self.to_api_data(data)
            return self.to_result(res)
        else:
            return make_custom_error_response({'status': 'NG', 'message': 'check out fail'}, 400)
