from functools import wraps

import flask
from shared.middlewares.response import http4xx, make_error_response, make_custom_error_response


def getRequest(*args,**kwargs):
    if len(args)>0:
        request = args[0]
    else:
        request = kwargs.get('request')
    if not request:
        request = flask.request
    return request;


def printRequestParams(f):
    @wraps(f)
    def func(*args,**kwargs):
        request = getRequest()
        print('you can just have a empty before_request func')
        print('----- endpoint -----');
        print(request.endpoint)

        print('----- environ -----');
        for k in request.environ:
            print(k, request.environ[k])

        print('----- we have login info(if you are login) -----')
        print('----- you can get these info in your apis the same way you get it here -----')
        user = request.environ.get('user')
        org = request.environ.get('organization')
        print(user, org)
        return f(*args,**kwargs)

    return func

'''
test_func(request)
return bool,error_code
error_code define in shared.middlewares.response package
see shared.middlewares.response.http4xx
'''
def request_pass_test(test_func):
    def atholder(f):
        @wraps(f)
        def func(*args,**kwargs):
            request = getRequest(*args,**kwargs)
            res, error = test_func(request)
            if res:
                ret = f(*args, **kwargs)
            else:
                if (error):
                    ret = make_error_response(error)
                    return ret
                else:
                    return make_custom_error_response({'status':'NG','message':'unexpected access'},404)
            return ret
        return func
    return atholder

def _is_exclude_endpoint(request,options = None):
    def _condition(x):
        if isinstance(x,str):
            return x== request.endpoint
        pass
    if options:
        excludes = options.get('excludes')
        if excludes and len(excludes)> 0 :
            return any(_condition(x) for x in excludes)
            # if isinstance(excludes,str):
            #     return request.endpoint in excludes
            #
            # elif isinstance(excludes,dict):


    return False

'''
test func with excludes
'''
def request_pass_test_ignore_excludes(f):
    @wraps(f)
    def deco_with_param(options = None):
        def test_func(request):
            request = getRequest()
            if _is_exclude_endpoint(request,options):
                return True,None
            return f(request)
        def login_decorator(func):
            atholder = request_pass_test(test_func)
            if (func):
                return atholder(func)
            return atholder
        return login_decorator
    return deco_with_param

'''
example assume all request is ok
'''
def alwaysTrue(request):
    return True,None

def decorator_example_always_ok(func):
    atholder = request_pass_test(alwaysTrue)
    if (func):
        return atholder(func)
    return atholder

'''
example assume all request is token expire
'''
def alwaysFalseTokenExpire(request):
    return False,http4xx.TOKEN_EXPIRE

def decorator_example_always_token_expire(func):
    atholder = request_pass_test(alwaysFalseTokenExpire)
    if (func):
        return atholder(func)
    return atholder

'''
example assume all request is un auth
'''
def alwaysFalseUnauth(request):
    return False,http4xx.INVALID_AUTHORIZATION_HEADER

def decorator_example_alwasy_unauth(func):
    atholder = request_pass_test(alwaysFalseUnauth)
    if (func):
        return atholder(func)
    return atholder

if __name__ == "__main__":
    def someFunc():
        print('func here')
        pass

    print('-----')
    decorator_example_always_ok(someFunc)()
    print ('-----')
    try:
        decorator_example_always_token_expire(someFunc)()
    except Exception as _:
        print(_)
    print('-----')
    try:
        decorator_example_alwasy_unauth(someFunc)()
    except Exception as _:
        print(_)
