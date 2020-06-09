'''
example assume all request is ok
'''
from shared.middlewares.request.permission.base import request_pass_test
from shared.middlewares.response import http4xx


def _is_authenticated(request):
    environ = request.environ
    user = environ.get('user')
    if not user.get('username'):
        if (user.get('reason')):
            return False,user.get('reason')
        else:
            return False,None
    return True,None

def login_required(func):
    atholder = request_pass_test(_is_authenticated)
    if (func):
        return atholder(func)
    return atholder