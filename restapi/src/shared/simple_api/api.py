from flask_restful import Resource
from shared.simple_api.resource import GetMixin, PutMixin, DeleteMixin, ListMixin, \
    PostMixin

class BaseApi():
    def __init__(self,decorators=None,wrapper_class=None,filter=None,*args,**kwargs):
        self._id_base = []
        self._list_base = []
        self._id_decorators = {}
        self._list_decorators = {}
        self._decorators = decorators or {}
        self._wrapper_class = wrapper_class
        self._filter = filter

class ApiMixin(BaseApi):
    pass

class GetApiMixin(ApiMixin):
    GET = GetMixin
    def __init__(self,*args,**kwargs):
        super(GetApiMixin,self).__init__(*args,**kwargs)
        self._id_base.append(self.GET)
        self._id_decorators['get'] = self._decorators.get('get') or []

class PUTApiMixin(ApiMixin):
    PUT = PutMixin
    def __init__(self,*args,**kwargs):
        super(PUTApiMixin,self).__init__(*args,**kwargs)
        self._id_base.append(self.PUT)
        self._id_decorators['put'] = self._decorators.get('put') or []

class DeleteApiMixin(ApiMixin):
    DELETE = DeleteMixin
    def __init__(self,*args,**kwargs):
        super(DeleteApiMixin,self).__init__(*args,**kwargs)
        self._id_base.append(self.DELETE)
        self._id_decorators['delete'] = self._decorators.get('delete') or []

class ListApiMixin(ApiMixin):
    LIST = ListMixin
    def __init__(self,*args,**kwargs):
        super(ListApiMixin,self).__init__(*args,**kwargs)
        self._list_base.append(self.LIST)
        self._list_decorators['get'] = self._decorators.get('list') or []

class PostApiMixin(ApiMixin):
    POST = PostMixin
    def __init__(self,*args,**kwargs):
        super(PostApiMixin,self).__init__(*args,**kwargs)
        self._list_base.append(self.POST)
        self._list_decorators['post'] = self._decorators.get('post') or []

class BaseSimpleApi(BaseApi):
    def __init__(self,api,prefix,service,*args,**kwargs):
        super(BaseSimpleApi,self).__init__(*args,**kwargs)
        self._api = api
        self._url = self._prefix = prefix
        self._service = service
        self._construct()
        self._add_resource()

    def _construct(self):
        self._id_resource = None
        self._list_resource = None
        if self._id_base:
            self._id_base.append(Resource)
            self._id_resource = type('Resource_'+self._url+'_id', tuple(self._id_base), {
                # constructor
                # data members
                'method_decorators': self._id_decorators,
                'service':self._service,
                # member functions
                "FILTER": self._filter,
                'wrapper_class': self._wrapper_class,
            })
        if self._list_base:
            self._list_base.append(Resource)
            self._list_resource = type('Resource_' + self._url + '_list', tuple(self._list_base), {
                # constructor
                # data members
                'method_decorators':self._list_decorators,
                'service': self._service,
                # member functions
                "FILTER": self._filter,
                'wrapper_class': self._wrapper_class
            })
    def _add_resource(self):
        if (self._id_resource):
            self._api.add_resource(self._id_resource, '/'+self._url+'/<id>/')
        if (self._list_resource):
            self._api.add_resource(self._list_resource, '/'+self._url+'/')

class SimpleApi(BaseSimpleApi):
    pass

class FullApi(SimpleApi,GetApiMixin,PostApiMixin,ListApiMixin,PUTApiMixin,DeleteApiMixin):
    pass

class ReadApi(SimpleApi,GetApiMixin,ListApiMixin):
    pass
