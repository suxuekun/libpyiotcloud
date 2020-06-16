from flask_restful import Resource

from payment.services import payment_service
from shared.middlewares.request import informations
from shared.middlewares.request.informations import get_entityname_query, requestWrap
from shared.middlewares.request.permission.base import getRequest
from shared.middlewares.response import make_error_response, http4xx
from shared.simple_api.resource import BaseResource, throw_custome_error_request
from shared.wrapper.response import IotHttpResponseWrapper


class ProrateResource(Resource,BaseResource):
    FILTER = requestWrap(get_entityname_query)
    service = payment_service
    wrapper_class = IotHttpResponseWrapper
    # @throw_custome_error_request()
    def get(self):
        request = getRequest()
        old_plan_id = request.args.get('old_plan_id')
        new_plan_id = request.args.get('new_plan_id')
        promocode = request.args.get('promocode')
        query = self.filtered()
        data = self.service.prorate(old_plan_id=old_plan_id,new_plan_id=new_plan_id,query=query,promocode=promocode)
        res = self.to_api_data(data)
        return self.to_result(res)

