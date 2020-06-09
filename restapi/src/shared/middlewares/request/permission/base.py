import flask
from shared.middlewares.response import http4xx, make_error_response, make_custom_error_response


def getRequest(*args,**kwargs):
    print('----request----',args,kwargs)
    if len(args)>0:
        request = args[0]
    else:
        request = kwargs.get('request')
    if not request:
        request = flask.request
    print(request)
    return request;

'''
test_func(request)
return bool,error_code
error_code define in shared.middlewares.response package
see shared.middlewares.response.http4xx
'''
def request_pass_test(test_func):
    def atholder(f):
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
