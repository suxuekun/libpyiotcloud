from flask_restful import Resource
from payment.services import transaction_service
from shared.simple_api.resource import BaseResource, ListMixin, GetMixin
from shared.wrapper.response import IotHttpResponseWrapper

class TransactionResource(Resource,GetMixin):
    service = transaction_service
    wrapper_class = IotHttpResponseWrapper
    pass

class TransactionListResource(Resource,ListMixin):
    service = transaction_service
    wrapper_class = IotHttpResponseWrapper
    pass