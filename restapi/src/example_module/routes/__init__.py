from flask import Blueprint , request
from flask_restful import Api

from example_module.routes.bulkapi import BulkApi
from example_module.routes.resource import TestAPI, TestAPIList
from shared.middlewares.request.permission.login import login_required

example_blueprint = Blueprint('example_blueprint', __name__)

@example_blueprint.before_request # you need a before request , if you want to apply middleware to all apis in this blueprint
#@login_required  # if need all api have login then add this
# @decorator_example_always_ok   # add other decorator, you can write your own checking follow the example
def pre_request():
    print('you can just have a empty before_request func')
    print('----- environ -----');
    for k in request.environ:
        print (k,request.environ[k])

    print('----- we have login info(if you are login) -----')
    print('----- you can get these info in your apis the same way you get it here -----')
    user = request.environ.get('user')
    org = request.environ.get('organization')
    print(user,org)

'''
-------------------------
using flask-restful example
it has apis:
-GET      /test/id/
-PUT      /test/id/
-DELETE   /test/id/
-POST     /test/
-GET      /test/
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
'''

BulkApi(api,prefix="bulk")

'''
--------------------------
raw flask blurprint route

'''
@example_blueprint.route("/raw/", methods=['GET'])
@login_required
def raw():
    result = 'this is a raw api' # result = someService.someFunc()
    return result