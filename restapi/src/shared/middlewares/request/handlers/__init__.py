from shared.client.clients.database_client import db_client
from shared.middlewares.response import http4xx
from shared.utils import require_util, timestamp_util
from shared.utils.pretty_print_util import pretty_print


def add_user(request):
    request.environ['user'] = request.environ.get('user') or {}
    auth_header_token = require_util.get_auth_header_token(request)
    if not auth_header_token:
        request.environ['user'].update({'reason':http4xx.INVALID_AUTHORIZATION_HEADER})
        return

    token = {'access': auth_header_token}
    access_token = auth_header_token
    username = db_client.get_username_from_token(token)
    if not username:
        request.environ['user'].update({'reason': http4xx.TOKEN_EXPIRE})
        return

    verify_ret, new_token = db_client.verify_token(username, token)

    if verify_ret ==2:
        request.environ['user'].update({'reason': http4xx.TOKEN_EXPIRE})
        return
    elif verify_ret !=0:
        request.environ['user'].update({'reason': http4xx.UNAUTHORIZED_ACCESS})
        return

    request.environ['user'].update({
        'username':username,
    })
    if new_token:
        request.environ['user'].update({
            'new_token':new_token
        })
        access_token = new_token.get('access')
    userinfo = db_client.admin_get_user(username)
    created = userinfo.get('UserCreateDate')
    last_modified = userinfo.get('UserLastModifiedDate')
    request.environ['user'].update({
        'created': created,
        'last_modified':last_modified
    })

def add_org(request):
    user = request.environ.get('user')
    username = None
    if (user):
        username = user.get('username')
    if not user:
        return
    orgname, orgid = db_client.get_active_organization(username)
    if orgname is not None:
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username
    request.environ['user'] = request.environ.get('user') or {}
    request.environ['user'].update({
        'entityname':entityname
    })
    request.environ['organization'] = request.environ.get('organization') or {}
    request.environ['organization'].update({
        'orgname':orgname,
        'orgid':orgid,
    })


