from flask_restful import Resource

from payment.dtos.prorate import ProrateQueryDTO
from payment.services import payment_service
from shared.middlewares.request import informations
from shared.middlewares.request.informations import get_entityname_query, requestWrap
from shared.middlewares.request.permission.base import getRequest
from shared.middlewares.response import make_error_response, http4xx, make_custom_error_response
from shared.simple_api.resource import BaseResource, throw_custome_error_request, throw_bad_request
from shared.wrapper.response import IotHttpResponseWrapper


class ProrateResource(Resource,BaseResource):
    FILTER = requestWrap(get_entityname_query)
    service = payment_service
    wrapper_class = IotHttpResponseWrapper
    POSTDTO = ProrateQueryDTO
    # @throw_custome_error_request()
    @throw_bad_request
    def get(self):
        request = getRequest()
        # old_plan_id = request.args.get('old_plan_id')
        # new_plan_id = request.args.get('new_plan_id')
        # promocode = request.args.get('promocode')
        parameters = request.args
        dto = self.to_valid_request_data(parameters)
        # created = informations.get_user_created_timestamp(request)
        query = self.filtered()
        print('wtf')
        data,message = self.service.prorate(old_plan_id=dto.old_plan_id,new_plan_id=dto.new_plan_id,query=query,promocode=dto.promocode)
        res = self.to_api_data(data)
        if data:
            return self.to_result(res,message=message)
        elif message:
            return make_custom_error_response({
                'status': 'NG',
                'message': message
            }, 404)
        else:
            return make_error_response(http4xx.BAD_REQUEST)


