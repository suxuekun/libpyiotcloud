import ssl
import json
import time
import paho.mqtt.client as mqtt
from flask import Flask, request
from flask_json import FlaskJSON, JsonError, json_response, as_json
from certificate_generator import certificate_generator
#from pymongo import MongoClient



###################################################################################
# MQTT and HTTP configurations
###################################################################################

CONFIG_MQTT_USERNAME        = "guest"
CONFIG_MQTT_PASSWORD        = "guest"
CONFIG_MQTT_TLS_CA          = "cert/rootca.pem"
CONFIG_MQTT_TLS_CERT        = "cert/server_cert.pem"
CONFIG_MQTT_TLS_PKEY        = "cert/server_pkey.pem"
CONFIG_MQTT_SUBSCRIBE_TOPIC = "topic/#"
CONFIG_MQTT_HOST            = "localhost"
CONFIG_MQTT_PORT            = 8883

CONFIG_HTTP_HOST            = "localhost"
CONFIG_HTTP_PORT            = 443
CONFIG_HTTP_TLS_CA          = "cert/rootca.pem"
CONFIG_HTTP_TLS_CERT        = "cert/server_cert.pem"
CONFIG_HTTP_TLS_PKEY        = "cert/server_pkey.pem"



###################################################################################
# global variables
###################################################################################

g_certificate_generator = None
g_mqtt_client = None
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
    print('device_name={}'.format(device_name))

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



def generate_mqtt_publish_topic(data, api):
    customer_id = data['customer_id']
    device_name = data['device_name']
    topic = customer_id + "/" + device_name + "/" + api 
    return topic

def generate_mqtt_publish_payload(data):
    data.pop('customer_id')
    data.pop('device_name')
    payload = json.dumps(data)
    return payload

def generate_mqtt_subscribe_topic(topic):
    topic = "server/" + topic
    return topic


@g_http_server.route('/get_gpio')
def get_gpio():

    start_time = time.time()
    api = 'get_gpio'

    # parse HTTP request
    data = request.get_json()
    print("\r\nAPI: {} request={}".format(api, data))

    # send MQTT request
    topic = generate_mqtt_publish_topic(data, api)
    payload = generate_mqtt_publish_payload(data)
    publish_mqtt_packet(topic, payload)

    # recv MQTT response
    topic = generate_mqtt_subscribe_topic(topic) + "/" + str(int(data['number']))
    subscribe_mqtt_topic(topic, subscribe=True)
    data = receive_mqtt_topic(topic)
    subscribe_mqtt_topic(topic, subscribe=False)
    elapsed_time = time.time() - start_time
    print(elapsed_time)

    # return HTTP response
    if data is None:
        return api
    return data

@g_http_server.route('/set_gpio', methods=['POST'])
def set_gpio():

    start_time = time.time()
    api = 'set_gpio'

    # parse HTTP request
    data = request.get_json()
    print("\r\nAPI: {} request={}".format(api, data))

    # send MQTT request
    topic = generate_mqtt_publish_topic(data, api)
    payload = generate_mqtt_publish_payload(data)
    publish_mqtt_packet(topic, payload)

    # recv MQTT response
    topic = generate_mqtt_subscribe_topic(topic) + "/" + str(int(data['number']))
    subscribe_mqtt_topic(topic, subscribe=True)
    data = receive_mqtt_topic(topic)
    subscribe_mqtt_topic(topic, subscribe=False)
    elapsed_time = time.time() - start_time
    print(elapsed_time)

    # return HTTP response
    if data is None:
        return api
    return data



@g_http_server.route('/get_rtc')
def get_rtc():

    api = 'get_rtc'

    # parse HTTP request
    data = request.get_json()
    print("\r\nAPI: {} request={}".format(api, data))

    # send MQTT request
    topic = generate_mqtt_publish_topic(data, api)
    payload = generate_mqtt_publish_payload(data)
    publish_mqtt_packet(topic, payload)

    # recv MQTT response
    topic = generate_mqtt_subscribe_topic(topic)
    subscribe_mqtt_topic(topic, subscribe=True)
    data = receive_mqtt_topic(topic)
    subscribe_mqtt_topic(topic, subscribe=False)

    # return HTTP response
    if data is None:
        return api
    return data

