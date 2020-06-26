from functools import wraps

from shared.middlewares.request.permission.base import getRequest


def requestWrap(f):
    @wraps(f)
    def func(*args,**kwargs):
        request = getRequest()
        ret =f(request)
        return ret
    return func

def get_user(request):
    return request.environ.get('user')

def get_org(request):
    return request.environ.get('organization')

def get_username(request):
    return get_user(request).get('username')

def get_entityname(request):
    return get_user(request).get('entityname')

def get_org_name(request):
    return get_org(request).get('orgname')

def get_org_id(request):
    return get_org(request).get('orgid')

def get_entityname_query(request):
    entityname = get_entityname(request)
    return {
        'username':entityname,
    }


