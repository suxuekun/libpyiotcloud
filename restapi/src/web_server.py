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
from web_server_config import config
from web_server_database import database_client
from flask_cors import CORS
from flask_api import status


###################################################################################
# Some configurations
###################################################################################

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
# POST /user/login
# { 'username': string, 'password': string }
# Response:
# {'status': 'OK', 'token': string}
# {'status': 'NG', 'message': string}
########################################################################################################
@app.route('/user/login', methods=['POST'])
def login():
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
    if not g_database_client.find_user(username):
        # NOTE:
        # its not good to provide a specific error message for LOGIN
        # because it provides additional info for hackers
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Login: Username does not exist [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    # check if password is valid
    token = g_database_client.login(username, password)
    if not token:
        # NOTE:
        # its not good to provide a specific error message for LOGIN
        # because it provides additional info for hackers
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Login: Password is incorrect [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    response = json.dumps({'status': 'OK', 'token': token})
    print('\r\nLogin successful: {}\r\n{}\r\n'.format(username, response))
    return response

########################################################################################################
# POST /user/signup
# { 'username': string, 'password': string, 'email': string, 'givenname': string, 'familyname': string }
# Response:
# {'status': 'OK', 'message': string}
# {'status': 'NG', 'message': string}
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
# POST /user/confirm_signup
# { 'username': string, 'confirmationcode': string }
# Response:
# {'status': 'OK', 'message': string}
# {'status': 'NG', 'message': string}
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
# POST /user/resend_confirmation_code
# { 'username': string }
# Response:
# {'status': 'OK', 'message': string}
# {'status': 'NG', 'message': string}
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
# POST /user/forgot_password
# { 'username': string, 'confirmationcode': string }
# Response:
# {'status': 'OK', 'message': string, 'username': string}
# {'status': 'NG', 'message': string}
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
# POST /user/confirm_forgot_password
# { 'username': string, 'confirmationcode': string, 'password': string }
# Response:
# {'status': 'OK', 'message': string}
# {'status': 'NG', 'message': string}
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
# POST /user/logout
# { 'username': string, 'token': string }
# Response:
# {'status': 'OK', 'message': string}
# {'status': 'NG', 'message': string}
########################################################################################################
@app.route('/user/logout', methods=['POST'])
def logout():
    data = flask.request.get_json()
    try:
        username = data['username']
        token = data['token']
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
    if not g_database_client.verify_token(username, token):
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Logout: Token is invalid [{}]\r\n'.format(username))
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response

    g_database_client.logout(token)

    response = json.dumps({'status': 'OK', 'message': 'User logout successfully.'})
    print('\r\nLogout successful: {}\r\n{}\r\n'.format(username, response))
    return response


########################################################################################################
# POST /user
# { 'username': string, 'token': string }
# Response:
# {'status': 'OK', 'message': string, 'info': string}
# {'status': 'NG', 'message': string}
########################################################################################################
@app.route('/user', methods=['POST', 'GET'])
def get_user_info():
    data = flask.request.get_json()
    username = data['username']
    token = data['token']
    print('get_user_info username={} token={}'.format(username, token))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Userinfo: Empty parameter found\r\n')
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response

    # check if username and token is valid
    if not g_database_client.verify_token(username, token):
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Userinfo: Token is invalid [{}]\r\n'.format(username))
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response

    info = g_database_client.get_user_info(token)
    response = json.dumps({'status': 'OK', 'message': 'Userinfo queried successfully.', 'info': info})
    print('\r\nUserinfo queried successful: {}\r\n{}\r\n'.format(username, response))
    return response



#########################


########################################################################################################
# POST/DELETE/GET /user/subscription
# { 'username': string, 'token': string }
# Response:
# {'status': 'OK', 'message': string, 'subscription': string}}
# {'status': 'NG', 'message': string}
########################################################################################################
@app.route('/user/subscription', methods=['POST', 'DELETE', 'PATCH'])
def get_subscription():
    data = flask.request.get_json()
    username = data['username']
    token = data['token']
    print('get_subscription username={} token={}'.format(username, token))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Userinfo: Empty parameter found\r\n')
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response

    # check if username and token is valid
    if not g_database_client.verify_token(username, token):
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Userinfo: Token is invalid [{}]\r\n'.format(username))
        # NOTE:
        # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
        return response

    if flask.request.method == 'POST':
        group = g_database_client.add_user_to_group(username)
        response = json.dumps({'status': 'OK', 'message': 'User subscribed successfully.', 'group': group})
        print('\r\nUser subscribed successful: {}\r\n{}\r\n'.format(username, response))
        return response

    elif flask.request.method == 'DELETE':
        group = g_database_client.remove_user_from_group(username)
        response = json.dumps({'status': 'OK', 'message': 'User unsubscribed successfully.', 'group': group})
        print('\r\nUser unsubscribed successful: {}\r\n{}\r\n'.format(username, response))
        return response

    elif flask.request.method == 'PATCH': # todo: replace PATCH with GET, investigate why GET is not working
        group = g_database_client.get_user_group(username)
        response = json.dumps({'status': 'OK', 'message': 'User subscription queried successfully.', 'group': group})
        print('\r\nUser subscription queried successful: {}\r\n{}\r\n'.format(username, response))
        return response


#########################


########################################################################################################
# NOTE: GET is not working so use POST instead
# POST /devices
# { 'username': string, 'token': string }
# Response:
# {'status': 'OK', 'message': string, 'devices': array[{'devicename': string, ...}, {'devicename': string, ...}]}
# {'status': 'NG', 'message': string}
########################################################################################################
@app.route('/devices', methods=['POST', 'GET'])
def get_device_list():
    data = flask.request.get_json()
    username = data['username']
    token = data['token']
    #print('get_device_list username={} token={}'.format(username, token))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Devices: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    if not g_database_client.verify_token(username, token):
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Devices: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    devices = g_database_client.get_devices(username)
    print(devices)

    response = json.dumps({'status': 'OK', 'message': 'Devices queried successfully.', 'devices': devices})
    return response

########################################################################################################
# POST/DELETE/GET /devices/device
# { 'username': string, 'token': string, 'devicename': string }
# Response:
# {'status': 'OK', 'message': string, 'device': {'devicename': string, ...}, {'devicename': string, ...}}
# {'status': 'NG', 'message': string}
########################################################################################################
@app.route('/devices/device', methods=['POST', 'DELETE', 'PATCH'])
def register_device():
    data = flask.request.get_json()
    username = data['username']
    token = data['token']
    devicename = data['devicename']
    #print('username={} token={} devicename={}'.format(username, token, devicename))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(devicename) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Devices: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    if not g_database_client.verify_token(username, token):
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
        cert, pkey = cg.generate(devicename)
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
        response = json.dumps({'status': 'OK', 'message': 'Devices registered successfully.', 'device': device})
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

        response = json.dumps({'status': 'OK', 'message': 'Devices unregistered successfully.'})
        print('\r\nDevice unregistered successful: {}\r\n{}\r\n'.format(username, response))
        return response

    elif flask.request.method == 'PATCH': # todo: replace PATCH with GET, investigate why GET is not working

        # check if device is registered
        device = g_database_client.find_device(username, devicename)
        if not device:
            response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
            print('\r\nERROR Devices: Device is not registered [{},{}]\r\n'.format(username, devicename))
            return response, status.HTTP_400_BAD_REQUEST

        print(device)
        response = json.dumps({'status': 'OK', 'message': 'Devices queried successfully.', 'device': device})
        print('\r\nDevice queried successful: {}\r\n{}\r\n'.format(username, response))
        return response



#########################


########################################################################################################
# NOTE: GET is not working so use POST instead
# POST /user/histories
# { 'username': string, 'token': string }
# Response:
# {'status': 'OK', 'message': string, 'histories': array[{'devicename': string, ...}, {'devicename': string, ...}]}
# {'status': 'NG', 'message': string}
########################################################################################################
@app.route('/user/histories', methods=['POST', 'GET'])
def get_user_histories():
    data = flask.request.get_json()
    username = data['username']
    token = data['token']
    #print('get_user_histories username={} token={}'.format(username, token))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Histories: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    if not g_database_client.verify_token(username, token):
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Histories: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED

    histories = g_database_client.get_user_history(username)
    print(histories)

    response = json.dumps({'status': 'OK', 'message': 'User histories queried successfully.', 'histories': histories})
    return response


#########################


########################################################################################################
# POST/GET/PUT /devices/device/get_ip
# { 'username': string, 'token': string, 'devicename': string }
# Response:
# {'status': 'OK', 'message': string, 'value': value}
# {'status': 'NG', 'message': string}
########################################################################################################
@app.route('/devices/device/ip', methods=['POST', 'GET', 'PUT'])
def get_ip():
    if flask.request.method == 'POST' or flask.request.method == 'GET':
        api = 'get_ip'
        return process_request(api)
    elif flask.request.method == 'PUT':
        return None # TODO

@app.route('/devices/device/subnet', methods=['POST', 'GET', 'PUT'])
def get_subnet():
    if flask.request.method == 'POST' or flask.request.method == 'GET':
        api = 'get_subnet'
        return process_request(api)
    elif flask.request.method == 'PUT':
        return None # TODO

@app.route('/devices/device/gateway', methods=['POST', 'GET', 'PUT'])
def get_gateway():
    if flask.request.method == 'POST' or flask.request.method == 'GET':
        api = 'get_gateway'
        return process_request(api)
    elif flask.request.method == 'PUT':
        return None # TODO

@app.route('/devices/device/mac', methods=['POST', 'GET', 'PUT'])
def get_mac():
    if flask.request.method == 'POST' or flask.request.method == 'GET':
        api = 'get_mac'
        return process_request(api)
    elif flask.request.method == 'PUT':
        api = 'set_mac'
        return process_request(api)



@app.route('/devices/device/gpio', methods=['POST', 'GET', 'PUT'])
def get_gpio():
    if flask.request.method == 'POST' or flask.request.method == 'GET':
        api = 'get_gpio'
        return process_request(api)
    elif flask.request.method == 'PUT':
        api = 'set_gpio'
        return process_request(api)

@app.route('/devices/device/rtc', methods=['POST', 'GET', 'PUT'])
def get_rtc():
    if flask.request.method == 'POST' or flask.request.method == 'GET':
        api = 'get_rtc'
        return process_request(api)
    elif flask.request.method == 'PUT':
        api = 'set_rtc'
        return process_request(api)



@app.route('/devices/device/uart', methods=['POST', 'GET', 'PUT'])
def write_uart():
    if flask.request.method == 'POST' or flask.request.method == 'GET':
        api = 'read_uart'
        return None
    elif flask.request.method == 'PUT':
        api = 'write_uart'
        return process_request(api)


@app.route('/devices/device/notification', methods=['POST', 'GET', 'PUT'])
def trigger_notification():
    if flask.request.method == 'POST' or flask.request.method == 'GET':
        return None
    elif flask.request.method == 'PUT':
        api = 'trigger_notification'
        return process_request(api)


@app.route('/devices/device/status', methods=['POST', 'GET', 'PUT'])
def get_status():
    if flask.request.method == 'POST' or flask.request.method == 'GET':
        api = 'get_status'
        return process_request(api)
    elif flask.request.method == 'PUT':
        api = 'set_status'
        return process_request(api)



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

def process_request(api):

    # parse HTTP request
    data = flask.request.get_json()
    print("\r\nAPI: {} request={}".format(api, data))

    username = data['username']
    token = data['token']
    devicename = data['devicename']

    # check if username and token is valid
    if not g_database_client.verify_token(username, token):
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
            response = json.dumps({'status': 'NG', 'message': 'Could not communicate with device'})
            print('\r\nERROR Could not communicate with device [{}, {}]\r\n'.format(username, devicename))
            return response, status.HTTP_401_UNAUTHORIZED
    except:
        response = json.dumps({'status': 'NG', 'message': 'Could not communicate with device'})
        print('\r\nERROR Could not communicate with device [{}, {}]\r\n'.format(username, devicename))
        return response, status.HTTP_401_UNAUTHORIZED

    # return HTTP response
    if response is None:
        response = json.dumps({'status': 'NG', 'message': 'Could not communicate with device'})
        print('\r\nERROR Could not communicate with device [{}, {}]\r\n'.format(username, devicename))
        return response, status.HTTP_401_UNAUTHORIZED

    print(response)
    try:
        response = json.dumps({'status': 'OK', 'message': 'Device accessed successfully.', 'value': (json.loads(response))["value"]})
    except:
        response = json.dumps({'status': 'OK', 'message': 'Device accessed successfully.'})
    return response



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


