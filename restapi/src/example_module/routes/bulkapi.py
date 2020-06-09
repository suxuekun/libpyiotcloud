from functools import wraps

from example_module.services.bulk_example_service import buld_service
from shared.simple_api.api import FullApi
from shared.wrapper.response import IotHttpResponseWrapper

# permission check example
def deco(f):
    @wraps(f)
    def atholder(*args, **kwargs):
        ret = f(*args, **kwargs)
        return ret
    return atholder
'''
example of make 5 common api in one go

you need a service to assign to a api class

and each api map to each functions in the service
'''

class BulkApi(FullApi):# builkApi(SimpleApi,GetApiMixin,ListApiMixin): assemble your own api needed with SimpleApi + mixins
    service = buld_service
    def __init__(self,api,prefix):
        self._api = api
        super(BulkApi,self).__init__(
                api=self._api,
                prefix=prefix,
                service=self.service,
                wrapper_class=IotHttpResponseWrapper,
                decorators={# example of decorators , can help handle permission
                    # 'get':[deco],# add your won deco on each api if needed
                    # 'list':[],
                    #'put': [],
                    #'post': [],
                    #'delete': [],
                }
            )