@g_http_server.route('/set_rtc', methods=['POST'])
def set_rtc():

    api = 'set_rtc'

    # parse HTTP request
    data = request.get_json()
    print("\r\nAPI: {} request={}".format(api, data))

    # send MQTT request
    topic = generate_mqtt_publish_topic(data, api)
    payload = generate_mqtt_publish_payload(data)
    publish_mqtt_packet(topic, payload)

    # recv MQTT response
    topic = generate_mqtt_subscribe_topic(topic)
    subscribe_mqtt_topic(topic, subscribe=True)
    data = receive_mqtt_topic(topic)
    subscribe_mqtt_topic(topic, subscribe=False)

    # return HTTP response
    if data is None:
        return api
    return data



@g_http_server.route('/get_status')
def get_status():

    api = 'get_status'

    # parse HTTP request
    data = request.get_json()
    print("\r\nAPI: {} request={}".format(api, data))

    # send MQTT request
    topic = generate_mqtt_publish_topic(data, api)
    payload = generate_mqtt_publish_payload(data)
    publish_mqtt_packet(topic, payload)

    # recv MQTT response
    topic = generate_mqtt_subscribe_topic(topic)
    subscribe_mqtt_topic(topic, subscribe=True)
    data = receive_mqtt_topic(topic)
    subscribe_mqtt_topic(topic, subscribe=False)

    # return HTTP response
    if data is None:
        return api
    return data

@g_http_server.route('/set_status', methods=['POST'])
def set_status():

    api = 'set_status'

    # parse HTTP request
    data = request.get_json()
    print("\r\nAPI: {} request={}".format(api, data))

    # send MQTT request
    topic = generate_mqtt_publish_topic(data, api)
    payload = generate_mqtt_publish_payload(data)
    publish_mqtt_packet(topic, payload)

    # recv MQTT response
    topic = generate_mqtt_subscribe_topic(topic)
    subscribe_mqtt_topic(topic, subscribe=True)
    data = receive_mqtt_topic(topic)
    subscribe_mqtt_topic(topic, subscribe=False)

    # return HTTP response
    if data is None:
        return api
    return data



@g_http_server.route('/get_mac')
def get_mac():

    api = 'get_mac'

    # parse HTTP request
    data = request.get_json()
    print("\r\nAPI: {} request={}".format(api, data))

    # send MQTT request
    topic = generate_mqtt_publish_topic(data, api)
    payload = generate_mqtt_publish_payload(data)
    publish_mqtt_packet(topic, payload)

    # recv MQTT response
    topic = generate_mqtt_subscribe_topic(topic)
    subscribe_mqtt_topic(topic, subscribe=True)
    data = receive_mqtt_topic(topic)
    subscribe_mqtt_topic(topic, subscribe=False)

    # return HTTP response
    if data is None:
        return api
    return data

@g_http_server.route('/set_mac', methods=['POST'])
def set_mac():

    api = 'set_mac'

    # parse HTTP request
    data = request.get_json()
    print("\r\nAPI: {} request={}".format(api, data))

    # send MQTT request
    topic = generate_mqtt_publish_topic(data, api)
    payload = generate_mqtt_publish_payload(data)
    publish_mqtt_packet(topic, payload)

    # recv MQTT response
    topic = generate_mqtt_subscribe_topic(topic)
    subscribe_mqtt_topic(topic, subscribe=True)
    data = receive_mqtt_topic(topic)
    subscribe_mqtt_topic(topic, subscribe=False)

    # return HTTP response
    if data is None:
        return api
    return data


@g_http_server.route('/get_ip')
def get_ip():

    api = 'get_ip'

    # parse HTTP request
    data = request.get_json()
    print("\r\nAPI: {} request={}".format(api, data))

    # send MQTT request
    topic = generate_mqtt_publish_topic(data, api)
    payload = generate_mqtt_publish_payload(data)
    publish_mqtt_packet(topic, payload)

    # recv MQTT response
    topic = generate_mqtt_subscribe_topic(topic)
    subscribe_mqtt_topic(topic, subscribe=True)
    data = receive_mqtt_topic(topic)
    subscribe_mqtt_topic(topic, subscribe=False)

    # return HTTP response
    if data is None:
        return api
    return data

