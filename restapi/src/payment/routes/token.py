from flask_restful import Resource

from payment.services import payment_service
from shared.middlewares.request import informations
from shared.middlewares.request.informations import requestWrap, get_entityname_query
from shared.middlewares.request.permission.base import getRequest
from shared.middlewares.response import http5xx, make_error_response
from shared.simple_api.resource import BaseResource
from shared.wrapper.response import IotHttpResponseWrapper


class TokenResource(Resource,BaseResource):
    FILTER = requestWrap(get_entityname_query)
    service = payment_service
    wrapper_class = IotHttpResponseWrapper
    def get(self):
        request = getRequest()
        username = informations.get_entityname(request)
        token = payment_service.get_client_token(username)
        if token:
            res = self.to_api_data({'token':token})
            return self.to_result(res)
        else:
            return make_error_response(http5xx.BRAINTREE_TOKEN_ERROR)