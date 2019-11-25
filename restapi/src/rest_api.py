import os
import ssl
import json
import time
import hmac
import hashlib
import flask
import base64
import time
from flask_json import FlaskJSON, JsonError, json_response, as_json
from certificate_generator import certificate_generator
from messaging_client import messaging_client
from rest_api_config import config
from database import database_client
from flask_cors import CORS
from flask_api import status
from jose import jwk, jwt
import http.client



###################################################################################
# Some configurations
###################################################################################

CONFIG_USE_ECC = True if int(os.environ["CONFIG_USE_ECC"]) == 1 else False
CONFIG_SEPARATOR            = '/'
CONFIG_PREPEND_REPLY_TOPIC  = "server"



###################################################################################
# global variables
###################################################################################

g_messaging_client = None
g_database_client = None
g_queue_dict  = {}
app = flask.Flask(__name__)
CORS(app)



###################################################################################
# HTTP REST APIs
###################################################################################

@app.route('/')
def index():
    return "", status.HTTP_401_UNAUTHORIZED

########################################################################################################
#
# LOGIN
#
# - Request:
#   POST /user/login
#   headers: {'Authorization': 'Basic ' + jwtEncode(username, password)}
#
# - Response:
#   {'status': 'OK', 'message': string, 'token': {'access': string, 'id': string, 'refresh': string} }
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user/login', methods=['POST'])
def login():
    # get username and password from Authorization header
    username, password, reason = get_auth_header_user_pass()
    if username is None or password is None:
        response = json.dumps({'status': 'NG', 'message': reason})
        print('\r\nERROR Login: Username password format invalid\r\n')
        return response, status.HTTP_400_BAD_REQUEST
    print('login username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(password) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Login: Empty parameter found [{}]\r\n'.format(username))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username does not exist
    print('find_user')
    if not g_database_client.find_user(username):
        # NOTE:
        # its not good to provide a specific error message for LOGIN
        # because it provides additional info for hackers
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Login: Username does not exist [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    # check if password is valid
    print('login')
    access, refresh, id = g_database_client.login(username, password)
    if not access:
        # NOTE:
        # its not good to provide a specific error message for LOGIN
        # because it provides additional info for hackers
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Login: Password is incorrect [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    response = json.dumps({'status': 'OK', 'message': "Login successful", 'token': {'access': access, 'refresh': refresh, 'id': id} })
    print('\r\nLogin successful: {}\r\n'.format(username))
    #print('\r\nLogin successful: {}\r\n{}\r\n'.format(username, response))
    return response

########################################################################################################
#
# SIGN-UP
#
# - Request:
#   POST /user/signup
#   headers: {'Authorization': 'Bearer ' + jwtEncode(email, password), 'Content-Type': 'application/json'}
#   data: { 'email': string, 'phone_number': string, 'name': string }
#   // name can be 1 or multiple words
#   // phone_number is optional
#   // phone number should begin with "+" followed by country code then the number (ex. SG number +6512341234)
#   // password length is 6 characters minimum as set in Cognito
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user/signup', methods=['POST'])
def signup():
    # get username and password from Authorization header
    username, password, reason = get_auth_header_user_pass()
    if username is None or password is None:
        response = json.dumps({'status': 'NG', 'message': reason})
        print('\r\nERROR Signup: Username password format invalid\r\n')
        return response, status.HTTP_400_BAD_REQUEST
    #print('signup username={}'.format(username))

    data = flask.request.get_json()
    email = data['email']
    if data.get("phone_number"):
        phonenumber = data['phone_number']
    else:
        phonenumber = None
    name = data['name']
    names = name.split(" ")
    if (len(names) > 1):
        givenname = " ".join(names[:-1])
        familyname = names[-1]
    else:
        # handle no family name
        givenname = names[0]
        familyname = "NONE"

    print('signup username={} password={} email={} phonenumber={} givenname={} familyname={}'.format(username, password, email, phonenumber, givenname, familyname))

    # check if a parameter is empty
    if len(username) == 0 or len(password) == 0 or len(email) == 0 or len(givenname) == 0 or len(familyname) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Signup: Empty parameter found [{}]\r\n'.format(username))
        return response, status.HTTP_400_BAD_REQUEST

    # check format of phonenumber
    if phonenumber is not None:
        if phonenumber[0] != "+":
            response = json.dumps({'status': 'NG', 'message': 'Phone number format is invalid'})
            print('\r\nERROR Signup: Phone number format is invalid [{}]\r\n'.format(phonenumber))
            return response, status.HTTP_400_BAD_REQUEST

    # check length of password
    if len(password) < 6:
        response = json.dumps({'status': 'NG', 'message': 'Password length should at least be 6 characters'})
        print('\r\nERROR Signup: Password length should at least be 6 characters [{}]\r\n'.format(username))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username is already in database
    if g_database_client.find_user(username):
        response = json.dumps({'status': 'NG', 'message': 'Username already exists'})
        print('\r\nERROR Signup: Username already exists [{}]\r\n'.format(username))
        return response, status.HTTP_409_CONFLICT

    # check if email is already in database
    if g_database_client.find_email(email) is not None:
        response = json.dumps({'status': 'NG', 'message': 'Email already used'})
        print('\r\nERROR Signup: Email already used [{}]\r\n'.format(email))
        return response, status.HTTP_409_CONFLICT

    # add entry in database
    result = g_database_client.add_user(username, password, email, phonenumber, givenname, familyname)
    if not result:
        response = json.dumps({'status': 'NG', 'message': 'Internal server error'})
        print('\r\nERROR Signup: Internal server error [{},{},{},{},{}]\r\n'.format(username, password, email, givenname, familyname))
        return response, status.HTTP_400_BAD_REQUEST

    response = json.dumps({'status': 'OK', 'message': 'User registered successfully. Check email for confirmation code.'})
    print('\r\nSignup successful: {}\r\n{}\r\n'.format(username, response))
    return response

########################################################################################################
#
# CONFIRM SIGN-UP
#
# - Request:
#   POST /user/confirm_signup
#   headers: {'Content-Type': 'application/json'}
#   data: { 'username': string, 'confirmationcode': string }
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user/confirm_signup', methods=['POST'])
def confirm_signup():
    data = flask.request.get_json()
    username = data['username']
    confirmationcode = data['confirmationcode']
    #print('confirm_signup username={} confirmationcode={}'.format(username, confirmationcode))

    # check if a parameter is empty
    if len(username) == 0 or len(confirmationcode) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Confirm Signup: Empty parameter found [{}]\r\n'.format(username))
        return response, status.HTTP_400_BAD_REQUEST

    # confirm user in database
    result = g_database_client.confirm_user(username, confirmationcode)
    if not result:
        response = json.dumps({'status': 'NG', 'message': 'Invalid code'})
        print('\r\nERROR Confirm Signup: Invalid code [{},{}]\r\n'.format(username, confirmationcode))
        return response, status.HTTP_400_BAD_REQUEST

    response = json.dumps({'status': 'OK', 'message': 'User registration confirmed successfully'})
    print('\r\nConfirm Signup successful: {}\r\n{}\r\n'.format(username, response))
    return response

########################################################################################################
#
# RESEND CONFIRMATION CODE
#
# - Request:
#   POST /user/resend_confirmation_code
#   headers: {'Content-Type': 'application/json'}
#   data: { 'username': string }
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user/resend_confirmation_code', methods=['POST'])
def resend_confirmation_code():
    data = flask.request.get_json()
    username = data['username']
    print('resend_confirmation_code username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Resend Confirmation: Empty parameter found [{}]\r\n'.format(username))
        return response, status.HTTP_400_BAD_REQUEST

    # confirm user in database
    result = g_database_client.resend_confirmationcode(username)
    if not result:
        response = json.dumps({'status': 'NG', 'message': 'Invalid code'})
        print('\r\nERROR Resend Confirmation: Invalid code [{}]\r\n'.format(username))
        return response, status.HTTP_400_BAD_REQUEST

    response = json.dumps({'status': 'OK', 'message': 'Confirmation code resend successfully'})
    print('\r\nResend Confirmation successful: {}\r\n{}\r\n'.format(username, response))
    return response

########################################################################################################
#
# FORGOT PASSWORD
#
# - Request:
#   POST /user/forgot_password
#   headers: {'Content-Type': 'application/json'}
#   data: { 'email': string }
#
# - Response:
#   {'status': 'OK', 'message': string, 'username': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user/forgot_password', methods=['POST'])
def forgot_password():
    data = flask.request.get_json()
    email = data['email']
    #print('forgot_password email={}'.format(email))

    # check if a parameter is empty
    if len(email) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Recover Account: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if email is in database
    username = g_database_client.find_email(email)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Email does not exist'})
        print('\r\nERROR Recover Account: Email does not exist [{}]\r\n'.format(email))
        return response, status.HTTP_400_BAD_REQUEST

    # recover account
    result = g_database_client.forgot_password(username)
    if not result:
        response = json.dumps({'status': 'NG', 'message': 'Internal server error'})
        print('\r\nERROR Recover Account: Internal server error [{}]\r\n'.format(email))
        return response, status.HTTP_400_BAD_REQUEST

    response = json.dumps({'status': 'OK', 'message': 'User account recovery successfully. Check email for confirmation code.', 'username': username})
    print('\r\nRecover Account successful: {}\r\n{}\r\n'.format(username, response))
    return response

########################################################################################################
#
# CONFIRM FORGOT PASSWORD
#
# - Request:
#   POST /user/confirm_forgot_password
#   headers: {'Authorization': 'Bearer ' + jwtEncode(username, password), 'Content-Type': 'application/json'}
#   data: { 'confirmationcode': string }
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user/confirm_forgot_password', methods=['POST'])
def confirm_forgot_password():
    # get username and password from Authorization header
    username, password, reason = get_auth_header_user_pass()
    if username is None or password is None:
        response = json.dumps({'status': 'NG', 'message': reason})
        print('\r\nERROR Reset Password: Username password format invalid\r\n')
        return response, status.HTTP_400_BAD_REQUEST
    print('confirm_forgot_password username={}'.format(username))

    data = flask.request.get_json()
    confirmationcode = data['confirmationcode']
    #print('confirm_forgot_password username={} confirmationcode={} password={}'.format(username, confirmationcode, password))

    # check if a parameter is empty
    if len(username) == 0 or len(confirmationcode) == 0 or len(password) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Reset Password: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # confirm user in database
    result = g_database_client.confirm_forgot_password(username, confirmationcode, password)
    if not result:
        response = json.dumps({'status': 'NG', 'message': 'Invalid code'})
        print('\r\nERROR Reset Password: Invalid code [{}]\r\n'.format(username))
        return response, status.HTTP_400_BAD_REQUEST

    response = json.dumps({'status': 'OK', 'message': 'User account recovery confirmed successfully.'})
    print('\r\nReset Password successful: {}\r\n{}\r\n'.format(username, response))
    return response


########################################################################################################
#
# LOGOUT
#
# - Request:
#   POST /user/logout
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user/logout', methods=['POST'])
def logout():
    data = flask.request.get_json()
    try:
        # get token from Authorization header
        auth_header_token = get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Logout: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = g_database_client.get_username_from_token(token)
        print('logout username={}'.format(username))

    except:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Logout: Empty parameter found\r\n')
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response
    print('logout username={} token={}'.format(username, token))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Logout: Empty parameter found\r\n')
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Logout: Token expired [{}]\r\n'.format(username))
        return response
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Logout: Token is invalid [{}]\r\n'.format(username))
        return response

    if new_token:
        g_database_client.logout(new_token['access'])
    else:
        g_database_client.logout(token['access'])


    msg = {'status': 'OK', 'message': 'User logout successfully.'}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\nLogout successful: {}\r\n{}\r\n'.format(username, response))
    return response


########################################################################################################
#
# GET USER INFO
#
# - Request:
#   GET /user
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 
#    'info': {'name': string, 'email': string, 'phone_number': string, 'email_verified': boolean, 'phone_number_verified': boolean} }
#   // phone_number and phone_number_verified are not included if no phone_number has been added yet
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user', methods=['GET'])
def get_user_info():
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Userinfo: Invalid authorization header [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('get_user_info username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Userinfo: Empty parameter found\r\n')
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2: # token expired
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Userinfo: Token expired [{}]\r\n'.format(username))
        return response
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Userinfo: Token is invalid [{}]\r\n'.format(username))
        return response

    if new_token:
        info = g_database_client.get_user_info(new_token['access'])
    else:
        info = g_database_client.get_user_info(token['access'])
    print(info)

    # handle no family name
    if 'given_name' in info:
        info['name'] = info['given_name']
        info.pop("given_name")
    if 'family_name' in info:
        if info['family_name'] != "NONE":
            info['name'] += " " + info['family_name']
        info.pop("family_name")

    msg = {'status': 'OK', 'message': 'Userinfo queried successfully.', 'info': info}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\nUserinfo queried successful: {}\r\n{}\r\n'.format(username, response))
    return response


########################################################################################################
#
# DELETE USER
#
# - Request:
#   DELETE /user
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string }
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user', methods=['DELETE'])
def delete_user():
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Delete user: Invalid authorization header [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('delete_user username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Delete user: Empty parameter found\r\n')
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2: # token expired
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Delete user: Token expired [{}]\r\n'.format(username))
        return response
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Delete user: Token is invalid [{}]\r\n'.format(username))
        return response

    # delete the user in cognito
    if new_token:
        result = g_database_client.delete_user(username, new_token['access'])
    else:
        result = g_database_client.delete_user(username, token['access'])
    if result == False:
        response = json.dumps({'status': 'NG', 'message': 'Delete user failed internal error'})
        print('\r\nERROR Delete user: Internal error [{}]\r\n'.format(username))
        return response

    # TODO: delete user devices

    msg = {'status': 'OK', 'message': 'Delete user successful.'}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\nDelete user successful: {}\r\n{}\r\n'.format(username, response))
    return response


########################################################################################################
#
# REFRESH USER TOKEN
#
# - Request:
#   POST /user/token
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'refresh': string, 'id: string' }
#
# - Response:
#   {'status': 'OK', 'message': string, 'token' : {'access': string, 'refresh': string, 'id': string} }
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user/token', methods=['POST'])
def refresh_user_token():
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Refresh token: Invalid authorization header [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('refresh_user_token username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Refresh token: Empty parameter found\r\n')
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response

    # get refresh and id token
    data = flask.request.get_json()
    if not data.get("refresh") or not data.get("id"):
        response = json.dumps({'status': 'NG', 'message': 'Refresh and ID tokens are not provided'})
        print('\r\nERROR Refresh token: Refresh and ID tokens are not provided [{}]\r\n'.format(username))
        return response
    token['refresh'] = data['refresh']
    token['id'] = data['id']

    # refresh the access token
    new_token = g_database_client.refresh_token(username, token)
    if new_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Refresh token invalid'})
        print('\r\nERROR Refresh token: Token expired [{}]\r\n'.format(username))
        return response

    msg = {'status': 'OK', 'message': 'Refresh token successful.', 'token': new_token}
    response = json.dumps(msg)
    print('\r\nRefresh token successful: {}\r\n{}\r\n'.format(username, response))
    return response


########################################################################################################
#
# VERIFY PHONE NUMBER
#
# - Request:
#   POST /user/verify_phone_number
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user/verify_phone_number', methods=['POST'])
def verify_phone_number():
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Verify phone: Invalid authorization header [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('refresh_user_token username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Verify phone: Empty parameter found\r\n')
        return response

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2: # token expired
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Verify phone: Token expired [{}]\r\n'.format(username))
        return response
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Verify phone: Token is invalid [{}]\r\n'.format(username))
        return response

    # verify phone number
    result = g_database_client.request_verify_phone_number(token["access"])
    if not result:
        response = json.dumps({'status': 'NG', 'message': 'Request failed'})
        print('\r\nERROR Verify phone: Request failed [{}]\r\n'.format(username))
        return response, status.HTTP_400_BAD_REQUEST

    response = json.dumps({'status': 'OK', 'message': 'Verify phone successful'})
    print('\r\nVerify phone successful: {}\r\n{}\r\n'.format(username, response))
    return response


########################################################################################################
#
# CONFIRM VERIFY PHONE NUMBER
#
# - Request:
#   POST /user/confirm_verify_phone_number
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: {'confirmationcode': string}
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user/confirm_verify_phone_number', methods=['POST'])
def confirm_verify_phone_number():
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Confirm verify phone: Invalid authorization header [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('refresh_user_token username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Confirm verify phone: Empty parameter found\r\n')
        return response

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2: # token expired
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Confirm verify phone: Token expired [{}]\r\n'.format(username))
        return response
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Confirm verify phone: Token is invalid [{}]\r\n'.format(username))
        return response

    data = flask.request.get_json()

    # confirm verify phone number
    result = g_database_client.confirm_verify_phone_number(token["access"], data["confirmationcode"])
    if not result:
        response = json.dumps({'status': 'NG', 'message': 'Request failed'})
        print('\r\nERROR Confirm verify phone: Request failed [{}]\r\n'.format(username))
        return response, status.HTTP_400_BAD_REQUEST

    response = json.dumps({'status': 'OK', 'message': 'Confirm verify phone successful'})
    print('\r\nConfirm verify phone successful: {}\r\n{}\r\n'.format(username, response))
    return response


########################################################################################################
#
# CHANGE PASSWORD
#
# - Request:
#   POST /user/change_password
#   headers: {'Authorization': 'Bearer ' + token.access}
#   data: {'token': jwtEncode(password, newpassword)}
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user/change_password', methods=['POST'])
def change_password():
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Change password: Invalid authorization header [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('refresh_user_token username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Change password: Empty parameter found\r\n')
        return response

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2: # token expired
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Change password: Token expired [{}]\r\n'.format(username))
        return response
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Change password: Token is invalid [{}]\r\n'.format(username))
        return response

    data = flask.request.get_json()
    password, newpassword, reason = get_jwtencode_user_pass(data["token"])
    if password is None or newpassword is None:
        response = json.dumps({'status': 'NG', 'message': reason})
        print('\r\nERROR Change password: Password newpassword format invalid\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # change password
    result = g_database_client.change_password(token["access"], password, newpassword)
    if not result:
        response = json.dumps({'status': 'NG', 'message': 'Request failed'})
        print('\r\nERROR Change password: Request failed [{}]\r\n'.format(username))
        return response, status.HTTP_400_BAD_REQUEST

    response = json.dumps({'status': 'OK', 'message': 'Change password successful'})
    print('\r\nChange password successful: {}\r\n{}\r\n'.format(username, response))
    return response


########################################################################################################
#
# UPDATE USER INFO
#
# - Request:
#   POST /user
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: {'name': string, 'phone_number': string}
#   // phone_number is optional
#   // phone number should begin with "+" followed by country code then the number (ex. SG number +6512341234)
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user', methods=['POST'])
def update_user_info():
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Update user: Invalid authorization header [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('refresh_user_token username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Update user: Empty parameter found\r\n')
        return response

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2: # token expired
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Update user: Token expired [{}]\r\n'.format(username))
        return response
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Update user: Token is invalid [{}]\r\n'.format(username))
        return response

    # get the input parameters
    data = flask.request.get_json()
    if data.get('phone_number'):
        phonenumber = data['phone_number']
    else:
        phonenumber = None
    print(phonenumber)
    name = data['name']
    names = name.split(" ")
    if (len(names) > 1):
        givenname = " ".join(names[:-1])
        familyname = names[-1]
    else:
        # handle no family name
        givenname = names[0]
        familyname = "NONE"

    # change user
    result = g_database_client.update_user(token["access"], phonenumber, givenname, familyname)
    if not result:
        response = json.dumps({'status': 'NG', 'message': 'Request failed'})
        print('\r\nERROR Update user: Request failed [{}]\r\n'.format(username))
        return response, status.HTTP_400_BAD_REQUEST

    response = json.dumps({'status': 'OK', 'message': 'Change password successful'})
    print('\r\nUpdate user successful: {}\r\n{}\r\n'.format(username, response))
    return response


#########################


########################################################################################################
#
# GET SUBSCRIPTION
#
# - Request:
#   GET /account/subscription
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#  {'status': 'OK', 'message': string, 'subscription': {'credits': string, 'type': string} }
#  {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/account/subscription', methods=['GET'])
def get_subscription():
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get Subscription: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('get_subscription username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get Subscription: Empty parameter found\r\n')
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get Subscription: Token expired [{}]\r\n'.format(username))
        return response
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get Subscription: Token is invalid [{}]\r\n'.format(username))
        return response

    subscription = g_database_client.get_subscription(username)
    print(subscription)
    msg = {'status': 'OK', 'message': 'User subscription queried successfully.', 'subscription': subscription}


    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\n{}: {}\r\n{}\r\n'.format(msg['message'], username, response))
    return response


########################################################################################################
#
# SET SUBSCRIPTION
#
# - Request:
#   POST /account/subscription
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'credits': string }
#
# - Response:
#  {'status': 'OK', 'message': string, 'subscription': {'credits': string, 'type': paid} }
#  {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/account/subscription', methods=['POST'])
def set_subscription():
    data = flask.request.get_json()
    credits = data['credits']

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Set Subscription: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('set_subscription username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Set Subscription: Empty parameter found\r\n')
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Set Subscription: Token expired [{}]\r\n'.format(username))
        return response
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Set Subscription: Token is invalid [{}]\r\n'.format(username))
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response

    subscription = g_database_client.set_subscription(username, credits)
    print(subscription)
    msg = {'status': 'OK', 'message': 'User subscription set successfully.', 'subscription': subscription}


    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\n{}: {}\r\n{}\r\n'.format(msg['message'], username, response))
    return response

#########################


########################################################################################################
#
# PAYPAL SETUP
#
# - Request:
#   POST /account/payment/paypalsetup
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'return_url': string, 'cancel_url', string, 'item_sku': string, 'item_credits': string, 'item_price': string }
#
# - Response:
#   {'status': 'OK', 'message': string, 'approval_url': string, 'paymentId': string, 'token': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/account/payment/paypalsetup', methods=['POST'])
def set_payment_paypal_setup():
    data = flask.request.get_json()
    payment = data

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Paypal Setup: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('set_payment_paypal_setup username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Paypal Setup: Empty parameter found\r\n')
        return response

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Paypal Setup: Token expired [{}]\r\n'.format(username))
        return response
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Paypal Setup: Token is invalid [{}]\r\n'.format(username))
        return response

    if flask.request.method != 'POST':
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Paypal Setup: Token is invalid [{}]\r\n'.format(username))
        return response

    print(payment)
    approval_url, payment_id, token = g_database_client.transactions_paypal_set_payment(username, token, payment)
    msg = {'status': 'OK', 'message': 'Paypal payment setup successful.', 'approval_url': approval_url, 'paymentId': payment_id, 'token': token}

    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\n{}: {}\r\n{}\r\n'.format(msg['message'], username, response))
    return response


########################################################################################################
#
# PAYPAL EXECUTE
#
# - Request:
#   POST /account/payment/paypalexecute
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'paymentId': string, 'payerId': string, 'token': string }
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/account/payment/paypalexecute', methods=['POST'])
def set_payment_paypal_execute():
    data = flask.request.get_json()
    payment = data

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Paypal Execute: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('set_payment_paypal_execute username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Paypal Execute: Empty parameter found\r\n')
        return response

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Paypal Execute: Token expired [{}]\r\n'.format(username))
        return response
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Paypal Execute: Token is invalid [{}]\r\n'.format(username))
        return response

    if flask.request.method != 'POST':
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Paypal Execute: Token is invalid [{}]\r\n'.format(username))
        return response

    print(payment)
    status = g_database_client.transactions_paypal_execute_payment(username, token, payment)
    if status:
        msg = {'status': 'OK', 'message': 'Paypal payment execution successful.'}
    else:
        msg = {'status': 'NG', 'message': 'Paypal payment execution failed.'}


    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\n{}: {}\r\n{}\r\n'.format(msg['message'], username, response))
    return response


########################################################################################################
#
# PAYPAL VERIFY
#
# - Request:
#   POST /account/payment/paypalverify
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'paymentId': string }
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/account/payment/paypalverify', methods=['POST'])
def set_payment_paypal_verify():
    data = flask.request.get_json()
    payment = data

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Paypal Verify: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('set_payment_paypal_verify username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Paypal Verify: Empty parameter found\r\n')
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Paypal Verify: Token expired [{}]\r\n'.format(username))
        return response
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Paypal Verify: Token is invalid [{}]\r\n'.format(username))
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response

    if flask.request.method != 'POST':
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Paypal Verify: Token is invalid [{}]\r\n'.format(username))
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response

    print(payment)
    status = g_database_client.transactions_paypal_verify_payment(username, token, payment)
    if status:
        msg = {'status': 'OK', 'message': 'Paypal payment verification successful.'}
    else:
        msg = {'status': 'NG', 'message': 'Paypal payment verification failed.'}


    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\n{}: {}\r\n{}\r\n'.format(msg['message'], username, response))
    return response

#########################




########################################################################################################
# 
# GET DEVICES
#
# - Request:
#   GET /devices
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'devices': array[{'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': string}, ...]}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices', methods=['GET'])
def get_device_list():
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get Devices: Invalid authorization header [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('get_device_list username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get Devices: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get Devices: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get Devices: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    devices = g_database_client.get_devices(username)
    #print(devices)


    msg = {'status': 'OK', 'message': 'Devices queried successfully.', 'devices': devices}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\nGet Devices successful: {}\r\n{} devices\r\n'.format(username, len(devices)))
    return response

########################################################################################################
#
# ADD DEVICE
#
# - Request:
#   POST /devices/device/<devicename>
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: {'deviceid': string, 'serialnumber': string}
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
#
# DELETE DEVICE
#
# - Request:
#   DELETE /devices/device/<devicename>
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/device/<devicename>', methods=['POST', 'DELETE'])
def register_device(devicename):
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Add/Delete Device: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('register_device username={} devicename={}'.format(username, devicename))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(devicename) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Add/Delete Device: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Add/Delete Device: Token expired [{}]\r\n'.format(username))
        return response
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Add/Delete Device: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    if flask.request.method == 'POST':
        # check if device is registered
        if g_database_client.find_device(username, devicename):
            response = json.dumps({'status': 'NG', 'message': 'Device is already registered'})
            print('\r\nERROR Add Device: Device is already registered [{},{}]\r\n'.format(username, devicename))
            return response, status.HTTP_409_CONFLICT

        data = flask.request.get_json()
        print(data)
        if not data.get("deviceid") or not data.get("serialnumber"):
            response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
            print('\r\nERROR Add Device: Parameters not included [{},{}]\r\n'.format(username, devicename))
            return response, status.HTTP_400_BAD_REQUEST
        print(data["deviceid"])
        print(data["serialnumber"])

        # add device to database
        result = g_database_client.add_device(username, devicename, data["deviceid"], data["serialnumber"])
        print(result)
        if not result:
            response = json.dumps({'status': 'NG', 'message': 'Device could not be registered'})
            print('\r\nERROR Add Device: Device could not be registered [{},{}]\r\n'.format(username, devicename))
            return response, status.HTTP_400_BAD_REQUEST

        # add and configure message broker user
        result = message_broker_register(data["deviceid"], data["serialnumber"])
        print(result)
        if not result:
            response = json.dumps({'status': 'NG', 'message': 'Device could not be registered in message broker'})
            print('\r\nERROR Add Device: Device could not be registered  in message broker [{},{}]\r\n'.format(username, devicename))
            return response, status.HTTP_400_BAD_REQUEST

        msg = {'status': 'OK', 'message': 'Devices registered successfully.'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nDevice registered successful: {}\r\n{}\r\n'.format(username, response))
        return response

    elif flask.request.method == 'DELETE':

        # check if device is registered
        device = g_database_client.find_device(username, devicename)
        if not device:
            response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
            print('\r\nERROR Delete Device: Device is not registered [{},{}]\r\n'.format(username, devicename))
            return response, status.HTTP_400_BAD_REQUEST

        # delete device from database
        g_database_client.delete_device(username, devicename)

        # delete message broker user
        result = message_broker_unregister(device["deviceid"])
        print(result)
        if not result:
            response = json.dumps({'status': 'NG', 'message': 'Device could not be unregistered in message broker'})
            print('\r\nERROR Delete Device: Device could not be unregistered  in message broker [{},{}]\r\n'.format(username, devicename))
            return response, status.HTTP_400_BAD_REQUEST

        msg = {'status': 'OK', 'message': 'Devices unregistered successfully.'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nDevice unregistered successful: {}\r\n{}\r\n'.format(username, response))
        return response


########################################################################################################
#
# GET DEVICE
#
# - Request:
#   GET /devices/device/<devicename>
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'device': {'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': string}}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/device/<devicename>', methods=['GET'])
def get_device(devicename):
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get Device: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('get_device username={} devicename={}'.format(username, devicename))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(devicename) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get Device: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get Device: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get Device: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    # check if device is registered
    device = g_database_client.find_device(username, devicename)
    if not device:
        response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
        print('\r\nERROR Get Device: Device is not registered [{},{}]\r\n'.format(username, devicename))
        return response, status.HTTP_400_BAD_REQUEST


    msg = {'status': 'OK', 'message': 'Devices queried successfully.', 'device': device}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\nDevice queried successful: {}\r\n{}\r\n'.format(username, response))
    return response


#########################


########################################################################################################
#
# GET HISTORIES
#
# - Request:
#   GET /devices/histories
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   { 'status': 'OK', 'message': string, 
#     'histories': array[
#       {'devicename': string, 'deviceid': string, 'direction': string, 'topic': string, 'payload': string, 'timestamp': string}, ...]}
#   { 'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/histories', methods=['GET'])
def get_device_histories():
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get Histories: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}
    print('get_user_histories token={}'.format(token["access"]))

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('get_user_histories username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get Histories: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2: # token expired
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get Histories: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get Histories: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    histories = g_database_client.get_user_history(username)
    print(histories)


    msg = {'status': 'OK', 'message': 'User histories queried successfully.', 'histories': histories}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    return response


########################################################################################################
#
# GET HISTORIES FILTERED
#
# - Request:
#   POST /devices/histories
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'devicename': string, 'deviceid': string, 'direction': string, 'topic': string, 'datebegin': int, 'dateend': int }
#
# - Response:
#   { 'status': 'OK', 'message': string, 
#     'histories': array[
#       {'devicename': string, 'deviceid': string, 'direction': string, 'topic': string, 'payload': string, 'timestamp': string}, ...]}
#   { 'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/histories', methods=['POST'])
def get_device_histories_filtered():
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get Histories: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('get_user_histories username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get Histories: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2: # token expired
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get Histories: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get Histories: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    # get filter data
    devicename = None
    direction = None
    topic = None
    datebegin = 0
    dateend = 0
    data = flask.request.get_json()
    if data.get("devicename"):
        devicename = data["devicename"]
    if data.get("direction"):
        direction = data["direction"]
    if data.get("topic"):
        topic = data["topic"]
    if data.get("datebegin"):
        datebegin = data["datebegin"]
        if data.get("dateend"):
            dateend = data["dateend"]

    histories = g_database_client.get_user_history_filtered(username, devicename, direction, topic, datebegin, dateend)
    print(histories)


    msg = {'status': 'OK', 'message': 'User histories queried successfully.', 'histories': histories}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    return response

#########################


########################################################################################################
# GET  /devices/device/<devicename>/xxx
# POST /devices/device/<devicename>/xxx
########################################################################################################
#
# GET STATUS
# - Request:
#   GET /devices/device/<devicename>/status
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': string }
#   { 'status': 'NG', 'message': string}
#
@app.route('/devices/device/<devicename>/status', methods=['GET'])
def get_status(devicename):
    api = 'get_status'

    print(devicename)
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = {}
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    data['username'] = g_database_client.get_username_from_token(data['token'])
    print('get_status username={}'.format(data['username']))

    return process_request_get(api, data)

#
# SET STATUS
# - Request:
#   POST /devices/device/<devicename>/status
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'value': string }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': string}
#   { 'status': 'NG', 'message': string}
#
@app.route('/devices/device/<devicename>/status', methods=['POST'])
def set_status(devicename):
    api = 'set_status'

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = flask.request.get_json()
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    data['username'] = g_database_client.get_username_from_token(data['token'])
    print('set_status username={}'.format(data['username']))

    return process_request(api, data)

#
# GET IP
#
# - Request:
#   GET /devices/device/<devicename>/ip
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': string }
#   { 'status': 'NG', 'message': string}
#
@app.route('/devices/device/<devicename>/ip', methods=['GET'])
def get_ip(devicename):
    api = 'get_ip'

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = {}
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    data['username'] = g_database_client.get_username_from_token(data['token'])
    print('get_ip username={}'.format(data['username']))

    return process_request_get(api, data)

#
# GET SUBNET
#
# - Request:
#   GET /devices/device/<devicename>/subnet
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': string }
#   { 'status': 'NG', 'message': string}
#
@app.route('/devices/device/<devicename>/subnet', methods=['GET'])
def get_subnet(devicename):
    api = 'get_subnet'

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = {}
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    data['username'] = g_database_client.get_username_from_token(data['token'])
    print('get_subnet username={}'.format(data['username']))

    return process_request_get(api, data)

#
# GET GATEWAY
#
# - Request:
#   GET /devices/device/<devicename>/gateway
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': string }
#   { 'status': 'NG', 'message': string}
#
@app.route('/devices/device/<devicename>/gateway', methods=['GET'])
def get_gateway(devicename):
    api = 'get_gateway'

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = {}
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    data['username'] = g_database_client.get_username_from_token(data['token'])
    print('get_gateway username={}'.format(data['username']))

    return process_request_get(api, data)

#
# GET MAC
#
# - Request:
#   GET /devices/device/<devicename>/mac
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': string }
#   { 'status': 'NG', 'message': string}
#
@app.route('/devices/device/<devicename>/mac', methods=['GET'])
def get_mac(devicename):
    api = 'get_mac'

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = {}
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    data['username'] = g_database_client.get_username_from_token(data['token'])
    print('get_mac username={}'.format(data['username']))

    return process_request_get(api, data)

# 
# GET GPIO
# 
# - Request:
#   GET /devices/device/<devicename>/gpio/<number>
#   headers: {'Authorization': 'Bearer ' + token.access}
# 
# - Response:
#   { 'status': 'OK', 'message': string, 'value': string }
#   { 'status': 'NG', 'message': string}
# 
@app.route('/devices/device/<devicename>/gpio/<number>', methods=['GET'])
def get_gpio(devicename, number):
    api = 'get_gpio'

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = {}
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    data['number'] = number
    data['username'] = g_database_client.get_username_from_token(data['token'])
    print('get_gpio username={}'.format(data['username']))

    return process_request_get(api, data)

# 
# SET GPIO
# 
# - Request:
#   POST /devices/device/<devicename>/gpio/<number>
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'value': string }
# 
# - Response:
#   { 'status': 'OK', 'message': string, 'value': string }
#   { 'status': 'NG', 'message': string}
# 
@app.route('/devices/device/<devicename>/gpio/<number>', methods=['POST'])
def set_gpio(devicename, number):
    api = 'set_gpio'

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = flask.request.get_json()
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    data['number'] = number
    data['username'] = g_database_client.get_username_from_token(data['token'])
    print('set_gpio username={}'.format(data['username']))

    return process_request(api, data)

#
# GET RTC
#
# - Request:
#   GET devices/device/<devicename>/rtc
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': string }
#   { 'status': 'NG', 'message': string}
#
@app.route('/devices/device/<devicename>/rtc', methods=['GET'])
def get_rtc(devicename):
    api = 'get_rtc'

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = {}
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    data['username'] = g_database_client.get_username_from_token(data['token'])
    print('get_rtc username={}'.format(data['username']))

    return process_request_get(api, data)

#
# SET UART
#
# - Request:
#   POST /devices/device/<devicename>/uart
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'value': string }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': string }
#   { 'status': 'NG', 'message': string}
#
@app.route('/devices/device/<devicename>/uart', methods=['POST'])
def write_uart(devicename):
    api = 'write_uart'

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = flask.request.get_json()
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    data['username'] = g_database_client.get_username_from_token(data['token'])
    print('write_uart username={}'.format(data['username']))

    return process_request(api, data)

#
# SET NOTIFICATIONS
#
# - Request:
#   POST /devices/device/<devicename>/notification
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'recipient': string, 'message': string, 'options': string }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': string }
#   { 'status': 'NG', 'message': string}
#
@app.route('/devices/device/<devicename>/notification', methods=['POST'])
def trigger_notification(devicename):
    api = 'trigger_notification'

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = flask.request.get_json()
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    data['username'] = g_database_client.get_username_from_token(data['token'])
    print('trigger_notification username={}'.format(data['username']))

    return process_request(api, data)




#########################



def generate_publish_topic(data, deviceid, api, separator):
    #username = data['username']
    #devicename = data['devicename']
    #topic = username + separator + devicename + separator + api 
    topic = deviceid + separator + api 
    return topic

def generate_publish_payload(data):
    data.pop('username')
    data.pop('token')
    data.pop('devicename')
    payload = json.dumps(data)
    return payload

def generate_subscribe_topic(topic, separator):
    topic = CONFIG_PREPEND_REPLY_TOPIC + separator + topic
    return topic


def process_request_get(api, data):

    print("\r\nAPI: {} username={} devicename={}".format(api, data['username'], data['devicename']))

    username = data['username']
    token = data['token']
    devicename = data['devicename']

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    # check if device is registered
    if not g_database_client.find_device(username, devicename):
        response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
        print('\r\nERROR Device is not registered [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    # get deviceid for subscribe purpose (AMQP)
    deviceid = g_database_client.get_deviceid(username, devicename)

    # construct publish/subscribe topics and payloads
    pubtopic = generate_publish_topic(data, deviceid, api, CONFIG_SEPARATOR)
    payload = generate_publish_payload(data)
    subtopic = generate_subscribe_topic(pubtopic, CONFIG_SEPARATOR)

    try:
        # subscribe for response
        ret = g_messaging_client.subscribe(subtopic, subscribe=True, deviceid=deviceid)
        if ret:
            # publish request
            g_messaging_client.publish(pubtopic, payload)

            # receive response
            response = receive_message(subtopic)
            g_messaging_client.subscribe(subtopic, subscribe=False)
        else:
            msg = {'status': 'NG', 'message': 'Could not communicate with device'}
            if new_token:
                msg['new_token'] = new_token
            response = json.dumps(msg)
            print('\r\nERROR Could not communicate with device [{}, {}]\r\n'.format(username, devicename))
            return response, status.HTTP_401_UNAUTHORIZED
    except:
        msg = {'status': 'NG', 'message': 'Could not communicate with device'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nERROR Could not communicate with device [{}, {}]\r\n'.format(username, devicename))
        return response, status.HTTP_401_UNAUTHORIZED

    # return HTTP response
    if response is None:
        msg = {'status': 'NG', 'message': 'Could not communicate with device'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nERROR Could not communicate with device [{}, {}]\r\n'.format(username, devicename))
        return response, status.HTTP_401_UNAUTHORIZED

    print(response)
    msg = {'status': 'OK', 'message': 'Device accessed successfully.'}
    if new_token:
        msg['new_token'] = new_token
    try:
        msg['value'] = (json.loads(response))["value"]
        response = json.dumps(msg)
    except:
        response = json.dumps(msg)
    return response


def process_request(api, data):

    #print("\r\nAPI: {} request={}".format(api, data))
    print("\r\nAPI: {} username={}".format(api, data['username']))

    username = data['username']
    token = data['token']
    devicename = data['devicename']

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    # check if device is registered
    if not g_database_client.find_device(username, devicename):
        response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
        print('\r\nERROR Device is not registered [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    # get deviceid for subscribe purpose (AMQP)
    deviceid = g_database_client.get_deviceid(username, devicename)

    # construct publish/subscribe topics and payloads
    pubtopic = generate_publish_topic(data, deviceid, api, CONFIG_SEPARATOR)
    payload = generate_publish_payload(data)
    subtopic = generate_subscribe_topic(pubtopic, CONFIG_SEPARATOR)

    try:
        # subscribe for response
        ret = g_messaging_client.subscribe(subtopic, subscribe=True, deviceid=deviceid)
        if ret:
            # publish request
            g_messaging_client.publish(pubtopic, payload)

            # receive response
            response = receive_message(subtopic)
            g_messaging_client.subscribe(subtopic, subscribe=False)
        else:
            msg = {'status': 'NG', 'message': 'Could not communicate with device'}
            if new_token:
                msg['new_token'] = new_token
            response = json.dumps(msg)
            print('\r\nERROR Could not communicate with device [{}, {}]\r\n'.format(username, devicename))
            return response, status.HTTP_401_UNAUTHORIZED
    except:
        msg = {'status': 'NG', 'message': 'Could not communicate with device'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nERROR Could not communicate with device [{}, {}]\r\n'.format(username, devicename))
        return response, status.HTTP_401_UNAUTHORIZED

    # return HTTP response
    if response is None:
        msg = {'status': 'NG', 'message': 'Could not communicate with device'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nERROR Could not communicate with device [{}, {}]\r\n'.format(username, devicename))
        return response, status.HTTP_401_UNAUTHORIZED

    print(response)
    msg = {'status': 'OK', 'message': 'Device accessed successfully.'}
    if new_token:
        msg['new_token'] = new_token
    try:
        msg['value'] = (json.loads(response))["value"]
        response = json.dumps(msg)
    except:
        response = json.dumps(msg)
    return response


# Authorization header for username and password
def get_auth_header_user_pass():
    auth_header = flask.request.headers.get('Authorization')
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
    #return get_base64encode_user_pass(token[1]) #change Bearer to Basic


# Authorization header: Bearer JWT
def get_jwtencode_user_pass(token):
    payload = jwt.decode(token, "iotmodembrtchip0iotmodembrtchip0", algorithms=['HS256'])
    if payload is None:
        reason = "JWT decode failed"
        print(reason)
        return None, None, reason
    if not payload.get("username"):
        reason = "No username field"
        print(reason)
        return None, None, reason
    if not payload.get("password"):
        reason = "No password field"
        print(reason)
        return None, None, reason
    if not payload.get("iat"):
        reason = "No iat field"
        print(reason)
        return None, None, reason
    if not payload.get("exp"):
        reason = "No exp field"
        print(reason)
        return None, None, reason

    currepoch = int(time.time())+2
    print("username: {}".format(payload["username"]))
    print("password: {}".format(payload["password"]))
    print("cur: {}".format(currepoch))
    print("iat: {}".format(payload["iat"]))
    print("exp: {}".format(payload["exp"]))

    if payload["exp"] - payload["iat"] != 10:
        reason = "JWT expiration date is incorrect"
        print(reason)
        return None, None, reason
    if currepoch < payload["iat"]:
        print("username: {}".format(payload["username"]))
        print("password: {}".format(payload["password"]))
        print("cur: {}".format(currepoch))
        print("iat: {}".format(payload["iat"]))
        print("exp: {}".format(payload["exp"]))
        reason = "currepoch({}) < payload[iat]({})".format(currepoch, payload["iat"])
        return None, None, reason
    elif currepoch > payload["exp"]:
        print("username: {}".format(payload["username"]))
        print("password: {}".format(payload["password"]))
        print("cur: {}".format(currepoch))
        print("iat: {}".format(payload["iat"]))
        print("exp: {}".format(payload["exp"]))
        reason = "currepoch({}) > payload[exp]({})".format(currepoch, payload["exp"])
        return None, None, reason
    return payload["username"], payload["password"], ""


# Authorization header: Basic Base64
def get_base64encode_user_pass(token):
    decoded = base64.b64decode(token)
    user_pass = decoded.decode("utf-8").split(":")
    return user_pass[0], user_pass[1], ""


# Authorization header for the access token
def get_auth_header_token():
    auth_header = flask.request.headers.get('Authorization')
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
    #print("auth header: {}".format(token[1]))
    return token[1]



###################################################################################
# MQ User/Device Management functions
###################################################################################

def mq_adduser(auth64, deviceid, serialnumber):
    conn = http.client.HTTPConnection(config.CONFIG_HOST, config.CONFIG_MGMT_PORT)
    header = { "Authorization": auth64, "Content-Type": "application/json" }

    api = "/api/users/{}".format(deviceid)
    params = { "password": serialnumber, "tags": "" }

    conn.request("PUT", api, json.dumps(params), header)
    response = conn.getresponse()
    if (response.status != 201):
        print(response.status)
        return False

    return True

def mq_removeuser(auth64, deviceid):
    conn = http.client.HTTPConnection(config.CONFIG_HOST, config.CONFIG_MGMT_PORT)
    header = { "Authorization": auth64 }

    api = "/api/users/{}".format(deviceid)

    conn.request("DELETE", api, None, header)
    response = conn.getresponse()
    if (response.status != 204):
        print(response.status)
        return False

    return True

def mq_setpermission(auth64, deviceid):
    conn = http.client.HTTPConnection(config.CONFIG_HOST, config.CONFIG_MGMT_PORT)
    header = { "Authorization": auth64, "Content-Type": "application/json" }

    api = "/api/permissions/%2F/{}".format(deviceid)
    params = { "configure": ".*", "write": ".*", "read": ".*" }

    conn.request("PUT", api, json.dumps(params), header)
    response = conn.getresponse()
    if (response.status != 201):
        print(response.status)
        return False

    return True

def mq_settopicpermission(auth64, deviceid):
    conn = http.client.HTTPConnection(config.CONFIG_HOST, config.CONFIG_MGMT_PORT)
    header = { "Authorization": auth64, "Content-Type": "application/json" }

    api = "/api/topic%2Dpermissions/%2F/{}".format(deviceid)
    pubtopic = "^server.{}.*".format(deviceid)
    subtopic = "{}.#".format(deviceid)
    params = {"exchange": "amq.topic", "write": pubtopic, "read": subtopic }

    conn.request("PUT", api, json.dumps(params), header)
    response = conn.getresponse()
    if (response.status != 201):
        print(response.status)
        return False

    return True


######

def message_broker_register(deviceid, serialnumber):
    if config.CONFIG_ENABLE_MQ_SECURITY:
        account = config.CONFIG_MGMT_ACCOUNT
        auth64 = "Basic {}".format(str(base64.urlsafe_b64encode(account.encode("utf-8")), "utf-8"))
        result = mq_adduser(auth64, deviceid, serialnumber)
        if not result:
            print("mq_adduser fails")
            return result
        result = mq_setpermission(auth64, deviceid)
        if not result:
            print("mq_setpermission fails")
            return result
        result = mq_settopicpermission(auth64, deviceid)
        if not result:
            print("mq_settopicpermission fails")
            return result
    return True

def message_broker_unregister(deviceid):
    if config.CONFIG_ENABLE_MQ_SECURITY:
        account = config.CONFIG_MGMT_ACCOUNT
        auth64 = "Basic {}".format(str(base64.urlsafe_b64encode(account.encode("utf-8")), "utf-8"))
        return mq_removeuser(auth64, deviceid)
    return True

######



###################################################################################
# MQTT/AMQP callback functions
###################################################################################

def on_mqtt_message(client, userdata, msg):
    if CONFIG_PREPEND_REPLY_TOPIC == '':
        g_queue_dict[msg.topic] = msg.payload
        print("RCV: {}".format(g_queue_dict))
    else:
        index = msg.topic.find(CONFIG_PREPEND_REPLY_TOPIC)
        if index == 0:
            g_queue_dict[msg.topic] = msg.payload
            print("RCV: {}".format(g_queue_dict))

def on_amqp_message(ch, method, properties, body):
    #print("RCV: {} {}".format(method.routing_key, body))
    g_queue_dict[method.routing_key] = body
    print("RCV: {}".format(g_queue_dict))

def receive_message(topic):
    time.sleep(1)
    i = 0
    while True:
        try:
            data = g_queue_dict[topic].decode("utf-8")
            g_queue_dict.pop(topic)
            print("API: response={}\r\n".format(data))
            return data
        except:
            #print("x")
            time.sleep(1)
            i += 1
        if i >= 3:
            print("receive_message timed_out")
            break
    return None



###################################################################################
# Main entry point
###################################################################################

def initialize():
    global CONFIG_SEPARATOR
    global g_messaging_client
    global g_database_client

    CONFIG_SEPARATOR = "." if config.CONFIG_USE_AMQP==1 else "/"

    # Initialize Message broker client
    print("Using {} for webserver-messagebroker communication!".format("AMQP" if config.CONFIG_USE_AMQP else "MQTT"))
    if config.CONFIG_USE_AMQP:
        g_messaging_client = messaging_client(config.CONFIG_USE_AMQP, on_amqp_message)
        g_messaging_client.set_server(config.CONFIG_HOST, config.CONFIG_AMQP_TLS_PORT)
    else:
        g_messaging_client = messaging_client(config.CONFIG_USE_AMQP, on_mqtt_message)
        g_messaging_client.set_server(config.CONFIG_HOST, config.CONFIG_MQTT_TLS_PORT)
    if config.CONFIG_USERNAME and config.CONFIG_PASSWORD:
        g_messaging_client.set_user_pass(config.CONFIG_USERNAME, config.CONFIG_PASSWORD)
    g_messaging_client.set_tls(config.CONFIG_TLS_CA, config.CONFIG_TLS_CERT, config.CONFIG_TLS_PKEY)
    while True:
        try:
            result = g_messaging_client.initialize(timeout=5)
            if not result:
                print("Could not connect to message broker!")
            else:
                break
        except:
            print("Could not connect to message broker! exception!")

    # Initialize Database client
    g_database_client = database_client()
    g_database_client.initialize()



# Initialize globally so that no issue with GUnicorn integration
if os.name == 'posix':
    initialize()


if __name__ == '__main__':

    if os.name == 'nt':
        initialize()

    # Initialize HTTP server
    if config.CONFIG_HTTP_USE_TLS:
        context = (config.CONFIG_HTTP_TLS_CERT, config.CONFIG_HTTP_TLS_PKEY)
        port = config.CONFIG_HTTP_TLS_PORT
    else:
        context = None
        port = config.CONFIG_HTTP_PORT
    app.run(ssl_context = context,
        host     = config.CONFIG_HTTP_HOST, 
        port     = port, 
        threaded = True, 
        debug    = True)


