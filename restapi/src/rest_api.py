import os
import ssl
import json
import time
import hmac
import hashlib
import flask
import base64
import datetime
from flask_json import FlaskJSON, JsonError, json_response, as_json
from certificate_generator import certificate_generator
from messaging_client import messaging_client
from rest_api_config import config
from database import database_client
from flask_cors import CORS
from flask_api import status
from jose import jwk, jwt
import http.client
from s3_client import s3_client
#import redis



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
g_storage_client = None
#g_redis_client = None
g_queue_dict  = {}
app = flask.Flask(__name__)
CORS(app)



###################################################################################
# i2c device classes
###################################################################################

I2C_DEVICE_CLASS_SPEAKER       = 0
I2C_DEVICE_CLASS_DISPLAY       = 1
I2C_DEVICE_CLASS_LIGHT         = 2
I2C_DEVICE_CLASS_POTENTIOMETER = 3
I2C_DEVICE_CLASS_TEMPERATURE   = 4
I2C_DEVICE_CLASS_HUMIDITY      = 5
I2C_DEVICE_CLASS_ANEMOMETER    = 6
I2C_DEVICE_CLASS_BATTERY       = 7
I2C_DEVICE_CLASS_FLUID         = 8



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
#   {'status': 'OK', 'message': string, 'token': {'access': string, 'id': string, 'refresh': string}, 'name': string }
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
        return response, status.HTTP_401_UNAUTHORIZED
    print('login username={} password={}'.format(username, password))

    # check if a parameter is empty
    if len(username) == 0 or len(password) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Login: Empty parameter found [{}]\r\n'.format(username))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username does not exist
    if not g_database_client.find_user(username):
        # NOTE:
        # its not good to provide a specific error message for LOGIN
        # because it provides additional info for hackers
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Login: Username does not exist [{}]\r\n'.format(username))
        return response, status.HTTP_404_NOT_FOUND

    # check if password is valid
    access, refresh, id = g_database_client.login(username, password)
    if not access:
        # NOTE:
        # its not good to provide a specific error message for LOGIN
        # because it provides additional info for hackers
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Login: Password is incorrect [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    # return name during login as per special request
    name = None
    info = g_database_client.get_user_info(access)
    if info:
        # handle no family name
        if 'given_name' in info:
            name = info['given_name']
        if 'family_name' in info:
            if info['family_name'] != "NONE":
                name += " " + info['family_name']

    msg = {'status': 'OK', 'message': "Login successful", 'token': {'access': access, 'refresh': refresh, 'id': id} }
    if name is not None:
        msg['name'] = name
    response = json.dumps(msg)
    #print('\r\nLogin successful: {}\r\n'.format(username))
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
        return response, status.HTTP_401_UNAUTHORIZED
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
        if g_database_client.is_email_verified(username):
            response = json.dumps({'status': 'NG', 'message': 'Username already exists'})
            print('\r\nERROR Signup: Username already exists [{}]\r\n'.format(username))
            return response, status.HTTP_409_CONFLICT
        else:
            # user already signed up but unverified, so delete the user for signup to proceed
            g_database_client.admin_delete_user(username)

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
        return response, status.HTTP_500_INTERNAL_SERVER_ERROR

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
    if len(username) == 0 or len(confirmationcode) != 6:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Confirm Signup: Empty parameter found [{}]\r\n'.format(username))
        return response, status.HTTP_400_BAD_REQUEST

    # confirm user in database
    result = g_database_client.confirm_user(username, confirmationcode)
    if not result:
        response = json.dumps({'status': 'NG', 'message': 'Invalid code'})
        print('\r\nERROR Confirm Signup: Invalid code [{},{}]\r\n'.format(username, confirmationcode))
        return response, status.HTTP_500_INTERNAL_SERVER_ERROR

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
        return response, status.HTTP_500_INTERNAL_SERVER_ERROR

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
        return response, status.HTTP_500_INTERNAL_SERVER_ERROR

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
        return response, status.HTTP_401_UNAUTHORIZED
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
        return response, status.HTTP_500_INTERNAL_SERVER_ERROR

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
    print('\r\nLogout')

    try:
        # get token from Authorization header
        auth_header_token = get_auth_header_token()
        if auth_header_token:
            token = {'access': auth_header_token}

            # get username from token
            username = g_database_client.get_username_from_token(token)
            if username is not None:
                # delete mobile device tokens
                g_database_client.delete_mobile_device_token(username)
                print('\r\nDeleted mobile device token\r\n')

            g_database_client.logout(token['access'])
            print('\r\nLogout successful\r\n')
    except:
        print('\r\nERROR Logout: exception\r\n')

    return json.dumps({'status': 'OK', 'message': 'User logout successfully.'})


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
        print('\r\nERROR Userinfo: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Userinfo: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    print('get_user_info username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Userinfo: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2: # token expired
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Userinfo: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Userinfo: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    if new_token:
        info = g_database_client.get_user_info(new_token['access'])
    else:
        info = g_database_client.get_user_info(token['access'])

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
        print('\r\nERROR Delete user: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Delete user: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('delete_user username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Delete user: Empty parameter found\r\n')
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2: # token expired
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Delete user: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Delete user: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    # delete the user in cognito
    if new_token:
        result = g_database_client.delete_user(username, new_token['access'])
    else:
        result = g_database_client.delete_user(username, token['access'])
    if result == False:
        response = json.dumps({'status': 'NG', 'message': 'Delete user failed internal error'})
        print('\r\nERROR Delete user: Internal error [{}]\r\n'.format(username))
        return response, status.HTTP_500_INTERNAL_SERVER_ERROR

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
        print('\r\nERROR Refresh token: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    #print('refresh_user_token')

    # check if a parameter is empty
    if len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Refresh token: Empty parameter found\r\n')
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response, status.HTTP_400_BAD_REQUEST

    # get refresh and id token
    data = flask.request.get_json()
    if not data.get("refresh") or not data.get("id"):
        response = json.dumps({'status': 'NG', 'message': 'Refresh and ID tokens are not provided'})
        print('\r\nERROR Refresh token: Refresh and ID tokens are not provided\r\n')
        return response, status.HTTP_400_BAD_REQUEST
    token['refresh'] = data['refresh']
    token['id'] = data['id']

    # refresh the access token
    new_token = g_database_client.refresh_token(token)
    if new_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Refresh token invalid'})
        print('\r\nERROR Refresh token: Token expired. DATETIME {}\r\n\r\n'.format(datetime.datetime.now()))
        return response, status.HTTP_500_INTERNAL_SERVER_ERROR

    msg = {'status': 'OK', 'message': 'Refresh token successful.', 'token': new_token}
    response = json.dumps(msg)
    print('\r\nRefresh token successful DATETIME {}\r\n'.format(datetime.datetime.now()))
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
        print('\r\nERROR Verify phone: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Verify phone: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('refresh_user_token username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Verify phone: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2: # token expired
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Verify phone: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Verify phone: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    # verify phone number
    result = g_database_client.request_verify_phone_number(token["access"])
    if not result:
        response = json.dumps({'status': 'NG', 'message': 'Request failed'})
        print('\r\nERROR Verify phone: Request failed [{}]\r\n'.format(username))
        return response, status.HTTP_500_INTERNAL_SERVER_ERROR

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
        print('\r\nERROR Confirm verify phone: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Confirm verify phone: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('confirm_verify_phone_number username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Confirm verify phone: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2: # token expired
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Confirm verify phone: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Confirm verify phone: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    data = flask.request.get_json()

    # confirm verify phone number
    result = g_database_client.confirm_verify_phone_number(token["access"], data["confirmationcode"])
    if not result:
        response = json.dumps({'status': 'NG', 'message': 'Request failed'})
        print('\r\nERROR Confirm verify phone: Request failed [{}]\r\n'.format(username))
        return response, status.HTTP_500_INTERNAL_SERVER_ERROR

    # update notifications for all devices to contain new phone number (for UART only)
    try:
        info = g_database_client.get_user_info(token['access'])
        devices = g_database_client.get_devices(username)
        sources = ["uart"]
        for source in sources:
            for device in devices:
                notification = g_database_client.get_device_notification(username, device["devicename"], source)
                if notification is not None:
                    if info is not None:
                        if info.get("phone_number"):
                            notification["endpoints"]["mobile"]["recipients"] = info["phone_number"]
                            notification["endpoints"]["mobile"]["recipients_list"] = []
                            notification["endpoints"]["mobile"]["recipients_list"].append({ "to": info["phone_number"], "group": False })
                            notification["endpoints"]["notification"]["recipients"] = info["phone_number"]
                            notification["endpoints"]["notification"]["recipients_list"] = []
                            notification["endpoints"]["notification"]["recipients_list"].append({ "to": info["phone_number"], "group": False })
                        if info.get("phone_number_verified"):
                            notification["endpoints"]["mobile"]["enable"] = info["phone_number_verified"]
                            notification["endpoints"]["notification"]["enable"] = False
                        g_database_client.update_device_notification(username, device["devicename"], source, notification)
    except:
        print("exception")
        pass

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
        print('\r\nERROR Change password: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Change password: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('refresh_user_token username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Change password: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2: # token expired
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Change password: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Change password: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

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
        return response, status.HTTP_500_INTERNAL_SERVER_ERROR

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
        print('\r\nERROR Update user: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Update user: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('refresh_user_token username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Update user: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2: # token expired
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Update user: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Update user: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    # get the input parameters
    data = flask.request.get_json()
    if data.get('phone_number'):
        phonenumber = data['phone_number']
    else:
        phonenumber = None
    #print(phonenumber)
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
        return response, status.HTTP_500_INTERNAL_SERVER_ERROR

    response = json.dumps({'status': 'OK', 'message': 'Change password successful'})
    print('\r\nUpdate user successful: {}\r\n{}\r\n'.format(username, response))
    return response


########################################################################################################
#
# REGISTER DEVICE TOKEN
#
# - Request:
#   POST /mobile/devicetoken
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: {'token': jwtEncode(devicetoken, service)}
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/mobile/devicetoken', methods=['POST'])
def register_mobile_device_token():
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Register mobile device token: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Register mobile device token: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('register_mobile_device_token username={}'.format(username))

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2: # token expired
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Register mobile device token: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Register mobile device token: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    # decode the devicetoken and service
    data = flask.request.get_json()
    if data.get("token") is None:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Register mobile device token: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST
    if len(data["token"]) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found 2'})
        print('\r\nERROR Register mobile device token: Empty parameter found 2\r\n')
        return response, status.HTTP_400_BAD_REQUEST
    devicetoken, service, reason = get_jwtencode_user_pass(data["token"])
    if devicetoken is None or service is None:
        response = json.dumps({'status': 'NG', 'message': reason})
        print('\r\nERROR Register mobile device token: Devicetoken, service format invalid\r\n')
        return response, status.HTTP_400_BAD_REQUEST
    if service != "APNS" and service != "GCM":
        response = json.dumps({'status': 'NG', 'message': reason})
        print('\r\nERROR Register mobile device token: Service value is invalid\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # add mobile device token
    g_database_client.add_mobile_device_token(username, devicetoken, service)
    print('\r\nAdded mobile device token\r\n')

    response = json.dumps({'status': 'OK', 'message': 'Register mobile device token successful'})
    print('\r\nRegister mobile device token successful: {}\r\n{}\r\n'.format(username, response))
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
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get Subscription: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_subscription {}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get Subscription: Empty parameter found\r\n')
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get Subscription: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get Subscription: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    subscription = g_database_client.get_subscription(username)
    #print(subscription)
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
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Set Subscription: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('set_subscription {}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Set Subscription: Empty parameter found\r\n')
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Set Subscription: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Set Subscription: Token is invalid [{}]\r\n'.format(username))
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response, status.HTTP_401_UNAUTHORIZED

    subscription = g_database_client.set_subscription(username, credits)
    #print(subscription)
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
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Paypal Setup: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('set_payment_paypal_setup {}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Paypal Setup: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Paypal Setup: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Paypal Setup: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    #print(payment)
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
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Paypal Execute: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('set_payment_paypal_execute {}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Paypal Execute: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Paypal Execute: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Paypal Execute: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    #print(payment)
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
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Paypal Verify: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('set_payment_paypal_verify {}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Paypal Verify: Empty parameter found\r\n')
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Paypal Verify: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Paypal Verify: Token is invalid [{}]\r\n'.format(username))
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response, status.HTTP_401_UNAUTHORIZED

    #print(payment)
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
#   {'status': 'OK', 'message': string, 'devices': array[{'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': string, 'heartbeat': string, 'version': string}, ...]}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices', methods=['GET'])
def get_device_list():
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get Devices: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get Devices: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_device_list {}'.format(username))

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


    #start_time = time.time()
    devices = g_database_client.get_devices(username)
    #print(time.time()-start_time)


    msg = {'status': 'OK', 'message': 'Devices queried successfully.', 'devices': devices}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('get_device_list {} {} devices'.format(username, len(devices)))
    return response

########################################################################################################
# 
# GET DEVICES FILTERED
#
# - Request:
#   GET /devices/filter/FILTERSTRING
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'devices': array[{'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': string, 'heartbeat': string, 'version': string}, ...]}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/filter/<filter>', methods=['GET'])
def get_device_list_filtered(filter):
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get Devices: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get Devices: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_device_list_filtered {}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(filter) == 0:
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


    #start_time = time.time()
    devices = g_database_client.get_devices_with_filter(username, filter)
    #print(time.time()-start_time)


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
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Add/Delete Device: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('register_device {} devicename={}'.format(username, devicename))

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
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Add/Delete Device: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    if flask.request.method == 'POST':
        # check parameters
        data = flask.request.get_json()
        #print(data)
        if not data.get("deviceid") or not data.get("serialnumber"):
            response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
            print('\r\nERROR Add Device: Parameters not included [{},{}]\r\n'.format(username, devicename))
            return response, status.HTTP_400_BAD_REQUEST
        #print(data["deviceid"])
        #print(data["serialnumber"])

        # check if device is registered
        # a user cannot register the same device name
        if g_database_client.find_device(username, devicename):
            response = json.dumps({'status': 'NG', 'message': 'Device name is already taken'})
            print('\r\nERROR Add Device: Device name is already taken [{},{}]\r\n'.format(username, devicename))
            return response, status.HTTP_409_CONFLICT

        # check if device is registered
        # a user cannot register a device if it is already registered by another user
        if g_database_client.find_device_by_id(data["deviceid"]):
            response = json.dumps({'status': 'NG', 'message': 'Device UUID is already registered'})
            print('\r\nERROR Add Device: Device uuid is already registered[{}]\r\n'.format(data["deviceid"]))
            return response, status.HTTP_409_CONFLICT

        # TODO: check if UUID and serial number matches

        # add device to database
        result = g_database_client.add_device(username, devicename, data["deviceid"], data["serialnumber"])
        #print(result)
        if not result:
            response = json.dumps({'status': 'NG', 'message': 'Device could not be registered'})
            print('\r\nERROR Add Device: Device could not be registered [{},{}]\r\n'.format(username, devicename))
            return response, status.HTTP_400_BAD_REQUEST

        # add and configure message broker user
        try:
            # if secure is True, device will only be able to publish and subscribe to server/<deviceid>/# and <deviceid>/# respectively
            # this means a hacker can only hack that particular device and will not be able to eavesdrop on other devices
            # if secure is False, device will be able to publish and subscribe to/from other devices which enables multi-subscriptions
            secure = True
            result = message_broker_register(data["deviceid"], data["serialnumber"], secure)
            #print(result)
            if not result:
                response = json.dumps({'status': 'NG', 'message': 'Device could not be registered in message broker'})
                print('\r\nERROR Add Device: Device could not be registered  in message broker [{},{}]\r\n'.format(username, devicename))
                return response, status.HTTP_500_INTERNAL_SERVER_ERROR
        except:
            pass

        # add default uart notification recipients
        # this is necessary so that an entry exist for consumption of notification manager
        source = "uart"
        notification = g_database_client.get_device_notification(username, devicename, source)
        if notification is None:
            notification = build_default_notifications(source, token)
            if notification is not None:
                g_database_client.update_device_notification(username, devicename, source, notification)

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
            return response, status.HTTP_404_NOT_FOUND

        # delete device sensors and related information
        sensors = g_database_client.get_all_device_sensors(username, devicename)
        if sensors is not None:
            for sensor in sensors:
                if sensor.get("source") and sensor.get("number") and sensor.get("sensorname"):
                    delete_sensor(username, devicename, sensor["source"], sensor["number"], sensor["sensorname"], sensor)

        # delete device from database
        g_database_client.delete_device(username, devicename)

        # delete message broker user
        try:
            # no checking needed
            message_broker_unregister(device["deviceid"])
        except:
            pass

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
#   {'status': 'OK', 'message': string, 'device': {'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': string, 'heartbeat': string, 'version': string}}
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
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get Device: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_device {} devicename={}'.format(username, devicename))

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
        return response, status.HTTP_404_NOT_FOUND


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

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get Histories: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_user_histories {}'.format(username))

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
    #print(histories)


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
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get Histories: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_user_histories {}'.format(username))

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
    #print(histories)


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
#   { 'status': 'OK', 'message': string, 'value': { 'status': int, 'version': string } }
#   { 'status': 'NG', 'message': string, 'value': { 'heartbeat': string, 'version': string} }
#
@app.route('/devices/device/<devicename>/status', methods=['GET'])
def get_status(devicename):
    api = 'get_status'

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
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username
    #print('get_status {} devicename={}'.format(data['username'], data['devicename']))

    response, status_return = process_request_get(api, data)
    if status_return == 503: # HTTP_503_SERVICE_UNAVAILABLE
        # if device is unreachable, get the cached heartbeat and version
        cached_value = g_database_client.get_device_cached_values(username, devicename)
        if not cached_value:
            response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
            print('\r\nERROR Device is not registered [{},{}]\r\n'.format(username, devicename))
            return response, status.HTTP_404_NOT_FOUND
        response = json.loads(response)
        response['value'] = cached_value
        response = json.dumps(response)
        return response, status_return

    if status_return == 200:
        response = json.loads(response)
        version = response["value"]["version"]
        response = json.dumps(response)
        g_database_client.save_device_version(username, devicename, version)

    return response

#
# SET STATUS
# - Request:
#   POST /devices/device/<devicename>/status
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'status': int }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': {'status': string} }
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

    # get parameter input
    data = flask.request.get_json()

    # check parameter input
    if data['status'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Set status: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get username from token
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    data['username'] = g_database_client.get_username_from_token(data['token'])
    if data['username'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('set_status {} devicename={}'.format(data['username'], data['devicename']))

    return process_request(api, data)

#
# GET SETTINGS
# - Request:
#   GET /devices/device/<devicename>/settings
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/settings', methods=['GET'])
def get_settings(devicename):
    api = 'get_settings'

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
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username
    print('get_settings {} devicename={}'.format(data['username'], data['devicename']))

    return process_request_get(api, data)

#
# SET SETTINGS
# - Request:
#   POST /devices/device/<devicename>/settings
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'status': int }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': { 'sensorrate': int } }
#   { 'status': 'NG', 'message': string}
#
@app.route('/devices/device/<devicename>/settings', methods=['POST'])
def set_settings(devicename):
    api = 'set_settings'

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get parameter input
    data = flask.request.get_json()

    # get username from token
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    data['username'] = g_database_client.get_username_from_token(data['token'])
    if data['username'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('set_settings {} devicename={}'.format(data['username'], data['devicename']))

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
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = {}
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    data['username'] = g_database_client.get_username_from_token(data['token'])
    if data['username'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_ip {}'.format(data['username']))

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
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = {}
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    data['username'] = g_database_client.get_username_from_token(data['token'])
    if data['username'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_subnet {}'.format(data['username']))

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
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = {}
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    data['username'] = g_database_client.get_username_from_token(data['token'])
    if data['username'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_gateway {}'.format(data['username']))

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
    if data['username'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_mac {}'.format(data['username']))

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
    if data['username'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_gpio {}'.format(data['username']))

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
    if data['username'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('set_gpio {}'.format(data['username']))

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
    if data['username'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_rtc {}'.format(data['username']))

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
    if data['username'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('write_uart {}'.format(data['username']))

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
    if data['username'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('trigger_notification {}'.format(data['username']))

    return process_request(api, data)



#########################

def build_default_notifications(type, token):
    notifications = {}

    if type == "uart":
        notifications["messages"] = [
            {
                "message": "Hello World", 
                "enable": True
            }
        ]
    else: # gpio, i2c, adc, 1wire, tprobe
        notifications["messages"] = [
            {
                "message": "Hello World", 
                "enable": True
            }, 
            {
                "message": "Hi World", 
                "enable": False
            }
        ]

    notifications["endpoints"] = {
        "mobile": {
            "recipients": "",
            "recipients_list" : [],
            "enable": False
        },
        "email": {
            "recipients": "",
            "recipients_list" : [],
            "enable": False
        },
        "notification": {
            "recipients": "",
            "recipients_list" : [],
            "enable": False
        },
        "modem": {
            "recipients": "",
            "recipients_list" : [],
            "enable": False
        },
        "storage": {
            "recipients": "",
            "recipients_list" : [],
            "enable": False
        },
    }

    info = g_database_client.get_user_info(token['access'])
    if info is None:
        return None

    if info.get("email"):
        notifications["endpoints"]["email"]["recipients"] = info["email"]
        notifications["endpoints"]["email"]["recipients_list"].append({ "to": info["email"], "group": False })

    if info.get("email_verified"):
        notifications["endpoints"]["email"]["enable"] = info["email_verified"]

    if info.get("phone_number"):
        notifications["endpoints"]["mobile"]["recipients"] = info["phone_number"]
        notifications["endpoints"]["mobile"]["recipients_list"].append({ "to": info["phone_number"], "group": False })
        #notifications["endpoints"]["notification"]["recipients"] = info["phone_number"]
        #notifications["endpoints"]["notification"]["recipients_list"].append({ "to": info["phone_number"], "group": False })

    if info.get("phone_number_verified"):
        notifications["endpoints"]["mobile"]["enable"] = info["phone_number_verified"]
        #notifications["endpoints"]["notification"]["enable"] = False

    return notifications


#
# GET UARTS
#
# - Request:
#   GET /devices/device/<devicename>/uarts
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 
#     'value': { 
#       'uarts': [
#         {'enabled': int}, 
#       ]
#     }
#   }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/uarts', methods=['GET'])
def get_uarts(devicename):
    api = 'get_uarts'

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    data = {}
    data['token'] = token
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username
    print('get_uarts {} devicename={}'.format(data['username'], data['devicename']))

    return process_request(api, data)


#
# GET UART PROPERTIES
#
# - Request:
#   GET /devices/device/<devicename>/uart/properties
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': { 'baudrate': int, 'parity': int, 'flowcontrol': int, 'stopbits': int, 'databits': int } }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/uart/properties', methods=['GET'])
def get_uart_prop(devicename):
    api = 'get_uart_prop'

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    data = {}
    data['token'] = token
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username
    print('get_uart_prop {} devicename={}'.format(data['username'], data['devicename']))

    response, status_return = process_request(api, data)
    if status_return != 200:
        return response, status_return

    source = "uart"
    notification = g_database_client.get_device_notification(username, devicename, source)
    if notification is not None:
        if notification["endpoints"]["modem"].get("recipients_id"):
            notification["endpoints"]["modem"].pop("recipients_id")
        #print(notification)
        # notification recipients should be empty
        if notification["endpoints"]["notification"].get("recipients"):
            notification["endpoints"]["notification"]["recipients"] = ""
        response = json.loads(response)
        response['value']['notification'] = notification
        response = json.dumps(response)
    else:
        response = json.loads(response)
        response['value']['notification'] = build_default_notifications("uart", token)
        response = json.dumps(response)

    return response


#
# SET UART PROPERTIES
#
# - Request:
#   POST /devices/device/<devicename>/uart/properties
#   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
#   data: { 'baudrate': int, 'parity': int, 'flowcontrol': int, 'stopbits': int, 'databits': int }
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/uart/properties', methods=['POST'])
def set_uart_prop(devicename):
    api = 'set_uart_prop'

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = flask.request.get_json()
    #print(data)
    if data['baudrate'] is None or data['parity'] is None or data['databits'] is None or data['stopbits'] is None or data['flowcontrol'] is None or data['notification'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST
    #print(data['baudrate'])
    #print(data['parity'])
    #print(data['notification'])

    # get notifications and remove from list
    notification = data['notification']
    #print(notification)
    data.pop('notification')
    #print(notification)
    #print(data)

    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username
    print('set_uart_prop {} devicename={}'.format(data['username'], data['devicename']))

    response, status_return = process_request(api, data)
    if status_return != 200:
        return response, status_return

    source = "uart"
    item = g_database_client.update_device_notification(username, devicename, source, notification)

    # update device configuration database for device bootup
    #print("data={}".format(data))
    item = g_database_client.update_device_peripheral_configuration(username, devicename, "uart", 1, None, None, None, data)

    return response


#
# ENABLE/DISABLE UART
#
# - Request:
#   POST /devices/device/DEVICENAME/uart/enable
#   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
#   data: { 'enable': int }
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/uart/enable', methods=['POST'])
def enable_uart(devicename):
    api = 'enable_uart'

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = flask.request.get_json()

    # check parameter input
    if data['enable'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username
    print('enable_uart {} devicename={}'.format(data['username'], data['devicename']))

    return process_request(api, data)


#
# GET GPIOS
#
# - Request:
#   GET /devices/device/<devicename>/gpios
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 
#     'value': { 
#       'voltage': int,
#       'gpios': [
#         {'direction': int, 'status': int}, 
#         {'direction': int, 'status': int}, 
#         {'direction': int, 'status': int}, 
#         {'direction': int, 'status': int}
#       ]
#     }
#   }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/gpios', methods=['GET'])
def get_gpios(devicename):
    api = 'get_gpios'

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    data = {}
    data['token'] = token
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username
    print('get_gpios {} devicename={}'.format(data['username'], data['devicename']))

    return process_request(api, data)


#
# GET GPIO PROPERTIES
#
# - Request:
#   GET /devices/device/<devicename>/gpio/<number>/properties
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': { 'direction': int, 'mode': int, 'alert': int, 'alertperiod': int } }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/gpio/<number>/properties', methods=['GET'])
def get_gpio_prop(devicename, number):
    api = 'get_gpio_prop'

    # check number parameter
    number = int(number)
    if number > 4 or number < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    data = {}
    data['token'] = token
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username
    data['number'] = number
    print('get_gpio_prop {} devicename={}'.format(data['username'], data['devicename']))

    response, status_return = process_request(api, data)
    if status_return != 200:
        return response, status_return

    source = "gpio{}".format(number)
    notification = g_database_client.get_device_notification(username, devicename, source)
    if notification is not None:
        response = json.loads(response)
        response['value']['notification'] = notification
        response = json.dumps(response)
    else:
        response = json.loads(response)
        response['value']['notification'] = build_default_notifications("gpio", token)
        response = json.dumps(response)

    return response


#
# SET GPIO PROPERTIES
#
# - Request:
#   POST /devices/device/<devicename>/gpio/<number>/properties
#   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
#   data: { 'direction': int, 'mode': int, 'alert': int, 'alertperiod': int }
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/gpio/<number>/properties', methods=['POST'])
def set_gpio_prop(devicename, number):
    api = 'set_gpio_prop'

    # check number parameter
    number = int(number)
    if number > 4 or number < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = flask.request.get_json()
    #print(data)
    if data['direction'] is None or data['mode'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST
    if data['direction'] == 0: # INPUT
        if data['alert'] is None or data['alertperiod'] is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
            print('\r\nERROR Invalid parameters\r\n')
            return response, status.HTTP_400_BAD_REQUEST
        if data['alertperiod'] < 5000:
            response = json.dumps({'status': 'NG', 'message': 'Invalid parameters: alert period should be >= 5000 milliseconds'})
            print('\r\nERROR Invalid parameters\r\n')
            return response, status.HTTP_400_BAD_REQUEST
    elif data['direction'] == 1: # OUTPUT
        # If OUTPUT, polarity must be present
        if data['polarity'] is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
            print('\r\nERROR Invalid parameters\r\n')
            return response, status.HTTP_400_BAD_REQUEST
        # If MODE is PULSE, width must be present
        # If MODE is CLOCK, mark and space must be present
        if data['mode'] == 1: # PULSE
            if data['width'] is None:
                response = json.dumps({'status': 'NG', 'message': 'Invalid parameters: width should be present'})
                print('\r\nERROR Invalid parameters\r\n')
                return response, status.HTTP_400_BAD_REQUEST
            if data['width'] == 0:
                response = json.dumps({'status': 'NG', 'message': 'Invalid parameters: width should be > 0 when mode is 1'})
                print('\r\nERROR Invalid parameters\r\n')
                return response, status.HTTP_400_BAD_REQUEST
        elif data['mode'] == 2: # CLOCK
            if data['mark'] is None or data['space'] is None or data['count'] is None:
                response = json.dumps({'status': 'NG', 'message': 'Invalid parameters: mark, space, count should be present'})
                print('\r\nERROR Invalid parameters\r\n')
                return response, status.HTTP_400_BAD_REQUEST
            if data['mark'] == 0 or data['space'] == 0 or data['count'] == 0:
                response = json.dumps({'status': 'NG', 'message': 'Invalid parameters: mark, space, count should be > 0 when mode is 2'})
                print('\r\nERROR Invalid parameters\r\n')
                return response, status.HTTP_400_BAD_REQUEST
    #print(data['direction'])
    #print(data['mode'])
    #print(data['alert'])
    #print(data['alertperiod'])
    #print(data['polarity'])
    #print(data['width'])
    #print(data['mark'])
    #print(data['space'])


    # get notifications and remove from list
    notification = data['notification']
    data.pop('notification')
    #print(data)
    #print(notification)

    #print(api)
    #print(data)
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username

    # note: python dict maintains insertion order so number will always be the last key
    data['number'] = number
    print('set_gpio_prop {} devicename={}'.format(data['username'], data['devicename']))

    response, status_return = process_request(api, data)
    if status_return != 200:
        return response, status_return

    source = "gpio{}".format(number)
    g_database_client.update_device_notification(username, devicename, source, notification)

    # update device configuration database for device bootup
    #print("data={}".format(data))
    data.pop('number')
    item = g_database_client.update_device_peripheral_configuration(username, devicename, "gpio", int(number), None, None, None, data)

    return response



#
# GET GPIO VOLTAGE
#
# - Request:
#   GET /devices/device/<devicename>/gpio/voltage
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': { 'voltage': int } }
#   { 'status': 'NG', 'message': string }
#   voltage is an index of the value in the list of voltages
#     ["3.3 V", "5 V"]
#
# GET ADC VOLTAGE
#
# - Request:
#   GET /devices/device/<devicename>/adc/voltage
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': { 'voltage': int } }
#   { 'status': 'NG', 'message': string }
#   voltage is an index of the value in the list of voltages
#     ["-5/+5V Range", "-10/+10V Range", "0/10V Range"]
#
@app.route('/devices/device/<devicename>/<xxx>/voltage', methods=['GET'])
def get_xxx_voltage(devicename, xxx):
    api = 'get_{}_voltage'.format(xxx)

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
    if data['username'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_{}_voltage {} devicename={}'.format(xxx, data['username'], data['devicename']))

    return process_request(api, data)

#
# SET GPIO VOLTAGE
#
# - Request:
#   POST /devices/device/<devicename>/gpio/voltage
#   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
#   data: { 'voltage': int }
#   voltage is an index of the value in the list of voltages
#     ["3.3 V", "5 V"]
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
# SET ADC VOLTAGE
#
# - Request:
#   POST /devices/device/<devicename>/adc/voltage
#   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
#   data: { 'voltage': int }
#   voltage is an index of the value in the list of voltages
#     ["-5/+5V Range", "-10/+10V Range", "0/10V Range"]
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/<xxx>/voltage', methods=['POST'])
def set_xxx_voltage(devicename, xxx):
    api = 'set_{}_voltage'.format(xxx)

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get parameter inputs
    data = flask.request.get_json()

    # check parameter input
    if data['voltage'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST
    if data['voltage'] > 2:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    data['username'] = g_database_client.get_username_from_token(data['token'])
    if data['username'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('set_{}_voltage {} devicename={}'.format(xxx, data['username'], data['devicename']))

    return process_request(api, data)


#
# ENABLE/DISABLE GPIO
#
# - Request:
#   POST /devices/device/DEVICENAME/gpio/NUMBER/enable
#   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
#   data: { 'enable': int }
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/gpio/<number>/enable', methods=['POST'])
def enable_gpio(devicename, number):
    api = 'enable_gpio'

    # check number parameter
    number = int(number)
    if number > 4 or number < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get parameter inputs
    data = flask.request.get_json()

    # check parameter input
    if data['enable'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username

    # note: python dict maintains insertion order so number will always be the last key
    data['number'] = number
    print('enable_gpio {} devicename={} number={}'.format(username, devicename, number))

    return process_request(api, data)


#
# GET I2CS
#
# - Request:
#   GET /devices/device/<devicename>/i2cs
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 
#     'value': { 
#       'i2cs': [
#         {'enabled': int}, 
#         {'enabled': int}, 
#         {'enabled': int}, 
#         {'enabled': int}, 
#       ]
#     }
#   }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/i2cs', methods=['GET'])
def get_i2cs(devicename):
    api = 'get_i2cs'

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    data = {}
    data['token'] = token
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username
    print('get_i2cs {} devicename={}'.format(data['username'], data['devicename']))

    return process_request(api, data)


########################################################################################################
#
# GET ALL I2C DEVICES
#
# - Request:
#   GET /devices/device/DEVICENAME/i2c/sensors
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string}, ...] }
#   { 'status': 'NG', 'message': string }
#
#
# GET ALL ADC DEVICES
# GET ALL 1WIRE DEVICES
# GET ALL TPROBE DEVICES
#
# - Request:
#   GET /devices/device/DEVICENAME/adc/sensors
#   GET /devices/device/DEVICENAME/1wire/sensors
#   GET /devices/device/DEVICENAME/tprobe/sensors
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'manufacturer': string, 'model': string, 'timestamp': string}, ...] }
#   { 'status': 'NG', 'message': string }
#
########################################################################################################
@app.route('/devices/device/<devicename>/<xxx>/sensors', methods=['GET'])
def get_all_xxx_sensors(devicename, xxx):

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get All {} Sensors: Invalid authorization header\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get All {} Sensors: Token expired\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_all_i2c_sensors {} devicename={}'.format(username, devicename))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get All {} Sensors: Empty parameter found\r\n'.format(xxx))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get All {} Sensors: Token expired [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get All {} Sensors: Token is invalid [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED

    sensors = g_database_client.get_all_sensors(username, devicename, xxx)


    msg = {'status': 'OK', 'message': 'All Sensors queried successfully.', 'sensors': sensors}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\nGet All {} Sensors successful: {}\r\n{} sensors\r\n'.format(xxx, username, len(sensors)))
    return response


########################################################################################################
#
# GET ALL I2C INPUT/OUTPUT DEVICES
#
# - Request:
#   GET /devices/device/DEVICENAME/i2c/sensors/DEVICETYPE
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string}, ...] }
#   { 'status': 'NG', 'message': string }
#
########################################################################################################
@app.route('/devices/device/<devicename>/i2c/sensors/<devicetype>', methods=['GET'])
def get_all_i2c_type_sensors(devicename, devicetype):

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get All {} Sensors: Invalid authorization header\r\n'.format("i2c"))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get All {} Sensors: Token expired\r\n'.format("i2c"))
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_all_i2c_sensors {} devicename={}'.format(username, devicename))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get All {} Sensors: Empty parameter found\r\n'.format("i2c"))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get All {} Sensors: Token expired [{}]\r\n'.format("i2c", username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get All {} Sensors: Token is invalid [{}]\r\n'.format("i2c", username))
        return response, status.HTTP_401_UNAUTHORIZED

    sensors = g_database_client.get_all_type_sensors(username, devicename, "i2c", devicetype)


    msg = {'status': 'OK', 'message': 'All Sensors queried successfully.', 'sensors': sensors}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\nGet All {} Sensors successful: {}\r\n{} sensors\r\n'.format("i2c", username, len(sensors)))
    return response


########################################################################################################
#
# GET PERIPHERAL SENSOR READINGS
#
# - Request:
#   GET /devices/device/DEVICENAME/sensors/readings
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string, 'readings': {'value': int, 'lowest': int, 'highest': int}, 'enabled': int}, ...] }
#   { 'status': 'NG', 'message': string }
#
#
# DELETE PERIPHERAL SENSOR READINGS
#
# - Request:
#   DELETE /devices/device/DEVICENAME/sensors/readings
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
########################################################################################################
@app.route('/devices/device/<devicename>/sensors/readings', methods=['GET', 'DELETE'])
def get_all_device_sensors_enabled_input_readings(devicename):

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get All Device Sensors: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get All Device Sensors: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    #print('get_all_device_sensors_enabled_input {} devicename={}'.format(username, devicename))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get All Device Sensors: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get All Device Sensors: Token expired [{} {}] DATETIME {}\r\n'.format(username, devicename, datetime.datetime.now()))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get All Device Sensors: Token is invalid [{} {}]\r\n'.format(username, devicename))
        return response, status.HTTP_401_UNAUTHORIZED


    if flask.request.method == 'GET':
        # query device
        api = "get_devs"
        data = {}
        data['token'] = token
        data['devicename'] = devicename
        data['username'] = username
        response, status_return = process_request(api, data)
        if status_return == 200:
            # query database
            sensors = g_database_client.get_all_device_sensors_input(username, devicename)

            # map queried result with database result
            #print("from device")
            response = json.loads(response)
            #print(response["value"])

            for sensor in sensors:
                #print(sensor)
                found = False
                peripheral = "{}{}".format(sensor['source'], sensor['number'])

                if sensor["source"] == "i2c":
                    if response["value"].get(peripheral):
                        for item in response["value"][peripheral]:
                            # match found for database result and actual device result
                            # set database record to configured and actual device item["enabled"]
                            if sensor["address"] == item["address"]:
                                g_database_client.set_enable_configure_sensor(username, devicename, sensor['source'], sensor['number'], sensor['sensorname'], item["enabled"], 1)
                                found = True
                                break
                else:
                    if response["value"].get(peripheral):
                        for item in response["value"][peripheral]:
                            if item["class"] == get_i2c_device_class(sensor["class"]):
                                g_database_client.set_enable_configure_sensor(username, devicename, sensor['source'], sensor['number'], sensor['sensorname'], item["enabled"], 1)
                                found = True
                                break

                # no match found
                # set database record to unconfigured and disabled
                if found == False:
                    g_database_client.set_enable_configure_sensor(username, devicename, sensor['source'], sensor['number'], sensor['sensorname'], 0, 0)
            #print()
        else:
            # cannot communicate with device so set database record to unconfigured and disabled
            g_database_client.disable_unconfigure_sensors(username, devicename)

        # query database
        sensors = g_database_client.get_all_device_sensors_enabled_input(username, devicename)
        for sensor in sensors:
            address = None
            if sensor.get("address"):
                address = sensor["address"]
            source = "{}{}".format(sensor["source"], sensor["number"])
            sensor_reading = g_database_client.get_sensor_reading(username, devicename, source, address)
            if sensor_reading is not None:
                sensor['readings'] = sensor_reading

    elif flask.request.method == 'DELETE':
        sensors = g_database_client.get_all_device_sensors_input(username, devicename)
        for sensor in sensors:
            address = None
            if sensor.get("address"):
                address = sensor["address"]
            source = "{}{}".format(sensor["source"], sensor["number"])
            g_database_client.delete_sensor_reading(username, devicename, source, address)


    msg = {'status': 'OK', 'message': 'Get All Device Sensors queried successfully.', 'sensors': sensors}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    #print('\r\nGet All Device Sensors successful: {} {} {} sensors\r\n'.format(username, devicename, len(sensors)))
    return response


########################################################################################################
#
# GET PERIPHERAL SENSOR READINGS DATASET
#
# - Request:
#   GET /devices/device/DEVICENAME/sensors/readings/dataset
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string, 'readings': [{'timestamp': float, 'value': float, 'subclass': {'value': float}}], 'enabled': int}, ...] }
#   { 'status': 'NG', 'message': string }
#
########################################################################################################
@app.route('/devices/device/<devicename>/sensors/readings/dataset', methods=['GET'])
def get_all_device_sensors_enabled_input_readings_dataset(devicename):

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get All Device Sensors Dataset: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get All Device Sensors Dataset: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    #print('get_all_device_sensors_enabled_input {} devicename={}'.format(username, devicename))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get All Device Sensors Dataset: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get All Device Sensors Dataset: Token expired [{} {}] DATETIME {}\r\n'.format(username, devicename, datetime.datetime.now()))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get All Device Sensors Dataset: Token is invalid [{} {}]\r\n'.format(username, devicename))
        return response, status.HTTP_401_UNAUTHORIZED


    if flask.request.method == 'GET':
        # query device
        api = "get_devs"
        data = {}
        data['token'] = token
        data['devicename'] = devicename
        data['username'] = username
        response, status_return = process_request(api, data)
        if status_return == 200:
            # query database
            sensors = g_database_client.get_all_device_sensors_input(username, devicename)

            # map queried result with database result
            #print("from device")
            response = json.loads(response)
            #print(response["value"])

            for sensor in sensors:
                #print(sensor)
                found = False
                peripheral = "{}{}".format(sensor['source'], sensor['number'])

                if sensor["source"] == "i2c":
                    if response["value"].get(peripheral):
                        for item in response["value"][peripheral]:
                            # match found for database result and actual device result
                            # set database record to configured and actual device item["enabled"]
                            if sensor["address"] == item["address"]:
                                g_database_client.set_enable_configure_sensor(username, devicename, sensor['source'], sensor['number'], sensor['sensorname'], item["enabled"], 1)
                                found = True
                                break
                else:
                    if response["value"].get(peripheral):
                        for item in response["value"][peripheral]:
                            if item["class"] == get_i2c_device_class(sensor["class"]):
                                g_database_client.set_enable_configure_sensor(username, devicename, sensor['source'], sensor['number'], sensor['sensorname'], item["enabled"], 1)
                                found = True
                                break

                # no match found
                # set database record to unconfigured and disabled
                if found == False:
                    g_database_client.set_enable_configure_sensor(username, devicename, sensor['source'], sensor['number'], sensor['sensorname'], 0, 0)
            #print()
        else:
            # cannot communicate with device so set database record to unconfigured and disabled
            g_database_client.disable_unconfigure_sensors(username, devicename)

        # query database
        sensors = g_database_client.get_all_device_sensors_enabled_input(username, devicename)
        for sensor in sensors:
            address = None
            if sensor.get("address"):
                address = sensor["address"]
            source = "{}{}".format(sensor["source"], sensor["number"])
            sensor_reading = g_database_client.get_sensor_reading_dataset(username, devicename, source, address)
            if sensor_reading is not None:
                sensor['readings'] = sensor_reading


    msg = {'status': 'OK', 'message': 'Get All Device Sensors Dataset queried successfully.', 'sensors': sensors}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    #print('\r\nGet All Device Sensors Dataset successful: {} {} {} sensors\r\n'.format(username, devicename, len(sensors)))
    return response


########################################################################################################
#
# DELETE PERIPHERAL SENSOR PROPERTIES
#
# - Request:
#   DELETE /devices/device/DEVICENAME/sensors/properties
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
########################################################################################################
@app.route('/devices/device/<devicename>/sensors/properties', methods=['DELETE'])
def delete_all_device_sensors_properties(devicename):

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Delete All Device Sensors Properties: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Delete All Device Sensors Properties: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('delete_all_device_sensors_properties {} devicename={}'.format(username, devicename))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Delete All Device Sensors Properties: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Delete All Device Sensors Properties: Token expired [{} {}]\r\n'.format(username, devicename))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Delete All Device Sensors Properties: Token is invalid [{} {}]\r\n'.format(username, devicename))
        return response, status.HTTP_401_UNAUTHORIZED

    g_database_client.delete_all_device_peripheral_configuration(username, devicename)

    msg = {'status': 'OK', 'message': 'Delete All Device Sensors Properties deleted successfully.',}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\nDelete All Device Sensors Properties successful: {} {}\r\n'.format(username, devicename))
    return response



########################################################################################################
#
# GET I2C DEVICES
#
# - Request:
#   GET /devices/device/DEVICENAME/i2c/NUMBER/sensors
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string, 'enabled': int}, ...] }
#   { 'status': 'NG', 'message': string }
#
#
# GET ADC DEVICES
# GET 1WIRE DEVICES
# GET TPROBE DEVICES
#
# - Request:
#   GET /devices/device/DEVICENAME/adc/NUMBER/sensors
#   GET /devices/device/DEVICENAME/1wire/NUMBER/sensors
#   GET /devices/device/DEVICENAME/tprobe/NUMBER/sensors
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'manufacturer': string, 'model': string, 'timestamp': string, 'enabled': int}, ...] }
#   { 'status': 'NG', 'message': string }
#
########################################################################################################
@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors', methods=['GET'])
def get_xxx_sensors(devicename, xxx, number):

    # check number parameter
    if int(number) > 4 or int(number) < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get {} Sensors: Invalid authorization header\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensors: Token expired\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_{}_sensors {} devicename={} number={}'.format(xxx, username, devicename, number))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get {} Sensors: Empty parameter found\r\n'.format(xxx))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensors: Token expired [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get {} Sensors: Token is invalid [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED

    # query peripheral sensors
    sensors = g_database_client.get_sensors(username, devicename, xxx, number)

    # query device
    api = "get_{}_devs".format(xxx)
    data = {}
    data['token'] = token
    data['devicename'] = devicename
    data['username'] = username
    data["number"] = int(number)
    response, status_return = process_request(api, data)
    if status_return == 200:
        # map queried result with database result
        #print("from device")
        response = json.loads(response)
        #print(response["value"])
        if xxx == "i2c":
            # if I2C
            #print("I2C")
            for sensor in sensors:
                found = False
                for item in response["value"]:
                    # match found for database result and actual device result
                    # set database record to configured and actual device item["enabled"]
                    if sensor["address"] == item["address"]:
                        # device is configured
                        g_database_client.set_enable_configure_sensor(username, devicename, sensor['source'], sensor['number'], sensor['sensorname'], item["enabled"], 1)
                        sensor["enabled"] = item["enabled"]
                        sensor["configured"] = 1
                        found = True
                        break
                # no match found
                # set database record to unconfigured and disabled
                if found == False:
                    g_database_client.set_enable_configure_sensor(username, devicename, sensor['source'], sensor['number'], sensor['sensorname'], 0, 0)
                    sensor["enabled"] = 0
                    sensor["configured"] = 0
        else:
            # if ADC/1WIRE/TPROBE
            #print("ADC/1WIRE/TPROBE")
            for sensor in sensors:
                found = False
                # check if this is the active sensor
                # if not the active sensor, then set database record to unconfigured and disabled
                #print(sensor)
#                if sensor['configured']:
                for item in response["value"]:
                    if item["class"] == get_i2c_device_class(sensor["class"]):
                        g_database_client.set_enable_configure_sensor(username, devicename, sensor['source'], sensor['number'], sensor['sensorname'], item["enabled"], 1)
                        sensor["enabled"] = item["enabled"]
                        sensor["configured"] = 1
                        found = True
                        break
                if found == False:
                    # set database record to unconfigured and disabled
                    g_database_client.set_enable_configure_sensor(username, devicename, sensor['source'], sensor['number'], sensor['sensorname'], 0, 0)
                    sensor["enabled"] = 0
                    sensor["configured"] = 0
#                else:
#                    # set database record to unconfigured and disabled
#                    g_database_client.set_enable_configure_sensor(username, devicename, sensor['source'], sensor['number'], sensor['sensorname'], 0, 0)
#                    sensor["enabled"] = 0
#                    sensor["configured"] = 0
        #print()
    else:
        # cannot communicate with device so set database record to unconfigured and disabled
        g_database_client.disable_unconfigure_sensors(username, devicename)
        for sensor in sensors:
            sensor["enabled"] = 0
            sensor["configured"] = 0

    # get sensor readings for enabled input devices
    for sensor in sensors:
        if sensor['type'] == 'input' and sensor['enabled']:
            address = None
            if sensor.get("address"):
                address = sensor["address"]
            source = "{}{}".format(xxx, number)
            sensor_reading = g_database_client.get_sensor_reading(username, devicename, source, address)
            if sensor_reading is not None:
                sensor['readings'] = sensor_reading

    msg = {'status': 'OK', 'message': 'Sensors queried successfully.', 'sensors': sensors}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\nGet {} Sensors successful: {}\r\n{} sensors\r\n'.format(xxx, username, len(sensors)))
    return response


#
# when deleting a sensor,
# make sure the sensor configurations, sensor readings and sensor registration are also deleted
#
def delete_sensor(username, devicename, xxx, number, sensorname, sensor):

    print("\r\ndelete_sensor {}".format(sensorname))
    address = None
    if sensor.get("address"):
        address = sensor["address"]

    print("")

    # delete sensor notifications
    print("Deleting sensor notifications...")
    source = "{}{}{}".format(xxx, number, sensorname)
    notification = g_database_client.get_device_notification(username, devicename, source)
    print(notification)
    g_database_client.delete_device_notification_sensor(username, devicename, source)
    notification = g_database_client.get_device_notification(username, devicename, source)
    print(notification)
    print("")

    # delete sensor configurations
    print("Deleting sensor configurations...")
    config = g_database_client.get_device_peripheral_configuration(username, devicename, xxx, int(number), address)
    print(config)
    g_database_client.delete_device_peripheral_configuration(username, devicename, xxx, int(number), address)
    config = g_database_client.get_device_peripheral_configuration(username, devicename, xxx, int(number), address)
    print(config)
    print("")

    # delete sensor readings
    print("Deleting sensor readings...")
    source = "{}{}".format(xxx, number)
    readings = g_database_client.get_sensor_reading(username, devicename, source, address)
    print(readings)
    readings_dataset = g_database_client.get_sensor_reading_dataset(username, devicename, source, address)
    print(readings_dataset)
    g_database_client.delete_sensor_reading(username, devicename, source, address)
    readings = g_database_client.get_sensor_reading(username, devicename, source, address)
    print(readings)
    readings_dataset = g_database_client.get_sensor_reading_dataset(username, devicename, source, address)
    print(readings_dataset)
    print("")

    # delete sensor from database
    print("Deleting sensor registration...")
    g_database_client.delete_sensor(username, devicename, xxx, number, sensorname)
    result = g_database_client.get_sensor(username, devicename, xxx, number, sensorname)
    print(result)
    print("")


########################################################################################################
#
# ADD I2C DEVICE
#
# - Request:
#   POST /devices/device/<devicename>/i2c/NUMBER/sensors/sensor/<sensorname>
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: {'address': int, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'attributes': []}
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
# ADD ADC DEVICE
# ADD 1WIRE DEVICE
# ADD TPROBE DEVICE
#
# - Request:
#   POST /devices/device/<devicename>/adc/NUMBER/sensors/sensor/<sensorname>
#   POST /devices/device/<devicename>/1wire/NUMBER/sensors/sensor/<sensorname>
#   POST /devices/device/<devicename>/tprobe/NUMBER/sensors/sensor/<sensorname>
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: {'manufacturer': string, 'model': string, 'class': string, 'type': string, 'attributes': []}
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
#
# DELETE I2C DEVICE
#
# - Request:
#   DELETE /devices/device/<devicename>/i2c/NUMBER/sensors/sensor/<sensorname>
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
# DELETE ADC DEVICE
# DELETE 1WIRE DEVICE
# DELETE TPROBE DEVICE
#
# - Request:
#   DELETE /devices/device/<devicename>/adc/NUMBER/sensors/sensor/<sensorname>
#   DELETE /devices/device/<devicename>/1wire/NUMBER/sensors/sensor/<sensorname>
#   DELETE /devices/device/<devicename>/tprobe/NUMBER/sensors/sensor/<sensorname>
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>', methods=['POST', 'DELETE'])
def register_xxx_sensor(devicename, xxx, number, sensorname):

    # check number parameter
    if int(number) > 4 or int(number) < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Add/Delete {} Sensor: Invalid authorization header\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Add/Delete {} Sensor: Token expired\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    print('register_{}_sensor {} devicename={} number={} sensorname={}'.format(xxx, username, devicename, number, sensorname))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(devicename) == 0 or len(sensorname) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Add/Delete {} Sensor: Empty parameter found\r\n'.format(xxx))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Add/Delete {} Sensor: Token expired [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Add/Delete {} Sensor: Token is invalid [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED

    if flask.request.method == 'POST':
        # get parameters
        data = flask.request.get_json()
        #print(data)
        if xxx == 'i2c':
            if data['address'] is None:
                response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
                print('\r\nERROR Add {} Sensor: Parameters not included [{},{}]\r\n'.format(xxx, username, devicename))
                return response, status.HTTP_400_BAD_REQUEST
            data["address"] = int(data["address"])
            if data["address"] == 0:
                response = json.dumps({'status': 'NG', 'message': 'Invalid address'})
                print('\r\nERROR Add {} Sensor: Invalid address [{},{}]\r\n'.format(xxx, username, devicename))
                return response, status.HTTP_400_BAD_REQUEST
            # check if sensor address is registered
            # address should be unique within a slot
            if g_database_client.get_sensor_by_address(username, devicename, xxx, number, data["address"]):
                response = json.dumps({'status': 'NG', 'message': 'Sensor address is already taken'})
                print('\r\nERROR Add {} Sensor: Sensor address is already taken [{},{},{}]\r\n'.format(xxx, username, devicename, data["address"]))
                return response, status.HTTP_409_CONFLICT

        if data["manufacturer"] is None or data["model"] is None or data["class"] is None or data["type"] is None or data["units"] is None or data["formats"] is None or data["attributes"] is None:
            response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
            print('\r\nERROR Add {} Sensor: Parameters not included [{},{}]\r\n'.format(xxx, username, devicename))
            return response, status.HTTP_400_BAD_REQUEST
        #print(data["manufacturer"])
        #print(data["model"])

        # check if sensor is registered
        # name should be unique all throughout the slots
        if g_database_client.check_sensor(username, devicename, sensorname):
            response = json.dumps({'status': 'NG', 'message': 'Sensor name is already taken'})
            print('\r\nERROR Add {} Sensor: Sensor name is already taken [{},{},{}]\r\n'.format(xxx, username, devicename, sensorname))
            return response, status.HTTP_409_CONFLICT

        # can only register 1 device for adc/1wire/tprobe
        if xxx != 'i2c':
            if g_database_client.get_sensors_count(username, devicename, xxx, number) > 0:
                response = json.dumps({'status': 'NG', 'message': 'Cannot add more than 1 sensor for {}'.format(xxx)})
                print('\r\nERROR Add {} Sensor: Cannot add more than 1 sensor [{},{},{}]\r\n'.format(xxx, username, devicename, sensorname))
                return response, status.HTTP_400_BAD_REQUEST

        # add sensor to database
        result = g_database_client.add_sensor(username, devicename, xxx, number, sensorname, data)
        #print(result)
        if not result:
            response = json.dumps({'status': 'NG', 'message': 'Sensor could not be registered'})
            print('\r\nERROR Add {} Sensor: Sensor could not be registered [{},{}]\r\n'.format(xxx, username, devicename))
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR

        msg = {'status': 'OK', 'message': 'Sensor registered successfully.'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\n{} Sensor registered successful: {}\r\n{}\r\n'.format(xxx, username, response))
        return response

    elif flask.request.method == 'DELETE':

        # check if sensor is registered
        sensor = g_database_client.get_sensor(username, devicename, xxx, number, sensorname)
        if not sensor:
            response = json.dumps({'status': 'NG', 'message': 'Sensor is not registered'})
            print('\r\nERROR Delete {} Sensor: Sensor is not registered [{},{}]\r\n'.format(xxx, username, devicename))
            return response, status.HTTP_404_NOT_FOUND

        # delete necessary sensor-related database information
        delete_sensor(username, devicename, xxx, number, sensorname, sensor)

        msg = {'status': 'OK', 'message': 'Sensor unregistered successfully.'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\n{} Sensor unregistered successful: {}\r\n{}\r\n'.format(xxx, username, response))
        return response


########################################################################################################
#
# GET I2C DEVICE
#
# - Request:
#   GET /devices/device/<devicename>/i2c/NUMBER/sensors/sensor/<sensorname>
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'sensor': {'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string}}
#   {'status': 'NG', 'message': string}
#
# GET ADC DEVICE
# GET 1WIRE DEVICE
# GET TPROBE DEVICE
#
# - Request:
#   GET /devices/device/<devicename>/adc/NUMBER/sensors/sensor/<sensorname>
#   GET /devices/device/<devicename>/1wire/NUMBER/sensors/sensor/<sensorname>
#   GET /devices/device/<devicename>/tprobe/NUMBER/sensors/sensor/<sensorname>
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'sensor': {'sensorname': string, 'manufacturer': string, 'model': string, 'timestamp': string}}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>', methods=['GET'])
def get_xxx_sensor(devicename, xxx, number, sensorname):

    # check number parameter
    if int(number) > 4 or int(number) < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get {} Sensor: Invalid authorization header\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensor: Token expired\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_{}_sensor {} devicename={} number={} sensorname={}'.format(xxx, username, devicename, number, sensorname))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(devicename) == 0 or len(sensorname) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get {} Sensor: Empty parameter found\r\n'.format(xxx))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensor: Token expired [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get {} Sensor: Token is invalid [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED

    # check if sensor is registered
    sensor = g_database_client.get_sensor(username, devicename, xxx, number, sensorname)
    if not sensor:
        response = json.dumps({'status': 'NG', 'message': 'Sensor is not registered'})
        print('\r\nERROR Get {} Sensor: Sensor is not registered [{},{}]\r\n'.format(xxx, username, devicename))
        return response, status.HTTP_404_NOT_FOUND


    msg = {'status': 'OK', 'message': 'Sensor queried successfully.', 'sensor': sensor}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\n{} Sensor queried successful: {}\r\n{}\r\n'.format(xxx, username, response))
    return response


########################################################################################################
#
# GET I2C DEVICE READINGS (per sensor)
#
# - Request:
#   GET /devices/device/<devicename>/i2c/NUMBER/sensors/sensor/<sensorname>/readings
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'sensor_readings': {'value': int, 'lowest': int, 'highest': int} }
#   {'status': 'NG', 'message': string }
#
# GET ADC DEVICE READINGS (per sensor)
# GET 1WIRE DEVICE READINGS (per sensor)
# GET TPROBE DEVICE READINGS (per sensor)
#
# - Request:
#   GET /devices/device/<devicename>/adc/NUMBER/sensors/sensor/<sensorname>/readings
#   GET /devices/device/<devicename>/1wire/NUMBER/sensors/sensor/<sensorname>/readings
#   GET /devices/device/<devicename>/tprobe/NUMBER/sensors/sensor/<sensorname>/readings
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'sensor_readings': {'value': int, 'lowest': int, 'highest': int} }
#   {'status': 'NG', 'message': string }
#
#
# DELETE I2C DEVICE READINGS (per sensor)
#
# - Request:
#   DELETE /devices/device/<devicename>/i2c/NUMBER/sensors/sensor/<sensorname>/readings
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string }
#   {'status': 'NG', 'message': string }
#
# DELETE ADC DEVICE READINGS (per sensor)
# DELETE 1WIRE DEVICE READINGS (per sensor)
# DELETE TPROBE DEVICE READINGS (per sensor)
#
# - Request:
#   DELETE /devices/device/<devicename>/adc/NUMBER/sensors/sensor/<sensorname>/readings
#   DELETE /devices/device/<devicename>/1wire/NUMBER/sensors/sensor/<sensorname>/readings
#   DELETE /devices/device/<devicename>/tprobe/NUMBER/sensors/sensor/<sensorname>/readings
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string }
#   {'status': 'NG', 'message': string }
#
########################################################################################################
@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>/readings', methods=['GET', 'DELETE'])
def get_xxx_sensor_readings(devicename, xxx, number, sensorname):

    # check number parameter
    if int(number) > 4 or int(number) < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get {} Sensor: Invalid authorization header\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensor: Token expired\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_{}_sensor_readings {} devicename={} number={} sensorname={}'.format(xxx, username, devicename, number, sensorname))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(devicename) == 0 or len(sensorname) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get {} Sensor: Empty parameter found\r\n'.format(xxx))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensor: Token expired [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get {} Sensor: Token is invalid [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED

    # check if sensor is registered
    sensor = g_database_client.get_sensor(username, devicename, xxx, number, sensorname)
    if not sensor:
        response = json.dumps({'status': 'NG', 'message': 'Sensor is not registered'})
        print('\r\nERROR Get {} Sensor: Sensor is not registered [{},{}]\r\n'.format(xxx, username, devicename))
        return response, status.HTTP_404_NOT_FOUND

    # check if sensor type is valid
    if sensor["type"] != "input":
        response = json.dumps({'status': 'NG', 'message': 'Sensor type is invalid'})
        print('\r\nERROR Get {} Sensor: Sensor type is invalid [{},{}]\r\n'.format(xxx, username, devicename))
        return response, status.HTTP_404_NOT_FOUND

    address = None
    if sensor.get("address"):
        address = sensor["address"]
    source = "{}{}".format(xxx, number)
    if flask.request.method == 'GET':
        # get sensor reading
        sensor_readings = g_database_client.get_sensor_reading(username, devicename, source, address)
        if not sensor_readings:
            # no readings yet
            sensor_readings = {}
            sensor_readings["value"] = "0"
            sensor_readings["lowest"] = "0"
            sensor_readings["highest"] = "0"

        msg = {'status': 'OK', 'message': 'Sensor reading queried successfully.', 'sensor_readings': sensor_readings}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nSensor reading queried successful: {}\r\n{}\r\n'.format(username, response))
        return response

    elif flask.request.method == 'DELETE':
        # delete sensor reading
        g_database_client.delete_sensor_reading(username, devicename, source, address)

        msg = {'status': 'OK', 'message': 'Sensor reading deleted successfully.'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nSensor reading deleted successful: {}\r\n{}\r\n'.format(username, response))
        return response


########################################################################################################
#
# GET I2C DEVICES READINGS (per peripheral slot)
#
# - Request:
#   GET /devices/device/<devicename>/i2c/NUMBER/sensors/readings
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'sensor_readings': {'value': int, 'lowest': int, 'highest': int} }
#   {'status': 'NG', 'message': string }
#
# GET ADC DEVICES READINGS (per peripheral slot)
# GET 1WIRE DEVICES READINGS (per peripheral slot)
# GET TPROBE DEVICES READINGS (per peripheral slot)
#
# - Request:
#   GET /devices/device/<devicename>/adc/NUMBER/sensors/readings
#   GET /devices/device/<devicename>/1wire/NUMBER/sensors/readings
#   GET /devices/device/<devicename>/tprobe/NUMBER/sensors/readings
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'sensor_readings': {'value': int, 'lowest': int, 'highest': int} }
#   {'status': 'NG', 'message': string }
#
#
# DELETE I2C DEVICES READINGS (per peripheral slot)
#
# - Request:
#   DELETE /devices/device/<devicename>/i2c/NUMBER/sensors/readings
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string }
#   {'status': 'NG', 'message': string }
#
# DELETE ADC DEVICES READINGS (per peripheral slot)
# DELETE 1WIRE DEVICES READINGS (per peripheral slot)
# DELETE TPROBE DEVICES READINGS (per peripheral slot)
#
# - Request:
#   DELETE /devices/device/<devicename>/adc/NUMBER/sensors/readings
#   DELETE /devices/device/<devicename>/1wire/NUMBER/sensors/readings
#   DELETE /devices/device/<devicename>/tprobe/NUMBER/sensors/readings
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string }
#   {'status': 'NG', 'message': string }
#
########################################################################################################
@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/readings', methods=['GET', 'DELETE'])
def get_xxx_sensors_readings(devicename, xxx, number):

    # check number parameter
    if int(number) > 4 or int(number) < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get {} Sensor: Invalid authorization header\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensor: Token expired\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_{}_sensor_readings {} devicename={} number={}'.format(xxx, username, devicename, number))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(devicename) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get {} Sensor: Empty parameter found\r\n'.format(xxx))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensor: Token expired [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get {} Sensor: Token is invalid [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED

    source = "{}{}".format(xxx, number)
    if flask.request.method == 'GET':
        if True:
            # get enabled input sensors
            sensors = g_database_client.get_sensors_enabled_input(username, devicename, xxx, number)

            # get sensor reading for each enabled input sensors
            for sensor in sensors:
                address = None
                if sensor.get("address"):
                    address = sensor["address"]
                sensor_reading = g_database_client.get_sensor_reading(username, devicename, source, address)
                sensor['readings'] = sensor_reading

            msg = {'status': 'OK', 'message': 'Sensors readings queried successfully.', 'sensor_readings': sensors}
            if new_token:
                msg['new_token'] = new_token
            response = json.dumps(msg)
            print('\r\nSensors readings queried successful: {}\r\n{}\r\n'.format(username, response))
            return response
        else:
            # get sensors readings
            sensor_readings = g_database_client.get_sensors_readings(username, devicename, source)

            msg = {'status': 'OK', 'message': 'Sensors readings queried successfully.', 'sensor_readings': sensor_readings}
            if new_token:
                msg['new_token'] = new_token
            response = json.dumps(msg)
            print('\r\nSensors readings queried successful: {}\r\n{}\r\n'.format(username, response))
            return response

    elif flask.request.method == 'DELETE':
        # delete sensors readings
        g_database_client.delete_sensors_readings(username, devicename, source)

        msg = {'status': 'OK', 'message': 'Sensors readings deleted successfully.'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nSensors readings deleted successful: {}\r\n{}\r\n'.format(username, response))
        return response


########################################################################################################
#
# GET I2C DEVICES READINGS DATASET (per peripheral slot)
#
# - Request:
#   GET /devices/device/<devicename>/i2c/NUMBER/sensors/sensor/SENSORNAME/readings/dataset
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'sensor_readings': [{'timestamp': int, 'value': int}] }
#   {'status': 'NG', 'message': string }
#
# GET ADC DEVICES READINGS DATASET (per peripheral slot)
# GET 1WIRE DEVICES READINGS DATASET (per peripheral slot)
# GET TPROBE DEVICES READINGS DATASET (per peripheral slot)
#
# - Request:
#   GET /devices/device/<devicename>/adc/NUMBER/sensors/sensor/SENSORNAME/readings/dataset
#   GET /devices/device/<devicename>/1wire/NUMBER/sensors/sensor/SENSORNAME/readings/dataset
#   GET /devices/device/<devicename>/tprobe/NUMBER/sensors/sensor/SENSORNAME/readings/dataset
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'sensor_readings': [{'timestamp': int, 'value': int}] }
#   {'status': 'NG', 'message': string }
#
########################################################################################################
@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>/readings/dataset', methods=['GET'])
def get_xxx_sensors_readings_dataset(devicename, xxx, number, sensorname):

    print('get_{}_sensor_readings_dataset'.format(xxx))

    # check number parameter
    if int(number) > 4 or int(number) < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get {} Sensor: Invalid authorization header\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensor: Token expired\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_{}_sensor_readings_dataset {} devicename={} number={}'.format(xxx, username, devicename, number))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(devicename) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get {} Sensor: Empty parameter found\r\n'.format(xxx))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensor: Token expired [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get {} Sensor: Token is invalid [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED


    # get sensor
    sensor = g_database_client.get_sensor(username, devicename, xxx, number, sensorname)

    source = "{}{}".format(xxx, number)
    address = None
    if sensor.get("address"):
        address = sensor["address"]
    sensor_reading = g_database_client.get_sensor_reading_dataset(username, devicename, source, address)
    sensor['readings'] = sensor_reading

    msg = {'status': 'OK', 'message': 'Sensors readings dataset queried successfully.', 'sensor_readings': sensor}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\nSensors readings dataset queried successful: {}\r\n{}\r\n'.format(username, response))
    return response


def get_i2c_device_class(classname):
    if classname == "speaker":
        return I2C_DEVICE_CLASS_SPEAKER
    elif classname == "display":
        return I2C_DEVICE_CLASS_DISPLAY
    elif classname == "light":
        return I2C_DEVICE_CLASS_LIGHT
    elif classname == "potentiometer":
        return I2C_DEVICE_CLASS_POTENTIOMETER
    elif classname == "temperature":
        return I2C_DEVICE_CLASS_TEMPERATURE
    elif classname == "humidity":
        return I2C_DEVICE_CLASS_HUMIDITY
    elif classname == "anemometer":
        return I2C_DEVICE_CLASS_ANEMOMETER
    elif classname == "battery":
        return I2C_DEVICE_CLASS_BATTERY
    elif classname == "fluid":
        return I2C_DEVICE_CLASS_FLUID
    return 0xFF


########################################################################################################
#
# SET I2C DEVICE PROPERTIES
#
# - Request:
#   POST /devices/device/<devicename>/i2c/number/sensors/sensor/<sensorname>/properties
#   headers: {'Authorization': 'Bearer ' + token.access}
#   data: adsasdasdasdasdasdasdasd
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
#
# SET ADC DEVICE PROPERTIES
# SET 1WIRE DEVICE PROPERTIES
# SET TPROBE DEVICE PROPERTIES
#
# - Request:
#   POST /devices/device/<devicename>/adc/number/sensors/sensor/<sensorname>/properties
#   POST /devices/device/<devicename>/1wire/number/sensors/sensor/<sensorname>/properties
#   POST /devices/device/<devicename>/tprobe/number/sensors/sensor/<sensorname>/properties
#   headers: {'Authorization': 'Bearer ' + token.access}
#   data: adsasdasdasdasdasdasdasd
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>/properties', methods=['POST'])
def set_xxx_dev_prop(devicename, xxx, number, sensorname):
    #print('set_{}_dev_prop'.format(xxx))

    # check number parameter
    if int(number) > 4 or int(number) < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Set {} Sensor: Invalid authorization header\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token} 
    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Set {} Sensor: Token expired\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    print('set_{}_dev_prop {} devicename={} number={} sensorname={}'.format(xxx, username, devicename, number, sensorname))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(devicename) == 0 or len(sensorname) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Set {} Sensor: Empty parameter found\r\n'.format(xxx))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Set {} Sensor: Token expired [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Set {} Sensor: Token is invalid [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = flask.request.get_json()
    if data is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if sensor is registered
    sensor = g_database_client.get_sensor(username, devicename, xxx, number, sensorname)
    if not sensor:
        response = json.dumps({'status': 'NG', 'message': 'Sensor is not registered'})
        print('\r\nERROR Get {} Sensor: Sensor is not registered [{},{}]\r\n'.format(xxx, username, devicename))
        return response, status.HTTP_404_NOT_FOUND

    api = 'set_{}_dev_prop'.format(xxx)
    #print('set_{}_dev_prop {}'.format(xxx, data))
    data['token'] = token
    data['devicename'] = devicename
    data['username'] = username
    if sensor.get('address'):
        data['address'] = sensor['address']
    data['class'] = int(get_i2c_device_class(sensor['class']))
    if sensor.get('subclass'):
        # handle subclasses
        data['subclass'] = int(get_i2c_device_class(sensor['subclass']))
    data['number'] = int(number)
    print('set_{}_dev_prop {} devicename={} number={}'.format(xxx, username, devicename, number))


    # no notification data
    if not data.get("notification"):
        #print("no notification data")

        response, status_return = process_request(api, data)
        if status_return != 200:
            # set enabled to FALSE and configured to FALSE
            g_database_client.set_enable_configure_sensor(username, devicename, xxx, number, sensorname, 0, 0)
            return response, status_return

        # if ADC/1WIRE/TPROBE, set all other ADC/1WIRE/TPROBE to unconfigured and disabled
        if xxx != "i2c":
            g_database_client.disable_unconfigure_sensors_source(username, devicename, xxx, number)
        # set to disabled and configured
        g_database_client.set_enable_configure_sensor(username, devicename, xxx, number, sensorname, 0, 1)

        # update device configuration database for device bootup
        #print("data={}".format(data))
        data.pop('number')
        if data.get('address'):
            data.pop('address')
        if data.get('class'):
            data.pop('class')
        if data.get('subclass'):
            data.pop('subclass')

        address = None
        if sensor.get('address'):
            address = sensor['address']
        classid = None
        if sensor.get('class'):
            classid = int(get_i2c_device_class(sensor['class']))
        subclassid = None
        if sensor.get('subclass'):
            subclassid = int(get_i2c_device_class(sensor['subclass']))
        item = g_database_client.update_device_peripheral_configuration(username, devicename, xxx, int(number), address, classid, subclassid, data)

        return response


    # has notification parameter (for class and subclass)
    notification = data['notification']
    data.pop('notification')
    # handle subclasses
    if data.get("subattributes"):
        subattributes_notification = data['subattributes']['notification']
        data['subattributes'].pop('notification')
    else:
        subattributes_notification = None

    # query device
    response, status_return = process_request(api, data)
    if status_return != 200:
        # set enabled to FALSE and configured to FALSE
        g_database_client.set_enable_configure_sensor(username, devicename, xxx, number, sensorname, 0, 0)
        return response, status_return

    # if ADC/1WIRE/TPROBE, set all other ADC/1WIRE/TPROBE to unconfigured and disabled
    if xxx != "i2c":
        g_database_client.disable_unconfigure_sensors_source(username, devicename, xxx, number)

    # set to disabled and configured
    g_database_client.set_enable_configure_sensor(username, devicename, xxx, number, sensorname, 0, 1)

    source = "{}{}{}".format(xxx, number, sensorname)
    #g_database_client.update_device_notification(username, devicename, source, notification)
    g_database_client.update_device_notification_with_notification_subclass(username, devicename, source, notification, subattributes_notification)

    # update device configuration database for device bootup
    #print("data={}".format(data))
    data.pop('number')
    if data.get('address'):
        data.pop('address')
    if data.get('class'):
        data.pop('class')
    if data.get('subclass'):
        data.pop('subclass')

    address = None
    if sensor.get('address'):
        address = sensor['address']
    classid = None
    if sensor.get('class'):
        classid = int(get_i2c_device_class(sensor['class']))
    subclassid = None
    if sensor.get('subclass'):
        subclassid = int(get_i2c_device_class(sensor['subclass']))
    item = g_database_client.update_device_peripheral_configuration(username, devicename, xxx, int(number), address, classid, subclassid, data)

    return response



########################################################################################################
#
# GET I2C DEVICE PROPERTIES
#
# - Request:
#   POST /devices/device/<devicename>/i2c/number/sensors/sensor/<sensorname>/properties
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'value': {}}
#   {'status': 'NG', 'message': string}
#
#
# GET ADC DEVICE PROPERTIES
# GET 1WIRE DEVICE PROPERTIES
# GET TPROBE DEVICE PROPERTIES
#
# - Request:
#   POST /devices/device/<devicename>/adc/number/sensors/sensor/<sensorname>/properties
#   POST /devices/device/<devicename>/1wire/number/sensors/sensor/<sensorname>/properties
#   POST /devices/device/<devicename>/tprobe/number/sensors/sensor/<sensorname>/properties
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'value': {}}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>/properties', methods=['GET'])
def get_xxx_dev_prop(devicename, xxx, number, sensorname):
    #print('get_{}_dev_prop'.format(xxx))

    # check number parameter
    if int(number) > 4 or int(number) < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get {} Sensor: Invalid authorization header\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token} 
    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensor: Token expired\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_{}_dev_prop {} devicename={} number={} sensorname={}'.format(xxx, username, devicename, number, sensorname))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(devicename) == 0 or len(sensorname) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get {} Sensor: Empty parameter found\r\n'.format(xxx))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensor: Token expired [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get {} Sensor: Token is invalid [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED

    # check if sensor is registered
    sensor = g_database_client.get_sensor(username, devicename, xxx, number, sensorname)
    if not sensor:
        response = json.dumps({'status': 'NG', 'message': 'Sensor is not registered'})
        print('\r\nERROR Get {} Sensor: Sensor is not registered [{},{}]\r\n'.format(xxx, username, devicename))
        return response, status.HTTP_404_NOT_FOUND

    api = 'get_{}_dev_prop'.format(xxx)
    data = {}
    data['token'] = token
    data['devicename'] = devicename
    data['username'] = username
    if sensor.get('address'):
        data['address'] = sensor['address']
    data['class'] = int(get_i2c_device_class(sensor['class']))
    data['number'] = int(number)
    print('get_{}_dev_prop {} devicename={} number={}'.format(xxx, username, devicename, number))

    # no notification object required
    if data["class"] < I2C_DEVICE_CLASS_POTENTIOMETER:
        return process_request(api, data)

    # has notification object required
    response, status_return = process_request(api, data)
    if status_return != 200:
        return response, status_return

    source = "{}{}{}".format(xxx, number, sensorname)
    #notification = g_database_client.get_device_notification(username, devicename, source)
    (notification, subattributes_notification) = g_database_client.get_device_notification_with_notification_subclass(username, devicename, source)
    if notification is not None:
        response = json.loads(response)
        if response.get('value'):
            response['value']['notification'] = notification
        else:
            response['value'] = {}
            response['value']['notification'] = notification
        response = json.dumps(response)
    else:
        response = json.loads(response)
        if response.get('value'):
            response['value']['notification'] = build_default_notifications(xxx, token)
        else:
            response['value'] = {}
            response['value']['notification'] = build_default_notifications(xxx, token)
        response = json.dumps(response)

    # handle subclasses
    if subattributes_notification is not None:
        response = json.loads(response)
        if response.get('value'):
            if response['value'].get('subattributes'):
                response['value']['subattributes']['notification'] = subattributes_notification
        else:
            response['value'] = {}
            response['value']['subattributes']['notification'] = subattributes_notification
        response = json.dumps(response)
    else:
        response = json.loads(response)
        if response.get('value'):
            if response['value'].get('subattributes'):
                response['value']['subattributes']['notification'] = build_default_notifications(xxx, token)
        else:
            response['value'] = {}
            response['value']['subattributes']['notification'] = build_default_notifications(xxx, token)
        response = json.dumps(response)

    return response


########################################################################################################
#
# ENABLE/DISABLE I2C DEVICE
#
# - Request:
#   POST /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/SENSORNAME/enable
#   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
#   data: { 'enable': int }
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
#
# ENABLE/DISABLE ADC DEVICE
# ENABLE/DISABLE 1WIRE DEVICE
# ENABLE/DISABLE TPROBE DEVICE
#
# - Request:
#   POST /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/SENSORNAME/enable
#   POST /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/SENSORNAME/enable
#   POST /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/SENSORNAME/enable
#   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
#   data: { 'enable': int }
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
########################################################################################################
@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>/enable', methods=['POST'])
def enable_xxx_dev(devicename, xxx, number, sensorname):
    api = 'enable_{}_dev'.format(xxx)

    # check number parameter
    if int(number) > 4 or int(number) < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = flask.request.get_json()

    # check parameter input
    if data['enable'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username

    # check if sensor is registered
    sensor = g_database_client.get_sensor(username, devicename, xxx, number, sensorname)
    if not sensor:
        response = json.dumps({'status': 'NG', 'message': 'Sensor is not registered'})
        print('\r\nERROR Get {} Sensor: Sensor is not registered [{},{}]\r\n'.format(xxx, username, devicename))
        return response, status.HTTP_404_NOT_FOUND

    #print(sensor)
    if sensor["configured"] == 0:
        response = json.dumps({'status': 'NG', 'message': 'Sensor is not yet configured'})
        print('\r\nERROR Get {} Sensor: Sensor is yet configured [{},{}]\r\n'.format(xxx, username, devicename))
        return response, status.HTTP_400_BAD_REQUEST

    if sensor.get('address'):
        data['address'] = sensor['address']
    # note: python dict maintains insertion order so number will always be the last key
    data['number'] = int(number)
    print('enable_{}_dev {} devicename={} number={}'.format(xxx, username, devicename, number))

    do_enable = data['enable']

    # communicate with device
    response, status_return = process_request(api, data)
    if status_return != 200:
        return response, status_return

    # set enabled to do_enable and configured to 1
    g_database_client.set_enable_configure_sensor(username, devicename, xxx, number, sensorname, do_enable, 1)

    # set enabled
    address = None
    if sensor.get('address'):
        address = sensor["address"]
    g_database_client.set_enable_device_peripheral_configuration(username, devicename, xxx, int(number), address, do_enable)

    return response


#
# ENABLE/DISABLE I2C
#
# - Request:
#   POST /devices/device/DEVICENAME/i2c/NUMBER/enable
#   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
#   data: { 'enable': int }
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/i2c/<number>/enable', methods=['POST'])
def enable_i2c(devicename, number):
    api = 'enable_i2c'

    # check number parameter
    number = int(number)
    if number > 4 or number < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = flask.request.get_json()

    # check parameter input
    if data['enable'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username

    # note: python dict maintains insertion order so number will always be the last key
    data['number'] = number
    print('enable_i2c {} devicename={} number={}'.format(username, devicename, number))

    return process_request(api, data)


#########################


########################################################################################################
#
# SEND FEEDBACK
#
# - Request:
#   POST /others/feedback
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'feedback': string, 'rating': int, 'contactme': boolean, 'recipient': string }
#   // recipient is temporary for testing purposes only
#
# - Response:
#  {'status': 'OK', 'message': string}
#  {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/others/feedback', methods=['POST'])
def send_feedback():
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Send Feedback: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Send Feedback: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('send_feedback {}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Send Feedback: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Send Feedback: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Send Feedback: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    # check if a parameter is empty
    data = flask.request.get_json()
    if data["feedback"] is None or data["rating"] is None or data["contactme"] is None:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Send Feedback: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST
    feedback = data['feedback']
    rating = data['rating']
    contactme = data['contactme']
    if data.get("recipient"):
        recipient = data['recipient']

    response = json.dumps({'status': 'OK', 'message': 'Feedback sent successfully.'})
    print('\r\nFeedback sent successfully: {}\r\n{}\r\n'.format(username, response))
    return response


########################################################################################################
#
# GET ABOUT
#
# - Request:
#   GET /others/ITEM
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'url': {'terms': string, 'privacy': string, 'license': string} }
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/others/<item>', methods=['GET'])
def get_item(item):
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get About: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get About: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_{} {}'.format(item, username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get About: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get About: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get About: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    # check if a parameter is empty
    url = {}
    if item == "faqs":
        url["faqs"] = "https://richmondu.com/faqs"
    elif item == "about":
        url["terms"]   = "https://richmondu.com/terms"
        url["privacy"] = "https://richmondu.com/privacy"
        url["license"] = "https://richmondu.com/license"
    else:
        response = json.dumps({'status': 'NG', 'message': 'Invalid request found'})
        print('\r\nERROR Get Item Url: Invalid request found\r\n')
        return response, status.HTTP_400_BAD_REQUEST


    msg = {'status': 'OK', 'message': 'Content queried successfully.'}
    msg['url'] = url
    response = json.dumps(msg)
    print('\r\nContent queried successfully: {}\r\n{}\r\n'.format(username, response))
    return response


########################################################################################################
#
# GET SUPPORTED I2C DEVICES
#
# - Request:
#   GET /others/i2cdevices
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'document': json_object } }
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/others/i2cdevices', methods=['GET'])
def get_supported_i2c_devices():
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get Supported I2C Devices: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get Supported I2C Devices: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_supported_i2c_devices {}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get Supported I2C Devices: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get Supported I2C Devices: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get Supported I2C Devices: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    # check if a parameter is empty
    result, document = g_storage_client.get_supported_i2c_devices()
    if not result:
        response = json.dumps({'status': 'NG', 'message': 'Could not retrieve JSON document'})
        print('\r\nERROR Get Supported I2C Devices: Could not retrieve JSON document [{}]\r\n'.format(username))
        return response, status.HTTP_500_INTERNAL_SERVER_ERROR


    msg = {'status': 'OK', 'message': 'Content queried successfully.'}
    msg['document'] = document
    response = json.dumps(msg)
    print('\r\nContent queried successfully: {}\r\n{}\r\n'.format(username, response))
    return response


########################################################################################################
#
# GET SUPPORTED SENSOR DEVICES
#
# - Request:
#   GET /others/sensordevices
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'document': json_object } }
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/others/sensordevices', methods=['GET'])
def get_supported_sensor_devices():
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get Supported Sensor Devices: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get Supported Sensor Devices: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_supported_sensor_devices {}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get Supported Sensor Devices: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get Supported Sensor Devices: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get Supported Sensor Devices: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    # check if a parameter is empty
    result, document = g_storage_client.get_supported_sensor_devices()
    if not result:
        response = json.dumps({'status': 'NG', 'message': 'Could not retrieve JSON document'})
        print('\r\nERROR Get Supported Sensor Devices: Could not retrieve JSON document [{}]\r\n'.format(username))
        return response, status.HTTP_500_INTERNAL_SERVER_ERROR


    msg = {'status': 'OK', 'message': 'Content queried successfully.'}
    msg['document'] = document
    response = json.dumps(msg)
    print('\r\nContent queried successfully: {}\r\n{}\r\n'.format(username, response))
    return response

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


