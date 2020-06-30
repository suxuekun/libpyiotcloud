from functools import wraps

from flask_api import status
from flask_restful import Resource

from payment.dtos.plan import PlanDTO
from payment.services import plan_service
from shared.middlewares.request.informations import requestWrap, get_entityname_query
from shared.middlewares.response import http5xx, make_custom_error_response
from shared.simple_api.resource import BaseResource, ListMixin, GetMixin, throw_bad_request
from shared.wrapper.response import IotHttpResponseWrapper

# example of plan
# class PlanApi(FullApi):
#     service = plan_service
#     def __init__(self,api,prefix):
#         self._api = api
#         super(PlanApi,self).__init__(
#                 api=self._api,
#                 prefix=prefix,
#                 service=self.service,
#                 wrapper_class=IotHttpResponseWrapper,
#                 decorators={# example of decorators , can help handle permission
#                     # 'get':[],
#                     # 'list':[],
#                 }
#             )

class PlanResource(Resource,GetMixin):
    service = plan_service
    wrapper_class = IotHttpResponseWrapper
    ENTITYDTO = PlanDTO
    pass

class PlanListResource(Resource,ListMixin):
    service = plan_service
    wrapper_class = IotHttpResponseWrapper
    ENTITYDTO = PlanDTO
    pass

class PlanReloadResource(Resource,BaseResource):
    service = plan_service
    wrapper_class = IotHttpResponseWrapper
    @throw_bad_request
    def get(self):
        data = self.service.reload()
        res = self.to_api_data(data)
        if res:
            return self.to_result(res,message="plan reload success")
        else:
            return make_custom_error_response({'status': 'NG', 'message': 'Can Not Reload Plans From Braintree'},status.HTTP_503_SERVICE_UNAVAILABLE)
