from functools import wraps

import flask
from flask_api.status import HTTP_400_BAD_REQUEST
from schematics import Model

from shared.middlewares.response import make_error_response, make_custom_error_response, http4xx
from shared.utils import dict_util

def throw_custome_error_request(response=None, httpcode=HTTP_400_BAD_REQUEST):
    def atholder(f):
        @wraps(f)
        def func(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as _:
                print(_)
                if (response):
                    make_custom_error_response(response,httpcode)
                else:
                    return make_error_response(http4xx.BAD_REQUEST)
        return func
    return atholder


def throw_bad_request(f):
    @wraps(f)
    def func(*args,**kwargs):
        try:
            return f(*args,**kwargs)
        except Exception as _:
            print(_)
            return make_error_response(http4xx.BAD_REQUEST)
    return func


class BaseResource():
    POSTDTO = None
    ENTITYDTO = None
    FILTER = None
    service = None
    wrapper_class = None
    def _get_default_filter(self):
        print (self.FILTER)
        if self.FILTER:
            if callable(self.FILTER):
                print(self.FILTER())
                return self.FILTER()
            else:
                return self.FILTER
    def filtered(self,query = None):
        list_filter = {}
        dict_util.updates(list_filter,query,self._get_default_filter())
        return list_filter

    def to_result(self,res,status="OK"):
        if self.wrapper_class:
            return self.wrapper_class(res,status=status).to_json_response()
        return res

    def to_valid_request_data(self,raw):
        dtoType = self.POSTDTO or self.ENTITYDTO
        if (dtoType):
            dto = dtoType(raw,strict=False)
            dto.validate()
            return dto.to_model()
            # dto = self.POSTDTO(strict=False).transform(raw).to_primitive()
            # return self.POSTDTO(raw,validate=True).to_primitive()
        else:
            return raw

    def to_api_data(self,model_instance):
        if (self.ENTITYDTO):
            e = self.ENTITYDTO(strict=False)
            e.from_model(model_instance)
            return e.to_primitive()
        else:
            if isinstance(model_instance,Model):
                return model_instance.to_primitive()
            return model_instance


class GetMixin(BaseResource):
    @throw_bad_request
    def get(self,id):
        data = self.service.get(id)
        res = self.to_api_data(data)
        if res:
            return self.to_result(res)
        else:
            return make_error_response(http4xx.DATA_NOT_FOUND)

class PostMixin(BaseResource):
    @throw_bad_request
    def post(self):
        raw = flask.request.get_json()
        dto = self.to_valid_request_data(raw)
        res = self.service.create(dto)
        self.to_result(res)

class ListMixin(BaseResource):
    @throw_bad_request
    def get(self,filter=None):
        query = self.filtered(filter)
        datalist = self.service.list(query)
        res = [self.to_api_data(i) for i in datalist]
        return self.to_result(res)

class PutMixin(BaseResource):
    @throw_bad_request
    def put(self,id):
        raw = flask.request.get_json()
        dto = self.to_valid_request_data(raw)
        res = self.service.update(id,dto)
        return self.to_result(res)

class DeleteMixin(BaseResource):
    @throw_bad_request
    def delete(self,id):
        res = self.service.delete(id)
        return self.to_result(res)

class BaseListResource(ListMixin,PostMixin):
    pass

class BaseIdResource(GetMixin,PutMixin,DeleteMixin):
    pass



