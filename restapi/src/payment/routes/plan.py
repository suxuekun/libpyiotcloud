from functools import wraps

from flask_restful import Resource

from payment.services import plan_service
from shared.simple_api.resource import BaseResource, ListMixin, GetMixin
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
    pass

class PlanListResource(Resource,ListMixin):
    service = plan_service
    wrapper_class = IotHttpResponseWrapper
    pass