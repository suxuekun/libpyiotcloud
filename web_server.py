import os
import ssl
import json
import time
import hmac
import hashlib
from flask import Flask, request
from flask_json import FlaskJSON, JsonError, json_response, as_json
from certificate_generator import certificate_generator
from messaging_client import messaging_client
from web_server_config import config
from web_server_database import database_client



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
app = Flask(__name__)
FlaskJSON(app)



###################################################################################
# HTTP REST APIs
###################################################################################

@app.route('/')
def index():
    return 'Hello, World!'



@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data['username']
    password = data['password']
    email = data['email']
    givenname = data['givenname']
    familyname = data['familyname']

    # check if username is already in database
    if g_database_client.find_user(username):
        print("Username {} already exist!\r\n".format(username))
        response = {}
        response['status'] = 'NG, username already exist'
        response = json.dumps(response)
        return response

    # add entry in database
    result = g_database_client.add_user(username, password, email, givenname, familyname)
    if not result:
        response = {}
        response['status'] = 'NG'
        response = json.dumps(response)
        return response
    confirmationcode = g_database_client.get_confirmationcode(username)

    response = {}
    response['status'] = 'OK'
    if confirmationcode:
        response['confirmationcode'] = confirmationcode
    response = json.dumps(response)
    return response

@app.route('/confirm_signup', methods=['POST'])
def confirm_signup():
    data = request.get_json()
    username = data['username']
    confirmationcode = data['confirmationcode']

    # confirm user in database
    result = g_database_client.confirm_user(username, confirmationcode)
    if not result:
        print("Incorrect code! {} {}\r\n".format(username, confirmationcode))
        response = {}
        response['status'] = 'NG, incorrect code'
        response = json.dumps(response)
        return response

    response = {}
    response['status'] = 'OK'
    response = json.dumps(response)
    return response


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if not g_database_client.find_user(username):
        response = {}
        response['status'] = 'NG, username does not exist'
        response['token'] = 'Unknown'
        response = json.dumps(response)
        return response

    token = g_database_client.login(username, password)
    if not token:
        response = {}
        response['status'] = 'NG, password is incorrect'
        response['token'] = 'Unknown'
        response = json.dumps(response)
        return response

    response = {}
    response['status'] = 'OK'
    response['token'] = token
    response = json.dumps(response)
    return response


@app.route('/get_device_list')
def get_device_list():
    data = request.get_json()
    username = data['username']
    token = data['token']
    print('get_device_list username={} token={}'.format(username, token))

    # check if username and token is valid
    if not g_database_client.verify_token(username, token):
        response = {}
        response['status'] = 'NG, token is incorrect'
        response = json.dumps(response)
        print('NG, token is incorrect')
        return response

    devices = g_database_client.get_devices(username)
    print(devices)

    response = {}
    response['status'] = 'OK'
    response["devices"] = devices
    response = json.dumps(response)
    return response

@app.route('/register_device', methods=['POST'])
def register_device():
    data = request.get_json()
    username = data['username']
    token = data['token']
    devicename = data['devicename']
    print('username={} token={} devicename={}'.format(username, token, devicename))

    # check if username and token is valid
    if not g_database_client.verify_token(username, token):
        response = {}
        response['status'] = 'NG, token is incorrect'
        response = json.dumps(response)
        print('NG, token is incorrect')
        return response

    # check if device is registered
    if g_database_client.find_device(username, devicename):
        response = {}
        response['status'] = 'NG, device already registered'
        response = json.dumps(response)
        print('NG, device already registered')
        return response

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

    response = {}
    response['status'] = 'OK'
    response["devicename"] = devicename
    response["deviceid"] = deviceid
    response["cert"] = cert
    response["pkey"] = pkey
    response["ca"] = ca
    response = json.dumps(response)
    return response

@app.route('/unregister_device', methods=['POST'])
def unregister_device():
    data = request.get_json()
    username = data['username']
    token = data['token']
    devicename = data['devicename']
    print('username={} token={} devicename={}'.format(username, token, devicename))

    # check if username and token is valid
    if not g_database_client.verify_token(username, token):
        response = {}
        response['status'] = 'NG, token is incorrect'
        response = json.dumps(response)
        print('NG, token is incorrect')
        return response

    # check if device is registered
    if not g_database_client.find_device(username, devicename):
        response = {}
        response['status'] = 'NG, device not registered'
        response = json.dumps(response)
        print('NG, device not registered')
        return response

    # delete device from database
    g_database_client.delete_device(username, devicename)

    response = {}
    response['status'] = 'OK'
    response = json.dumps(response)
    return response



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
    data = request.get_json()
    print("\r\nAPI: {} request={}".format(api, data))

    username = data['username']
    token = data['token']
    devicename = data['devicename']
    # check if username and token is valid
    if not g_database_client.verify_token(username, token):
        return 'Device token is not valid!', 400
    # check if device is registered
    if not g_database_client.find_device(username, devicename):
        return 'Device is not registered!', 400
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
            print("process_request Please check if device is connected with correct deviceid=\r\n{}".format(deviceid))
            response = None
    except:
        print("process_request: exception!")
        response = None

    # return HTTP response
    if response is None:
        return 'Device is not running!', 400
    return response


@app.route('/get_gpio')
def get_gpio():
    api = 'get_gpio'
    return process_request(api)

@app.route('/set_gpio', methods=['POST'])
def set_gpio():
    api = 'set_gpio'
    return process_request(api)


@app.route('/get_rtc')
def get_rtc():
    api = 'get_rtc'
    return process_request(api)

@app.route('/set_rtc', methods=['POST'])
def set_rtc():
    api = 'set_rtc'
    return process_request(api)


@app.route('/get_status')
def get_status():
    api = 'get_status'
    return process_request(api)

@app.route('/set_status', methods=['POST'])
def set_status():
    api = 'set_status'
    return process_request(api)


@app.route('/get_mac')
def get_mac():
    api = 'get_mac'
    return process_request(api)

@app.route('/set_mac', methods=['POST'])
def set_mac():
    api = 'set_mac'
    return process_request(api)


@app.route('/get_ip')
def get_ip():
    api = 'get_ip'
    return process_request(api)

@app.route('/get_subnet')
def get_subnet():
    api = 'get_subnet'
    return process_request(api)

@app.route('/get_gateway')
def get_gateway():
    api = 'get_gateway'
    return process_request(api)


@app.route('/write_uart', methods=['POST'])
def write_uart():
    api = 'write_uart'
    return process_request(api)



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
            #time.sleep(1)
            i += 1
        if i > 5:
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
        g_messaging_client = messaging_client(CONFIG_USE_AMQP, on_mqtt_message)
        g_messaging_client.set_server(config.CONFIG_HOST, config.CONFIG_MQTT_TLS_PORT)
    g_messaging_client.set_user_pass(config.CONFIG_USERNAME, config.CONFIG_PASSWORD)
    g_messaging_client.set_tls(config.CONFIG_TLS_CA, config.CONFIG_TLS_CERT, config.CONFIG_TLS_PKEY)
    g_messaging_client.initialize()

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