def process_request_get(api, data, timeout=2):

    #print("\r\nAPI: {} {} devicename={}".format(api, data['username'], data['devicename']))

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
        return response, status.HTTP_404_NOT_FOUND

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
            response = receive_message(subtopic, timeout)
            g_messaging_client.subscribe(subtopic, subscribe=False)
        else:
            msg = {'status': 'NG', 'message': 'Could not communicate with device'}
            if new_token:
                msg['new_token'] = new_token
            response = json.dumps(msg)
            print('\r\nERROR Could not communicate with device [{}, {}]\r\n'.format(username, devicename))
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR
    except:
        msg = {'status': 'NG', 'message': 'Could not communicate with device'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nERROR Could not communicate with device [{}, {}]\r\n'.format(username, devicename))
        return response, status.HTTP_500_INTERNAL_SERVER_ERROR

    # return HTTP response
    if response is None:
        msg = {'status': 'NG', 'message': 'Device is unreachable'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nERROR Device is unreachable [{}, {}] DATETIME {}\r\n'.format(username, devicename, datetime.datetime.now()))
        return response, status.HTTP_503_SERVICE_UNAVAILABLE

    #print(response)
    msg = {'status': 'OK', 'message': 'Device accessed successfully.'}
    if new_token:
        msg['new_token'] = new_token
    try:
        msg['value'] = (json.loads(response))["value"]
        response = json.dumps(msg)
    except:
        response = json.dumps(msg)
    return response, 200


def process_request(api, data, timeout=2):

    #print("\r\nAPI: {} {} devicename={}".format(api, data['username'], data['devicename']))

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
        return response, status.HTTP_404_NOT_FOUND

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
            response = receive_message(subtopic, timeout)
            g_messaging_client.subscribe(subtopic, subscribe=False)
        else:
            msg = {'status': 'NG', 'message': 'Could not communicate with device'}
            if new_token:
                msg['new_token'] = new_token
            response = json.dumps(msg)
            print('\r\nERROR Could not communicate with device [{}, {}]\r\n'.format(username, devicename))
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR
    except:
        msg = {'status': 'NG', 'message': 'Could not communicate with device'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nERROR Could not communicate with device [{}, {}]\r\n'.format(username, devicename))
        return response, status.HTTP_500_INTERNAL_SERVER_ERROR

    # return HTTP response
    if response is None:
        msg = {'status': 'NG', 'message': 'Device is unreachable'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nERROR Device is unreachable [{}, {}] DATETIME {}\r\n'.format(username, devicename, datetime.datetime.now()))
        return response, status.HTTP_503_SERVICE_UNAVAILABLE

    #print(response)
    msg = {'status': 'OK', 'message': 'Device accessed successfully.'}
    if new_token:
        msg['new_token'] = new_token
    try:
        msg['value'] = (json.loads(response))["value"]
        response = json.dumps(msg)
    except:
        response = json.dumps(msg)
    return response, 200


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
    payload = None
    try:
        payload = jwt.decode(token, config.CONFIG_JWT_SECRET_KEY, algorithms=['HS256'])
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

def message_broker_register(deviceid, serialnumber, secure=True):
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
        # set topic permission only if secure option is enabled
        if secure:
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
        #print("RCV: {}".format(g_queue_dict))
    else:
        index = msg.topic.find(CONFIG_PREPEND_REPLY_TOPIC)
        if index == 0:
            g_queue_dict[msg.topic] = msg.payload
            #print("RCV: {}".format(g_queue_dict))

def on_amqp_message(ch, method, properties, body):
    #print("RCV: {} {}".format(method.routing_key, body))
    g_queue_dict[method.routing_key] = body
    #print("RCV: {}".format(g_queue_dict))

def receive_message(topic, timeout):
    time.sleep(1)
    i = 0
    while True:
        try:
            data = g_queue_dict[topic].decode("utf-8")
            g_queue_dict.pop(topic)
            #print("API: response={}\r\n".format(data))
            return data
        except:
            #print("x")
            time.sleep(1)
            i += 1
        if i >= timeout:
            #print("receive_message timed_out")
            break
    return None



###################################################################################
# Main entry point
###################################################################################

def initialize():
    global CONFIG_SEPARATOR
    global g_messaging_client
    global g_database_client
    global g_storage_client

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

    # Initialize S3 client
    g_storage_client = s3_client()

    # Initialize Redis client
    #g_redis_client = redis.Redis(config.CONFIG_REDIS_HOST, config.CONFIG_REDIS_PORT, 0)


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


