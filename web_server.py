import ssl
import json
import time
import argparse
import sys
from flask import Flask, request
from flask_json import FlaskJSON, JsonError, json_response, as_json
from certificate_generator import certificate_generator
from messaging_client import messaging_client



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

CONFIG_MQTT_HOST            = "localhost"
CONFIG_MQTT_TLS_PORT        = 8883
CONFIG_AMQP_HOST            = "localhost"
CONFIG_AMQP_TLS_PORT        = 5671

CONFIG_SEPARATOR            = '/'
CONFIG_PREPEND_REPLY_TOPIC  = "server"



###################################################################################
# global variables
###################################################################################

g_certificate_generator = None
g_messaging_client = None
g_http_server = Flask(__name__)
g_queue_dict  = {}
FlaskJSON(g_http_server)



###################################################################################
# HTTP REST APIs
###################################################################################

@g_http_server.route('/')
def index():
    return 'Hello, World!'

@g_http_server.route('/register_device', methods=['POST'])
def register_device():
    data = request.get_json()
    customer_id = data['customer_id']
    device_name = data['device_name']
    print('customer_id={} device_name={}'.format(customer_id, device_name))

    # TODO: check if device name is valid

    cert, pkey = g_certificate_generator.generate(device_name)
    ca = g_certificate_generator.getca()
    print(cert)
    print(pkey)
    print(ca)

    # TODO: the certificates should be uploaded in Amazon S3, then add the links here

    response = {}
    response["cert"] = cert
    response["pkey"] = pkey
    response["ca"] = ca
    response = json.dumps(response)
    return response

@g_http_server.route('/unregister_device', methods=['POST'])
def unregister_device():
    data = request.get_json()
    customer_id = data['customer_id']
    device_name = data['device_name']
    print('device_name={}'.format(device_name))
    data.pop('customer_id')
    data.pop('device_name')

    return 'unregister_device'



def generate_publish_topic(data, api, separator):
    customer_id = data['customer_id']
    device_name = data['device_name']
    topic = customer_id + separator + device_name + separator + api 
    return topic

def generate_publish_payload(data):
    data.pop('customer_id')
    data.pop('device_name')
    payload = json.dumps(data)
    return payload

def generate_subscribe_topic(topic, separator):
    topic = CONFIG_PREPEND_REPLY_TOPIC + separator + topic
    return topic

def process_request(api):

    # parse HTTP request
    data = request.get_json()
    print("\r\nAPI: {} request={}".format(api, data))

    # construct publish/subscribe topics and payloads
    pubtopic = generate_publish_topic(data, api, CONFIG_SEPARATOR)
    payload = generate_publish_payload(data)
    subtopic = generate_subscribe_topic(pubtopic, CONFIG_SEPARATOR)

    # subscribe for response
    g_messaging_client.subscribe(subtopic, subscribe=True)

    # publish request
    g_messaging_client.publish(pubtopic, payload)

    # receive response
    response = receive_message(subtopic)
    g_messaging_client.subscribe(subtopic, subscribe=False)

    # return HTTP response
    if response is None:
        return api
    return response


@g_http_server.route('/get_gpio')
def get_gpio():
    api = 'get_gpio'
    return process_request(api)

@g_http_server.route('/set_gpio', methods=['POST'])
def set_gpio():
    api = 'set_gpio'
    return process_request(api)


@g_http_server.route('/get_rtc')
def get_rtc():
    api = 'get_rtc'
    return process_request(api)

@g_http_server.route('/set_rtc', methods=['POST'])
def set_rtc():
    api = 'set_rtc'
    return process_request(api)


@g_http_server.route('/get_status')
def get_status():
    api = 'get_status'
    return process_request(api)

@g_http_server.route('/set_status', methods=['POST'])
def set_status():
    api = 'set_status'
    return process_request(api)


@g_http_server.route('/get_mac')
def get_mac():
    api = 'get_mac'
    return process_request(api)

@g_http_server.route('/set_mac', methods=['POST'])
def set_mac():
    api = 'set_mac'
    return process_request(api)


@g_http_server.route('/get_ip')
def get_ip():
    api = 'get_ip'
    return process_request(api)

@g_http_server.route('/get_subnet')
def get_subnet():
    api = 'get_subnet'
    return process_request(api)

@g_http_server.route('/get_gateway')
def get_gateway():
    api = 'get_gateway'
    return process_request(api)


@g_http_server.route('/write_uart', methods=['POST'])
def write_uart():
    api = 'write_uart'
    return process_request(api)



###################################################################################
# HTTP server initialization
###################################################################################

def init_http_server():
    context = (CONFIG_HTTP_TLS_CERT, CONFIG_HTTP_TLS_PKEY)
    g_http_server.run(ssl_context = context,
        host     = CONFIG_HTTP_HOST, 
        port     = CONFIG_HTTP_PORT, 
        threaded = True, 
        debug    = True)
    return g_http_server


def init_db_client():
    #client = MongoClient('localhost', 27017)
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

def parse_arguments(argv, default_value):

    parser = argparse.ArgumentParser()
    parser.add_argument('--USE_AMQP', required=False, default=default_value, help='Use AMQP instead of MQTT')
    return parser.parse_args(argv)


if __name__ == '__main__':

    default_value = 1 if CONFIG_USE_AMQP else 0
    args = parse_arguments(sys.argv[1:], default_value)

    CONFIG_USE_AMQP = True if int((args.USE_AMQP))==1 else False
    CONFIG_SEPARATOR = "." if int((args.USE_AMQP))==1 else "/"
    print("USE_AMQP={}".format(args.USE_AMQP))


    # Initialize MQTT/AMQP client
    print("Using {} for webserver-messagebroker communication!".format("AMQP" if CONFIG_USE_AMQP else "MQTT"))
    if CONFIG_USE_AMQP:
        g_messaging_client = messaging_client(CONFIG_USE_AMQP, on_amqp_message)
        g_messaging_client.set_server(CONFIG_AMQP_HOST, CONFIG_AMQP_TLS_PORT)
    else:
        g_messaging_client = messaging_client(CONFIG_USE_AMQP, on_mqtt_message)
        g_messaging_client.set_server(CONFIG_MQTT_HOST, CONFIG_MQTT_TLS_PORT)
    g_messaging_client.set_user_pass(CONFIG_USERNAME, CONFIG_PASSWORD)
    g_messaging_client.set_tls(CONFIG_TLS_CA, CONFIG_TLS_CERT, CONFIG_TLS_PKEY)
    g_messaging_client.initialize()

    # Initialize certificate generator
    #g_certificate_generator = certificate_generator()

    # Initialize Database client
    #g_db_client = init_db_client()

    # Initialize HTTP server
    g_http_server = init_http_server()


