from flask_restful import Resource

from payment.dtos.checkout import CheckoutDTO
from payment.services import payment_service
from shared.middlewares.request import informations
from shared.middlewares.request.informations import requestWrap, get_entityname_query
from shared.middlewares.request.permission.base import getRequest
from shared.simple_api.resource import BaseResource
from shared.wrapper.response import IotHttpResponseWrapper


class CheckoutResource(Resource,BaseResource):
    FILTER = requestWrap(get_entityname_query)
    service = payment_service
    wrapper_class = IotHttpResponseWrapper
    POSTDTO = CheckoutDTO
    def post(self):
        request = getRequest()
        data = request.args
        query = informations.get_entityname_query(request)

        pass