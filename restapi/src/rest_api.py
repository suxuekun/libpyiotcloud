import os
import ssl
import json
import time
import hmac
import hashlib
import flask
from flask_json import FlaskJSON, JsonError, json_response, as_json
from certificate_generator import certificate_generator
from messaging_client import messaging_client
from rest_api_config import config
from database import database_client
from flask_cors import CORS
from flask_api import status


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
#   { 'username': string, 'password': string }
#
# - Response:
#   {'status': 'OK', 'token': {'access': string, 'id': string, 'refresh': string} }
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user/login', methods=['POST'])
def login():
    print("login")
    data = flask.request.get_json()
    username = data['username']
    password = data['password']
    #print('login username={} password={}'.format(username, password))

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

    response = json.dumps({'status': 'OK', 'token': {'access': access, 'refresh': refresh, 'id': id} })
    print('\r\nLogin successful: {}\r\n'.format(username))
    #print('\r\nLogin successful: {}\r\n{}\r\n'.format(username, response))
    return response

########################################################################################################
#
# SIGN-UP
#
# - Request:
#   POST /user/signup
#   { 'username': string, 'password': string, 'email': string, 'givenname': string, 'familyname': string }
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user/signup', methods=['POST'])
def signup():
    data = flask.request.get_json()
    username = data['username']
    password = data['password']
    email = data['email']
    givenname = data['givenname']
    familyname = data['familyname']
    #print('signup username={} password={} email={} givenname={} familyname={}'.format(username, password, email, givenname, familyname))

    # check if a parameter is empty
    if len(username) == 0 or len(password) == 0 or len(email) == 0 or len(givenname) == 0 or len(familyname) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Signup: Empty parameter found [{}]\r\n'.format(username))
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
    result = g_database_client.add_user(username, password, email, givenname, familyname)
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
#   { 'username': string, 'confirmationcode': string }
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
#   { 'username': string }
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
#   { 'email': string }
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
#   { 'username': string, 'confirmationcode': string, 'password': string }
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user/confirm_forgot_password', methods=['POST'])
def confirm_forgot_password():
    data = flask.request.get_json()
    username = data['username']
    confirmationcode = data['confirmationcode']
    password = data['password']
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
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
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
            print('\r\nERROR Invalid authorization header\r\n')
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
    if verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Logout: Token is invalid [{}]\r\n'.format(username))
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
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
#   {'status': 'OK', 'message': string, 'info': {'email': string, 'family_name': string, 'given_name': string} }
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user', methods=['GET'])
def get_user_info():
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header [{}]\r\n'.format(username))
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


    msg = {'status': 'OK', 'message': 'Userinfo queried successfully.', 'info': info}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\nUserinfo queried successful: {}\r\n{}\r\n'.format(username, response))
    return response



#########################


