from flask_restful import Resource

from payment.dtos.subscription import SubscriptionDTO
from payment.services import subscription_service
from shared.client.clients.database_client import db_client
from shared.middlewares.request import informations
from shared.middlewares.request.informations import requestWrap, get_entityname_query
from shared.middlewares.request.permission.base import getRequest
from shared.middlewares.response import make_error_response, http4xx
from shared.simple_api.resource import GetMixin, throw_bad_request, BaseResource
from shared.wrapper.response import IotHttpResponseWrapper


class SubscriptionResource(Resource,GetMixin):
    FILTER = requestWrap(get_entityname_query)
    service = subscription_service
    wrapper_class = IotHttpResponseWrapper
    ENTITYDTO = SubscriptionDTO

    @throw_bad_request
    def get(self, id):
        data = self.service.get(id)
        res = self.to_api_data(data)
        if res:
            return self.to_result(res)
        else:
            return make_error_response(http4xx.DATA_NOT_FOUND)

class SubscriptionListResource(Resource,BaseResource):
    FILTER = requestWrap(get_entityname_query)
    service = subscription_service
    wrapper_class = IotHttpResponseWrapper
    ENTITYDTO = SubscriptionDTO
    @throw_bad_request
    def get(self):
        request = getRequest()
        query = informations.get_entityname_query(request)
        data = self.service.get_current_subscriptions(query)
        res = [self.to_api_data(x) for x in data]
        return self.to_result(res)