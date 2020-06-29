from flask_restful import Resource

from payment.dtos.promocode import PromoCodeQueryDTO, PromoCodeVerifyDTO
from payment.services import promocode_service
from shared.middlewares.request import informations
from shared.middlewares.request.informations import get_entityname_query, requestWrap
from shared.middlewares.request.permission.base import getRequest
from shared.middlewares.response import make_error_response, http4xx, make_custom_error_response
from shared.simple_api.resource import ListMixin, BaseResource, \
    throw_custome_error_request, throw_bad_request
from shared.wrapper.response import IotHttpResponseWrapper

class PromocodeResource(Resource,BaseResource):
    FILTER = requestWrap(get_entityname_query)
    service = promocode_service
    wrapper_class = IotHttpResponseWrapper
    # @throw_custome_error_request()
    # def get(self, code):
    #     data = self.service.get_one({'code':code})
    #     # print(code,data)
    #     if data:
    #         res = self.to_api_data(data)
    #         return self.to_result(res)
    #     else:
    #         return make_error_response(http4xx.DATA_NOT_FOUND)

class PromocodeListResource(Resource,BaseResource):
    FILTER = requestWrap(get_entityname_query)
    service = promocode_service
    wrapper_class = IotHttpResponseWrapper
    POSTDTO = PromoCodeQueryDTO

    @throw_bad_request
    def get(self):
        request = getRequest()
        parameters = request.args
        print(parameters)
        dto = self.to_valid_request_data(parameters)
        # username = informations.get_username(request)
        created = informations.get_user_created_timestamp(request)
        datalist = self.service.list_valid_code(dto.subscription_id,dto.plan_id,created)
        res = [self.to_api_data(i) for i in datalist]
        return self.to_result(res)

class PromocodeVerifyResource(Resource,BaseResource):
    FILTER = requestWrap(get_entityname_query)
    service = promocode_service
    wrapper_class = IotHttpResponseWrapper
    POSTDTO = PromoCodeVerifyDTO
    def post(self):
        request = getRequest()
        raw = request.get_json()
        dto = self.to_valid_request_data(raw)
        created = informations.get_user_created_timestamp(request)
        res = self.service.verify(dto.code,dto.subscription_id, dto.plan_id, created)
        if res:
            return self.to_result(self.to_api_data(res))
        else:
            return make_custom_error_response({
                'status':'NG',
                'message':"NO CODE FOUND OR CODE NOT AVALIABLE FOR THIS PLAN"
            },404)