########################################################################################################
#
# GET SUBSCRIPTION
#
# - Request:
#   GET /user/subscription
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#  {'status': 'OK', 'message': string, 'subscription': {'credits': string, 'type': paid} }
#  {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user/subscription', methods=['GET'])
def get_subscription():
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('get_subscription username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Userinfo: Empty parameter found\r\n')
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Userinfo: Token expired [{}]\r\n'.format(username))
        return response
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Userinfo: Token is invalid [{}]\r\n'.format(username))
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
#   POST /user/subscription
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'credits': string }
#
# - Response:
#  {'status': 'OK', 'message': string, 'subscription': {'credits': string, 'type': paid} }
#  {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user/subscription', methods=['POST'])
def set_subscription():
    data = flask.request.get_json()
    credits = data['credits']

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('set_subscription username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Userinfo: Empty parameter found\r\n')
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Userinfo: Token is invalid [{}]\r\n'.format(username))
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
#   POST /user/payment/paypalsetup
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'payment': {'return_url': string, 'cancel_url', string, 'item_sku': string, 'item_credits': string, 'item_price': string} }
#
# - Response:
#   {'status': 'OK', 'message': string, 'approval_url': string, 'paymentId': string, 'token': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user/payment/paypalsetup', methods=['POST'])
def set_payment_paypal_setup():
    data = flask.request.get_json()
    payment = data['payment']

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('set_payment_paypal_setup username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Userinfo: Empty parameter found\r\n')
        return response

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Userinfo: Token is invalid [{}]\r\n'.format(username))
        return response

    if flask.request.method != 'POST':
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Userinfo: Token is invalid [{}]\r\n'.format(username))
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
#   POST /user/payment/paypalexecute
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'payment': {'paymentId': string, 'payerId': string, 'token': string} }
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user/payment/paypalexecute', methods=['POST'])
def set_payment_paypal_execute():
    data = flask.request.get_json()
    payment = data['payment']

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('set_payment_paypal_execute username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Userinfo: Empty parameter found\r\n')
        return response

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Userinfo: Token is invalid [{}]\r\n'.format(username))
        return response

    if flask.request.method != 'POST':
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Userinfo: Token is invalid [{}]\r\n'.format(username))
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
#   POST /user/payment/paypalverify
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'payment': {'paymentId': string} }
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/user/payment/paypalverify', methods=['POST'])
def set_payment_paypal_verify():
    data = flask.request.get_json()
    payment = data['payment']

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('set_payment_paypal_verify username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Userinfo: Empty parameter found\r\n')
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Userinfo: Token is invalid [{}]\r\n'.format(username))
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response

    if flask.request.method != 'POST':
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Userinfo: Token is invalid [{}]\r\n'.format(username))
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
#   {'status': 'OK', 'message': string, 'devices': array[{'devicename': string, 'deviceid': string, 'cert': cert, 'pkey': pkey, 'ca': ca}, ...]}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices', methods=['GET'])
def get_device_list():
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('get_device_list username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Devices: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Devices: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Devices: Token is invalid [{}]\r\n'.format(username))
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
#   POST /devices/device
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   { 'devicename': string }
#
# - Response:
#   {'status': 'OK', 'message': string, 'device': {'devicename': string, 'deviceid': string, 'cert': cert, 'pkey': pkey, 'ca': ca}}
#   {'status': 'NG', 'message': string}
#
#
# DELETE DEVICE
#
# - Request:
#   DELETE /devices/device
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'devicename': string }
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/device', methods=['POST', 'DELETE'])
def register_device():
    data = flask.request.get_json()
    devicename = data['devicename']

    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('register_device username={} devicename={}'.format(username, devicename))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(devicename) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Devices: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Devices: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    if flask.request.method == 'POST':
        # check if device is registered
        if g_database_client.find_device(username, devicename):
            response = json.dumps({'status': 'NG', 'message': 'Device is already registered'})
            print('\r\nERROR Devices: Device is already registered [{},{}]\r\n'.format(username, devicename))
            return response, status.HTTP_409_CONFLICT

        cg = certificate_generator()
        cert, pkey = cg.generate(devicename, ecc=CONFIG_USE_ECC)
        ca = cg.getca()
        cert = open(cert).read()
        pkey = open(pkey).read()
        ca = open(ca).read()
        print(cert)
        print(pkey)
        print(ca)

        # add device to database
        deviceid = g_database_client.add_device(username, devicename, cert, pkey)
        print(deviceid)

        device = {"devicename": devicename, "deviceid": deviceid, "cert": cert, "pkey": pkey, "ca": ca}

        msg = {'status': 'OK', 'message': 'Devices registered successfully.', 'device': device}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nDevice registered successful: {}\r\n{}\r\n'.format(username, response))
        return response

    elif flask.request.method == 'DELETE':

        # check if device is registered
        if not g_database_client.find_device(username, devicename):
            response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
            print('\r\nERROR Devices: Device is not registered [{},{}]\r\n'.format(username, devicename))
            return response, status.HTTP_400_BAD_REQUEST

        # delete device from database
        g_database_client.delete_device(username, devicename)

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
#   {'status': 'OK', 'message': string, 'device': {'devicename': string, 'deviceid': string, 'cert': cert, 'pkey': pkey}}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/device/<devicename>', methods=['GET'])
def get_device(devicename):
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('get_device username={} devicename={}'.format(username, devicename))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(devicename) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Devices: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Devices: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Devices: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    # check if device is registered
    device = g_database_client.find_device(username, devicename)
    if not device:
        response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
        print('\r\nERROR Devices: Device is not registered [{},{}]\r\n'.format(username, devicename))
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
# GET DEVICE TRANSACTION HISTORIES
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
def get_user_histories():
    # get token from Authorization header
    auth_header_token = get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    print('get_user_histories username={}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Histories: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2: # token expired
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Histories: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Histories: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    histories = g_database_client.get_user_history(username)
    print(histories)


    msg = {'status': 'OK', 'message': 'User histories queried successfully.', 'histories': histories}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    return response


#########################


########################################################################################################
# GET  /devices/device/<devicename>/xxx
# POST /devices/device/xxx
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
#   POST /devices/device/status
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'devicename': string, 'value': string }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': string}
#   { 'status': 'NG', 'message': string}
#
@app.route('/devices/device/status', methods=['POST'])
def set_status():
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
#   POST /devices/device/gpio
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'devicename': string, 'number': string, 'value': string }
# 
# - Response:
#   { 'status': 'OK', 'message': string, 'value': string }
#   { 'status': 'NG', 'message': string}
# 
@app.route('/devices/device/gpio', methods=['POST'])
def set_gpio():
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
#   POST /devices/device/uart
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'devicename': string, 'value': string }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': string }
#   { 'status': 'NG', 'message': string}
#
@app.route('/devices/device/uart', methods=['POST'])
def write_uart():
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
    data['username'] = g_database_client.get_username_from_token(data['token'])
    print('write_uart username={}'.format(data['username']))

    return process_request(api, data)

#
# SET NOTIFICATIONS
#
# - Request:
#   POST /devices/device/notification
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'devicename': string, 'recipient': string, 'message': string, 'options': string }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': string }
#   { 'status': 'NG', 'message': string}
#
@app.route('/devices/device/notification', methods=['POST'])
def trigger_notification():
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
        if i >= 5:
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


