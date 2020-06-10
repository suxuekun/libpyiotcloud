import jwt
import time
from rest_api_config import config
from jose import jwt

from shared.utils import timestamp_util

def get_auth_header_token(request):
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        print("No Authorization header")
        return None
    token = auth_header.split(" ")
    if len(token) != 2:
        print("No Authorization Bearer header")
        return None
    if token[0] != "Bearer":
        print("No Bearer header")
        return None
    # print("auth header: {}".format(token[1]))
    return token[1]

def get_auth_header_info(request):
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        reason = "No Authorization header"
        print(reason)
        return None, None, reason
    token = auth_header.split(" ")
    if len(token) != 2:
        reason = "No Authorization Bearer header"
        print(reason)
        return None, None, reason
    if token[0] != "Bearer":
        reason = "No Bearer header"
        print(reason)
        return None, None, reason
    return get_jwtencode_user_pass(token[1])

def get_jwtencode_user_pass(token):
    print(token)
    payload = None
    try:
        payload = jwt.decode(token, config.CONFIG_JWT_SECRET_KEY, algorithms=['HS256'])
    except Exception as e:
        reason = "JWT decode exception"
        print(reason)
        print(e)
        return None, None, reason
    if payload is None:
        reason = "JWT decode failed"
        print(reason)
        return None, None, reason
    if not payload.get("username") or not payload.get("password") or not payload.get("iat") or not payload.get("exp"):
        reason = "JWT has missing fields"
        print(reason)
        return None, None, reason

    currepoch = timestamp_util.get_timestamp_int()
    if False:
        print("username: {}".format(payload["username"]))
        print("password: {}".format(payload["password"]))
        print("cur: {}".format(currepoch))
        print("iat: {}".format(payload["iat"]))
        print("exp: {}".format(payload["exp"]))

    if payload["exp"] - payload["iat"] != config.CONFIG_JWT_EXPIRATION:
        reason = "JWT expiration date is incorrect"
        print(reason)
        return None, None, reason
    # add lee way for both time start and time end
    # so that minor differences in time will not fail
    # example if pc is NOT set to automatically synchronize with SNTP
    # allow difference of +/- 60 seconds
    if currepoch < payload["iat"] - config.CONFIG_JWT_ADJUSTMENT:
        print("username: {}".format(payload["username"]))
        print("password: {}".format(payload["password"]))
        print("cur: {}".format(currepoch))
        print("iat: {}".format(payload["iat"]))
        print("exp: {}".format(payload["exp"]))
        reason = "currepoch({}) < payload[iat]({})".format(currepoch, payload["iat"])
        return None, None, reason
    elif currepoch > payload["exp"] + config.CONFIG_JWT_ADJUSTMENT:
        print("username: {}".format(payload["username"]))
        print("password: {}".format(payload["password"]))
        print("cur: {}".format(currepoch))
        print("iat: {}".format(payload["iat"]))
        print("exp: {}".format(payload["exp"]))
        reason = "currepoch({}) > payload[exp]({})".format(currepoch, payload["exp"])
        return None, None, reason
    return payload["username"], payload["password"], ""


# Authorization header for username and password
def get_auth_header_user_pass_ota(request):
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        reason = "No Authorization header"
        print(reason)
        return None, None, reason
    token = auth_header.split(" ")
    if len(token) != 2:
        reason = "No Authorization Bearer header"
        print(reason)
        return None, None, reason
    if token[0] != "Bearer":
        reason = "No Bearer header"
        print(reason)
        return None, None, reason
    return get_jwtencode_user_pass_ota(token[1])


# Authorization header: Bearer JWT
def get_jwtencode_user_pass_ota(token):
    payload = None
    try:
        payload = jwt.decode(token, config.CONFIG_JWT_SECRET_KEY_DEVICE, algorithms=['HS256'])
    except:
        reason = "JWT decode exception"
        print(reason)
        return None, None, reason
    if payload is None:
        reason = "JWT decode failed"
        print(reason)
        return None, None, reason
    if not payload.get("username") or not payload.get("password") or not payload.get("iat") or not payload.get("exp"):
        reason = "JWT has missing fields"
        print(reason)
        return None, None, reason

    currepoch = int(time.time())
    if True:
        print("username: {}".format(payload["username"]))
        print("password: {}".format(payload["password"]))
        print("cur: {}".format(currepoch))
        print("iat: {}".format(payload["iat"]))
        print("exp: {}".format(payload["exp"]))

    if payload["exp"] - payload["iat"] != config.CONFIG_JWT_EXPIRATION:
        reason = "JWT expiration date is incorrect"
        print(reason)
        return None, None, reason
    # add lee way for both time start and time end
    # so that minor differences in time will not fail
    # example if pc is NOT set to automatically synchronize with SNTP
    # allow difference of +/- 60 seconds
    if currepoch < payload["iat"] - config.CONFIG_JWT_ADJUSTMENT:
        print("username: {}".format(payload["username"]))
        print("password: {}".format(payload["password"]))
        print("cur: {}".format(currepoch))
        print("iat: {}".format(payload["iat"]))
        print("exp: {}".format(payload["exp"]))
        reason = "currepoch({}) < payload[iat]({})".format(currepoch, payload["iat"])
        return None, None, reason
    elif currepoch > payload["exp"] + config.CONFIG_JWT_ADJUSTMENT:
        print("username: {}".format(payload["username"]))
        print("password: {}".format(payload["password"]))
        print("cur: {}".format(currepoch))
        print("iat: {}".format(payload["iat"]))
        print("exp: {}".format(payload["exp"]))
        reason = "currepoch({}) > payload[exp]({})".format(currepoch, payload["exp"])
        return None, None, reason
    return payload["username"], payload["password"], payload