@g_http_server.route('/get_subnet')
def get_subnet():

    api = 'get_subnet'

    # parse HTTP request
    data = request.get_json()
    print("\r\nAPI: {} request={}".format(api, data))

    # send MQTT request
    topic = generate_mqtt_publish_topic(data, api)
    payload = generate_mqtt_publish_payload(data)
    publish_mqtt_packet(topic, payload)

    # recv MQTT response
    topic = generate_mqtt_subscribe_topic(topic)
    subscribe_mqtt_topic(topic, subscribe=True)
    data = receive_mqtt_topic(topic)
    subscribe_mqtt_topic(topic, subscribe=False)

    # return HTTP response
    if data is None:
        return api
    return data

@g_http_server.route('/get_gateway')
def get_gateway():

    api = 'get_gateway'

    # parse HTTP request
    data = request.get_json()
    print("\r\nAPI: {} request={}".format(api, data))

    # send MQTT request
    topic = generate_mqtt_publish_topic(data, api)
    payload = generate_mqtt_publish_payload(data)
    publish_mqtt_packet(topic, payload)

    # recv MQTT response
    topic = generate_mqtt_subscribe_topic(topic)
    subscribe_mqtt_topic(topic, subscribe=True)
    data = receive_mqtt_topic(topic)
    subscribe_mqtt_topic(topic, subscribe=False)

    # return HTTP response
    if data is None:
        return api
    return data



###################################################################################
# MQTT callback handlers
###################################################################################

def on_mqtt_connect(client, userdata, flags, rc):
    print("MQTT Connected with result code " + str(rc))
    client.subscribe(CONFIG_MQTT_SUBSCRIBE_TOPIC)

def on_mqtt_message(client, userdata, msg):
    index = msg.topic.find('server/')
    if index == 0:
        g_queue_dict[msg.topic] = msg.payload
        print("RCV: {}".format(g_queue_dict))

def publish_mqtt_packet(topic, payload):
    print("PUB: topic={} payload={}".format(topic, payload))
    if g_mqtt_client:
        g_mqtt_client.publish(topic, payload)

def subscribe_mqtt_topic(topic, subscribe=True):
    print("SUB: topic={}".format(topic))
    if g_mqtt_client:
        if subscribe:
            g_mqtt_client.subscribe(topic)
        else:
            g_mqtt_client.unsubscribe(topic)

def receive_mqtt_topic(topic):
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
# MQTT client initialization
###################################################################################

def init_mqtt_client():
    client = mqtt.Client()
    client.on_connect = on_mqtt_connect
    client.on_message = on_mqtt_message

    # Set MQTT credentials
    client.username_pw_set(CONFIG_MQTT_USERNAME, CONFIG_MQTT_PASSWORD)

    # Set TLS certificates
    client.tls_set(ca_certs = CONFIG_MQTT_TLS_CA,
        certfile    = CONFIG_MQTT_TLS_CERT,
        keyfile     = CONFIG_MQTT_TLS_PKEY,
        cert_reqs   = ssl.CERT_REQUIRED,
        tls_version = ssl.PROTOCOL_TLSv1_2,
        ciphers=None)

    # handle issue: 
    #   hostname doesn't match xxxx
    client.tls_insecure_set(True)

    # handle issues: 
    #   MQTT server is down OR 
    #   invalid MQTT crendentials OR 
    #   invalid TLS certificates
    try:
        client.connect(CONFIG_MQTT_HOST, CONFIG_MQTT_PORT)
        client.loop_start()
    except:
        client = None

    return client



###################################################################################
# HTTP server initialization
###################################################################################

def init_http_server():
    context = (CONFIG_MQTT_TLS_CERT, CONFIG_MQTT_TLS_PKEY)
    g_http_server.run(ssl_context = context,
        host     = CONFIG_HTTP_HOST, 
        port     = CONFIG_HTTP_PORT, 
        threaded = True, 
        debug    = True)
    return g_http_server


def init_db_client():
    client = MongoClient('localhost', 27017)
    return client



###################################################################################
# Main entry point
###################################################################################

if __name__ == '__main__':

    # Initialize certificate generator
    g_certificate_generator = certificate_generator()

    # Initialize Database client
    #g_db_client = init_db_client()


    # Initialize MQTT client
    g_mqtt_client = init_mqtt_client()
    if g_mqtt_client is None:
        print("Error: MQTT server is down!!!")

    # Initialize HTTP server
    g_http_server = init_http_server()


