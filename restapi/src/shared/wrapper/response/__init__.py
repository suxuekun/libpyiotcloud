from shared.utils.json_util import to_json
class HttpResponseWrapper():
    def to_json(self):
        return to_json(self.__dict__);

class IotHttpResponseWrapper(HttpResponseWrapper):
    def __init__(self,data = None,status=None,message=None):
        self.status = status or "OK"
        self.message = message or ""
        self.data = data
