import ssl
import json
import time
import argparse
import sys
import hmac
import hashlib
from flask import Flask, request
from flask_json import FlaskJSON, JsonError, json_response, as_json
from certificate_generator import certificate_generator
from messaging_client import messaging_client
from pymongo import MongoClient



###################################################################################
# Enable to use AMPQ for webserver-to-messagebroker communication
# Disable to use MQTT for webserver-to-messagebroker communication
CONFIG_USE_AMQP = True
###################################################################################



###################################################################################
# HTTP configurations
###################################################################################

CONFIG_HTTP_HOST            = "localhost"
CONFIG_HTTP_PORT            = 443
CONFIG_HTTP_TLS_CA          = "cert/rootca.pem"
CONFIG_HTTP_TLS_CERT        = "cert/server_cert.pem"
CONFIG_HTTP_TLS_PKEY        = "cert/server_pkey.pem"

CONFIG_USERNAME             = "guest"
CONFIG_PASSWORD             = "guest"
CONFIG_TLS_CA               = "cert/rootca.pem"
CONFIG_TLS_CERT             = "cert/server_cert.pem"
CONFIG_TLS_PKEY             = "cert/server_pkey.pem"

CONFIG_HOST                 = "localhost"
CONFIG_MQTT_TLS_PORT        = 8883
CONFIG_AMQP_TLS_PORT        = 5671

CONFIG_SEPARATOR            = '/'
CONFIG_PREPEND_REPLY_TOPIC  = "server"



###################################################################################
# global variables
###################################################################################

g_certificate_generator = None
g_messaging_client = None
g_db_client = None
app = Flask(__name__)
g_queue_dict  = {}
FlaskJSON(app)



###################################################################################
# HTTP REST APIs
###################################################################################

def compute_secret(timestamp, username, password):
    key = timestamp.encode('utf-8')
    message = (username + password).encode('utf-8')
    secret = hmac.new(key, message, hashlib.sha1).hexdigest()
    return secret

def display_users():
    users = g_db_client['profiles']
    if users:
        for user in users.find({},{'username': 1, 'password':1, 'secret':1}):
            print(user)

def find_user(username):
    users = g_db_client['profiles']
    if users:
        for user in users.find({},{'username': 1}):
            #print(user)
            if user['username'] == username:
                return True
    return False

def check_password(username, password):
    users = g_db_client['profiles']
    if users:
        for user in users.find({},{'username': 1, 'password':1}):
            #print(user)
            if user['username'] == username and user['password'] == password:
                return True
    return False

def get_secret(username):
    users = g_db_client['profiles']
    if users:
        for user in users.find({},{'username': 1, 'secret': 1}):
            #print(user)
            if user['username'] == username:
                return user['secret']
    return None

def check_secret(username, secret):
    users = g_db_client['profiles']
    if users:
        for user in users.find({},{'username': 1, 'secret':1}):
            #print(user)
            if user['username'] == username and user['secret'] == secret:
                return True
    return False

def delete_user(username):
    users = g_db_client['profiles']
    if users:
        myquery = { 'username': username }
        users.delete_one(myquery)

def add_user(username, password):
    timestamp = str(int(time.time()))
    secret = compute_secret(timestamp, username, password)
    profile = {}
    profile['username']  = username
    profile['password']  = password
    profile['timestamp'] = timestamp
    profile['secret']    = secret
    #print('post={}'.format(profile))
    g_db_client.profiles.insert_one(profile)

def compute_deviceid(timestamp, username, devicename):
    key = timestamp.encode('utf-8')
    message = (username + devicename).encode('utf-8')
    secret = hmac.new(key, message, hashlib.sha1).hexdigest()
    return secret

def display_devices(username):
    devices = g_db_client['devices']
    if devices:
        for device in devices.find({},{'username': 1, 'devicename':1, 'deviceid': 1, 'timestamp':1, 'cert':1, 'pkey':1}):
            if device['username'] == username:
                print(device)

def get_devices(username):
    device_list = []
    devices = g_db_client['devices']
    if devices:
        for device in devices.find({},{'username': 1, 'devicename':1, 'deviceid': 1, 'timestamp':1, 'cert':1, 'pkey':1}):
            if device['username'] == username:
                device.pop('username')
                device.pop('timestamp')
                device.pop('_id')
                device_list.append(device)
    return device_list

def add_device(username, devicename, cert, pkey):
    timestamp = str(int(time.time()))
    deviceid = compute_deviceid(timestamp, username, devicename)
    device = {}
    device['username']   = username
    device['devicename'] = devicename
    device['deviceid']   = deviceid
    device['timestamp']  = timestamp
    device['cert']       = cert
    device['pkey']       = pkey
    #print('post={}'.format(device))
    g_db_client.devices.insert_one(device)
    return deviceid

def delete_device(username, devicename):
    devices = g_db_client['devices']
    if devices:
        myquery = { 'username': username, 'devicename': devicename }
        devices.delete_one(myquery)

def find_device(username, devicename):
    devices = g_db_client['devices']
    if devices:
        for device in devices.find({},{'username': 1, 'devicename': 1}):
            #print(user)
            if device['username'] == username and device['devicename'] == devicename:
                return True
    return False

def get_deviceid(username, devicename):
    devices = g_db_client['devices']
    if devices:
        for device in devices.find({},{'username': 1, 'devicename': 1, 'deviceid': 1}):
            #print(user)
            if device['username'] == username and device['devicename'] == devicename:
                return device['deviceid']
    return None



@app.route('/')
def index():
    return 'Hello, World!'



@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data['username']
    password = data['password']

    # check if username is already in database
    print("\r\nBefore addition...")
