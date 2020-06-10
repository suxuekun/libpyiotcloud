from werkzeug.wrappers import Request
from shared.middlewares.request import handlers

class DefaultMiddleWare():
    '''
    Simple WSGI middleware
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = Request(environ)
        handlers.add_user(request)
        handlers.add_org(request)
        return self.app(environ, start_response)
