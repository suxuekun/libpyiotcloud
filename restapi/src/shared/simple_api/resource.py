import flask
from shared.middlewares.response import make_error_response, make_custom_error_response

class BaseResource():
    FILTER = None
    service = None
    wrapper_class = None
    def filtered(self):
        return
    def to_result(self,res,status="OK"):
        if self.wrapper_class:
            return self.wrapper_class(res,status=status).to_json_response()
        return res

class GetMixin(BaseResource):
    def get(self,id):
        res = self.service.get(id)
        if res:
            return self.to_result(res)
        else:
            return make_custom_error_response({'status': 'NG', 'message': 'data not found'}, 404)

class PostMixin(BaseResource):
    def post(self,entity):
        res = self.service.create(entity)
        if (res):
            return self.to_result(res)
        else:
            return

class ListMixin(BaseResource):
    def get(self,filter=None):
        list_filter = {}
        if (filter):
            list_filter = {}.update(filter)
        if (self.FILTER):
            list_filter = filter.update(self.FILTER())
        if (list_filter == {}):
            list_filter = None
        res = self.service.list(list_filter)
        return self.to_result(res)

class PutMixin(BaseResource):
    def put(self,id):
        entity = flask.request.get_json()
        res = self.service.update(id,entity)
        return self.to_result(res)

class DeleteMixin(BaseResource):
    def delete(self,id):
        res = self.service.delete(id)
        return self.to_result(res)

class BaseListResource(ListMixin,PostMixin):
    pass

class BaseIdResource(GetMixin,PutMixin,DeleteMixin):
    pass