#    delete_user(username)
    if find_user(username):
        print("Username {} already exist!\r\n".format(username))
        response = {}
        response['status'] = 'NG, username already exist'
        response = json.dumps(response)
        return response

    # add entry in database
    add_user(username, password)

    # Print database entries
    print("\r\nAfter addition...")
    display_users()

    response = {}
    response['status'] = 'OK'
    response = json.dumps(response)
    return response

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if not find_user(username):
        response = {}
        response['status'] = 'NG, username does not exist'
        response['secret'] = 'Unknown'
        response = json.dumps(response)
        return response

    if not check_password(username, password):
        response = {}
        response['status'] = 'NG, password is incorrect'
        response['secret'] = 'Unknown'
        response = json.dumps(response)
        return response

    response = {}
    response['status'] = 'OK'
    response['secret'] = get_secret(username)
    response = json.dumps(response)
    return response


@app.route('/get_device_list')
def get_device_list():
    data = request.get_json()
    username = data['username']
    secret = data['secret']
    print('get_device_list username={} secret={}'.format(username, secret))

    # check if username and secret is valid
    if not check_secret(username, secret):
        response = {}
        response['status'] = 'NG, secret is incorrect'
        response = json.dumps(response)
        print('NG, secret is incorrect')
        return response

    devices = get_devices(username)
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
    secret = data['secret']
    devicename = data['devicename']
    print('username={} secret={} devicename={}'.format(username, secret, devicename))

    # check if username and secret is valid
    if not check_secret(username, secret):
        response = {}
        response['status'] = 'NG, secret is incorrect'
        response = json.dumps(response)
        print('NG, secret is incorrect')
        return response

    # check if device is registered
    if find_device(username, devicename):
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
    deviceid = add_device(username, devicename, cert, pkey)
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
    secret = data['secret']
    devicename = data['devicename']
    print('username={} secret={} devicename={}'.format(username, secret, devicename))

    # check if username and secret is valid
    if not check_secret(username, secret):
        response = {}
        response['status'] = 'NG, secret is incorrect'
        response = json.dumps(response)
        print('NG, secret is incorrect')
        return response

    # check if device is registered
    if not find_device(username, devicename):
        response = {}
        response['status'] = 'NG, device not registered'
        response = json.dumps(response)
        print('NG, device not registered')
        return response

    # delete device from database
    delete_device(username, devicename)

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
    data.pop('secret')
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
    secret = data['secret']
    devicename = data['devicename']
    # check if username and secret is valid
    if not check_secret(username, secret):
        return 'Device secret is not valid!', 400
    # check if device is registered
    if not find_device(username, devicename):
        return 'Device is not registered!', 400
    # get deviceid for subscribe purpose (AMQP)
    deviceid = get_deviceid(username, devicename)

    # construct publish/subscribe topics and payloads
    pubtopic = generate_publish_topic(data, deviceid, api, CONFIG_SEPARATOR)
    payload = generate_publish_payload(data)
    subtopic = generate_subscribe_topic(pubtopic, CONFIG_SEPARATOR)

    try:
        # subscribe for response
        g_messaging_client.subscribe(subtopic, subscribe=True, deviceid=deviceid)

        # publish request
        g_messaging_client.publish(pubtopic, payload)

        # receive response
        response = receive_message(subtopic)
        g_messaging_client.subscribe(subtopic, subscribe=False)

    except:
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
# HTTP server initialization
###################################################################################

def init_http_server():
    print(CONFIG_HTTP_HOST)
    context = (CONFIG_HTTP_TLS_CERT, CONFIG_HTTP_TLS_PKEY)
    app.run(ssl_context = context,
        host     = CONFIG_HTTP_HOST, 
        port     = CONFIG_HTTP_PORT, 
        threaded = True, 
        debug    = True)
    return app


def init_db_client():
    mongo_client = MongoClient('localhost', 27017)
    client = mongo_client['iotcloud-database']
    return client



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

def parse_arguments(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--USE_AMQP', required=False, default=1 if CONFIG_USE_AMQP else 0, help='Use AMQP instead of MQTT')
    parser.add_argument('--USE_HOST', required=False, default=CONFIG_HOST, help='Message broker to connect to')
    return parser.parse_args(argv)


if __name__ == '__main__':

    args = parse_arguments(sys.argv[1:])

    CONFIG_USE_AMQP = True if int((args.USE_AMQP))==1 else False
    CONFIG_SEPARATOR = "." if int((args.USE_AMQP))==1 else "/"
    CONFIG_HOST = args.USE_HOST
    print("USE_AMQP={}".format(args.USE_AMQP))
    print("USE_HOST={}".format(args.USE_HOST))


    # Initialize MQTT/AMQP client
    print("Using {} for webserver-messagebroker communication!".format("AMQP" if CONFIG_USE_AMQP else "MQTT"))
    if CONFIG_USE_AMQP:
        g_messaging_client = messaging_client(CONFIG_USE_AMQP, on_amqp_message)
        g_messaging_client.set_server(CONFIG_HOST, CONFIG_AMQP_TLS_PORT)
    else:
        g_messaging_client = messaging_client(CONFIG_USE_AMQP, on_mqtt_message)
        g_messaging_client.set_server(CONFIG_HOST, CONFIG_MQTT_TLS_PORT)
    g_messaging_client.set_user_pass(CONFIG_USERNAME, CONFIG_PASSWORD)
    g_messaging_client.set_tls(CONFIG_TLS_CA, CONFIG_TLS_CERT, CONFIG_TLS_PKEY)
    g_messaging_client.initialize()


    # Initialize Database client
    g_db_client = init_db_client()

    # Initialize HTTP server
    app = init_http_server()

    # Initialize certificate generator
    #g_certificate_generator = certificate_generator()

