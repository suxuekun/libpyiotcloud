'''
example assume all request is ok
'''
from functools import wraps

from shared.middlewares.request.permission.base import request_pass_test_ignore_excludes


def _is_authenticated(request):
    environ = request.environ
    user = environ.get('user')
    if not user.get('username'):
        if (user.get('reason')):
            return False,user.get('reason')
        else:
            return False,None
    return True,None
# change it to this way so it check exclude first then
login_required = request_pass_test_ignore_excludes(_is_authenticated)
login_required.__name__ = 'login_required'

# def login_required(func):
#     atholder = request_pass_test(_is_authenticated)
#     if (func):
#         return atholder(func)
#     return atholder

# def login_required(options = None):
#     def test_func(request):
#         request = getRequest()
#         if _is_exclude_endpoint(request,options):
#             return True,None
#         return _is_authenticated(request)
#     def login_decorator(func):
#         atholder = request_pass_test(test_func)
#         if (func):
#             return atholder(func)
#         return atholder
#     return login_decorator