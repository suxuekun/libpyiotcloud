from flask_restful import Resource

from shared.middlewares.request.permission.login import login_required
from shared.wrapper.response import IotHttpResponseWrapper

class TestAPI(Resource):
    # permission for this , you can add your cusomized premissions or checkings
    method_decorators = {
        'get':[login_required()]
    }
    def get(self,id):
        res = {
            'api':'get test',
            'id':id
        }
        return IotHttpResponseWrapper(res).to_json_response()
    def put(self,id):
        res = {
            'api': 'put test',
            'id': id
        }
        return IotHttpResponseWrapper(res).to_json_response()
    def delete(self,id):
        res = {
            'api': 'del test',
            'id': id
        }
        return IotHttpResponseWrapper(res).to_json_response()
class TestAPIList(Resource):
    def get(self):
        res = {
            'api': 'get list',
        }
        return IotHttpResponseWrapper(res).to_json_response()
    def post(self):
        res = {
            'api': 'create one',
        }
        return IotHttpResponseWrapper(res).to_json_response()