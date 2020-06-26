from random import random

from werkzeug.wrappers import Request, Response, ResponseStream

import rest_api_utils


class middleware():
    '''
    Simple WSGI middleware
    '''
    utils = rest_api_utils.utils()
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = Request(environ)
        # print('middle ware',request)
        # environ['test'] = True
        # environ['test_value'] = random()

        return self.app(environ, start_response)

        # userName = request.authorization['username']
        # password = request.authorization['password']

        # these are hardcoded for demonstration
        # verify the username and password from some database or env config variable

        # return res(environ, start_response)
