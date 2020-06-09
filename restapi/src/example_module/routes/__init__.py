from flask import Blueprint , request
from flask_restful import Api

from example_module.routes.bulkapi import BulkApi
from example_module.routes.resource import TestAPI, TestAPIList
from shared.middlewares.request.permission.base import printRequestParams
from shared.middlewares.request.permission.login import login_required

example_blueprint = Blueprint('example_blueprint', __name__)

@example_blueprint.before_request # you need a before request , if you want to apply middleware to all apis in this blueprint
@printRequestParams # this is just for print environment variables in backend console , in production just remove it
# @login_required({'excludes':['example_blueprint.bulk']})  # if need all api have login then add this
# @decorator_example_always_ok   # add other decorator, you can write your own checking follow the example
def pre_request():
    pass

'''
-------------------------
using flask-restful example
it has apis:
-GET      /test/id/
-PUT      /test/id/
-DELETE   /test/id/
-POST     /test/
-GET      /test/

endpoints:( naming --  blueprint.Resource)
example_blueprint.testapi           /test/id/     
example_blueprint.testapilist       /test/  
'''
api =Api(example_blueprint)
api.add_resource(TestAPI, '/test/<id>/')
api.add_resource(TestAPIList,'/test/')



'''
--------------------------
using bulk api on top of flask-restful example
-GET      /bulk/id/
-PUT      /bulk/id/
-DELETE   /bulk/id/
-POST     /bulk/
-GET      /bulk/

endpoints:( naming --  blueprint.url[_id])
example_blueprint.bulk_id           /bulk/id/     
example_blueprint.bulk              /bulk/        
'''

BulkApi(api,prefix="bulk")

'''
--------------------------
raw flask blurprint route

endpoint:( naming -- blueprint.func)
example_blueprint.raw

'''
@example_blueprint.route("/raw/", methods=['GET'])
@login_required()# remember () after login_required, the decorator is login_required(options=None) not login_required
def raw():
    result = 'this is a raw api' # result = someService.someFunc()
    return result

@example_blueprint.route("/raw2/", methods=['GET'])
def raw2():
    result = 'this is a raw api' # result = someService.someFunc()
    return result