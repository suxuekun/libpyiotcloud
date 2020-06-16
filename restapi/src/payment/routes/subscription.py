from flask_restful import Resource
from payment.services import subscription_service
from shared.middlewares.request import informations
from shared.middlewares.request.permission.base import getRequest
from shared.simple_api.resource import GetMixin, throw_bad_request, BaseResource
from shared.wrapper.response import IotHttpResponseWrapper


class SubscriptionResource(Resource,GetMixin):
    service = subscription_service
    wrapper_class = IotHttpResponseWrapper

class SubscriptionListResource(Resource,BaseResource):
    service = subscription_service
    wrapper_class = IotHttpResponseWrapper
    @throw_bad_request
    def get(self):
        request = getRequest()
        query = informations.get_entityname_query(request)
        data = self.service.get_current_subscriptions(query)
        res = [self.to_api_data(x) for x in data]
        return self.to_result(res)