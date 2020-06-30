from flask_restful import Resource

from payment.dtos.transaction import TransactionDTO
from payment.services import transaction_service
from shared.middlewares.request.informations import requestWrap, get_entityname_query
from shared.simple_api.resource import BaseResource, ListMixin, GetMixin
from shared.wrapper.response import IotHttpResponseWrapper

class TransactionResource(Resource,GetMixin):
    service = transaction_service
    wrapper_class = IotHttpResponseWrapper
    ENTITYDTO = TransactionDTO
    pass

class TransactionListResource(Resource,ListMixin):
    FILTER = requestWrap(get_entityname_query)
    service = transaction_service
    wrapper_class = IotHttpResponseWrapper
    ENTITYDTO = TransactionDTO
    pass