from flask_restful import Resource

from payment.services import promocode_service
from shared.middlewares.request.informations import get_entityname_query, requestWrap
from shared.middlewares.response import make_error_response, http4xx
from shared.simple_api.resource import ListMixin, BaseResource, \
    throw_custome_error_request
from shared.wrapper.response import IotHttpResponseWrapper

class PromocodeResource(Resource,BaseResource):
    FILTER = requestWrap(get_entityname_query)
    service = promocode_service
    wrapper_class = IotHttpResponseWrapper

    @throw_custome_error_request()
    def get(self, code):
        data = self.service.get_one({'code':code})
        # print(code,data)
        if data:
            res = self.to_api_data(data)
            return self.to_result(res)
        else:
            return make_error_response(http4xx.DATA_NOT_FOUND)

class PromocodeListResource(Resource,ListMixin):
    FILTER = requestWrap(get_entityname_query)
    service = promocode_service
    wrapper_class = IotHttpResponseWrapper
    pass