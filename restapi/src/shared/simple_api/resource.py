class BaseResource():
    FILTER = None
    service = None
    wrapper_class = None
    def filtered(self):
        return
    def to_result(self,res):
        if self.wrapper_class:
            return self.wrapper_class(res).to_json_response()
        return res

class GetMixin(BaseResource):
    def get(self,id):
        res = self.service.get(id)
        return self.to_result(res)


class PostMixin(BaseResource):
    def post(self,entity):
        res = self.service.create(entity)
        if (res):
            return self.to_result(res),201
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
    def put(self,entity):
        res = self.service.update(entity)
        return self.to_result(res)

class DeleteMixin(BaseResource):
    def delete(self,id):
        res = self.service.delete(id)
        return self.to_result(res)

class BaseListResource(ListMixin,PostMixin):
    pass

class BaseIdResource(GetMixin,PutMixin,DeleteMixin):
    pass





