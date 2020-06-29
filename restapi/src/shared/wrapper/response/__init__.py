from flask import Response

from shared.utils.json_util import to_json
class HttpResponseWrapper():
    def to_json(self):
        if isinstance(self.data,bool):
            del self.data
        return to_json(self.__dict__);
    def to_json_response(self):
        return Response(self.to_json(),mimetype='application/json')


class IotHttpResponseWrapper(HttpResponseWrapper):
    def __init__(self,data = None,status=None,message=None):
        self.status = status or "OK"
        self.message = message or ""
        self.data = data

    def success(self,message=None):
        self.status = 'OK'
        self.message = message or self.message
        return self.to_json_response()

    def fail(self,message=None):
        self.status = "NG"
        self.message = message or self.message
        return self.to_json_response()

