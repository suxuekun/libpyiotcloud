from flask_restful import Resource

from payment.dtos.checkout import CheckoutDTO
from payment.services import payment_service, promocode_service
from shared.middlewares.request import informations
from shared.middlewares.request.informations import requestWrap, get_entityname_query
from shared.middlewares.request.permission.base import getRequest
from shared.middlewares.response import make_custom_error_response, make_error_response, http4xx
from shared.simple_api.resource import BaseResource, throw_custome_error_request
from shared.wrapper.response import IotHttpResponseWrapper


class CheckoutResource(Resource,BaseResource):
    FILTER = requestWrap(get_entityname_query)
    service = payment_service
    wrapper_class = IotHttpResponseWrapper
    POSTDTO = CheckoutDTO
    @throw_custome_error_request()
    def post(self):
        data = None
        try:
            request = getRequest()
            req_data = request.get_json()
            username = informations.get_entityname(request)
            # query = informations.get_entityname_query(request)
            dto =self.to_valid_request_data(req_data)
            dto.validate()
        except Exception as e:
            print(e)
            return make_error_response(http4xx.BAD_REQUEST)

        # print(dto.to_primitive())
        try:
            data = self.service.checkout(username,dto.nonce,dto.items);
        except Exception as e:
            print(e)
            return make_custom_error_response({'status': 'NG', 'message': 'check out fail with braintree'}, 503)
        if data:
            res = self.to_api_data(data)
            return self.to_result(res)
        else:
            return make_custom_error_response({'status':'NG','message':'data format fail'},503)

class CancelSubscriptionResource(Resource,BaseResource):
    FILTER = requestWrap(get_entityname_query)
    service = payment_service
    wrapper_class = IotHttpResponseWrapper
    def post(self):
        request = getRequest()
        req_data = request.get_json()
        subscription_id = req_data.get('subscription_id')
        data = self.service.cancel_subscription(subscription_id)
        if data:
            res = self.to_api_data(data)
            return self.to_result(res)
        else:
            return make_custom_error_response({'status': 'NG', 'message': 'check out fail'}, 400)
