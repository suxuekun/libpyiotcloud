from functools import wraps

from werkzeug.wrappers import Request
from shared.middlewares.request import handlers
from shared.middlewares.request.permission.base import getRequest


def middleware_func(request):
    handlers.add_user(request)
    handlers.add_org(request)

def default_middleware(f):
    @wraps(f)
    def deco(*args,**kwargs):
        request = getRequest()
        middleware_func(request)
        ret = f(*args,**kwargs)
        return ret
    return deco

class DefaultMiddleWare():
    '''
    Simple WSGI middleware
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = Request(environ)
        middleware_func(request)
        return self.app(environ, start_response)


