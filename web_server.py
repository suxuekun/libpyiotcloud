import ssl
import json
import time
import threading
from flask import Flask, request
from flask_json import FlaskJSON, JsonError, json_response, as_json
from certificate_generator import certificate_generator
#from pymongo import MongoClient



CONFIG_USE_AMPQ = True
if CONFIG_USE_AMPQ:
    import pika
else:
    import paho.mqtt.client as mqtt



###################################################################################
# MQTT, HTTP and AMPQ configurations
###################################################################################

CONFIG_MQTT_USERNAME        = "guest"
CONFIG_MQTT_PASSWORD        = "guest"
CONFIG_MQTT_TLS_CA          = "cert/rootca.pem"
CONFIG_MQTT_TLS_CERT        = "cert/server_cert.pem"
CONFIG_MQTT_TLS_PKEY        = "cert/server_pkey.pem"
CONFIG_MQTT_HOST            = "localhost"
CONFIG_MQTT_TLS_PORT        = 8883

CONFIG_HTTP_HOST            = "localhost"
CONFIG_HTTP_PORT            = 443
CONFIG_HTTP_TLS_CA          = "cert/rootca.pem"
CONFIG_HTTP_TLS_CERT        = "cert/server_cert.pem"
CONFIG_HTTP_TLS_PKEY        = "cert/server_pkey.pem"

CONFIG_AMPQ_TLS_CA          = "cert/rootca.pem"
CONFIG_AMPQ_TLS_CERT        = "cert/server_cert.pem"
CONFIG_AMPQ_TLS_PKEY        = "cert/server_pkey.pem"
CONFIG_AMPQ_HOST            = "localhost"
CONFIG_AMPQ_TLS_PORT        = 5671
CONFIG_AMPQ_PORT            = 5672

CONFIG_PREPEND_REPLY_TOPIC  = "server"
CONFIG_QOS                  = 1



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



def generate_messaging_publish_topic(data, api):
    customer_id = data['customer_id']
    device_name = data['device_name']
    if CONFIG_USE_AMPQ:
        topic = customer_id + "." + device_name + "." + api 
    else:
        topic = customer_id + "/" + device_name + "/" + api 
    return topic

def generate_messaging_publish_payload(data):
    data.pop('customer_id')
    data.pop('device_name')
    payload = json.dumps(data)
    return payload

def generate_messaging_subscribe_topic(topic):
    if CONFIG_USE_AMPQ:
        topic = CONFIG_PREPEND_REPLY_TOPIC + "." + topic
    else:
        topic = CONFIG_PREPEND_REPLY_TOPIC + "/" + topic
    return topic

def process_request(api):
    # parse HTTP request
    data = request.get_json()
    print("\r\nAPI: {} request={}".format(api, data))

    # construct publish/subscribe topics and payloads
    pubtopic = generate_messaging_publish_topic(data, api)
    payload = generate_messaging_publish_payload(data)
    subtopic = generate_messaging_subscribe_topic(pubtopic)

    # subscribe for response
    subscribe_messaging_topic(subtopic, subscribe=True)

    # publish request
    publish_messaging_packet(pubtopic, payload)

    # receive response
    response = receive_messaging_topic(subtopic)
    subscribe_messaging_topic(subtopic, subscribe=False)

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



###################################################################################
# MQTT callback handlers
###################################################################################

def on_mqtt_connect(client, userdata, flags, rc):
    print("MQTT Connected with result code " + str(rc))

def on_mqtt_message(client, userdata, msg):
    if CONFIG_PREPEND_REPLY_TOPIC == '':
        g_queue_dict[msg.topic] = msg.payload
        print("RCV: {}".format(g_queue_dict))
    else:
        index = msg.topic.find(CONFIG_PREPEND_REPLY_TOPIC)
        if index == 0:
            g_queue_dict[msg.topic] = msg.payload
            print("RCV: {}".format(g_queue_dict))

def publish_mqtt_packet(topic, payload):
    print("PUB: topic={} payload={}".format(topic, payload))
    if g_messaging_client:
        g_messaging_client.publish(topic, payload, qos=CONFIG_QOS)

def subscribe_mqtt_topic(topic, subscribe=True):
    print("SUB: topic={}".format(topic))
    if g_messaging_client:
        if subscribe:
            g_messaging_client.subscribe(topic, qos=CONFIG_QOS)
        else:
            g_messaging_client.unsubscribe(topic)

def on_ampq_message(ch, method, properties, body):
    #print("RCV: {} {}".format(method.routing_key, body))
    g_queue_dict[method.routing_key] = body
    print("RCV: {}".format(g_queue_dict))
    g_messaging_client.stop_consuming()

def publish_ampq_packet(topic, payload):
    print("PUB: topic={} payload={}".format(topic, payload))
    if g_messaging_client:
        g_messaging_client.basic_publish(exchange='amq.topic', routing_key=topic, body=payload.encode("utf-8"))

def subscribe_ampq_thread(client):
    while True:
        try:
            #print("start consuming")
            client.start_consuming()
            #print("end consuming")
            break
        # Don't recover if connection was closed by broker
        except pika.exceptions.ConnectionClosedByBroker:
            print("ConnectionClosedByBroker")
            time.sleep(1)
            continue
        # Don't recover on client errors
        except pika.exceptions.AMQPChannelError:
            print("AMQPChannelError")
            time.sleep(1)
            continue
        # Recover on all other connection errors
        except pika.exceptions.AMQPConnectionError:
            print("AMQPConnectionError")
            time.sleep(1)
            continue

def subscribe_ampq_topic(topic, subscribe=True):
    print("SUB: topic={}".format(topic))
    if g_messaging_client:
        if subscribe:
            if CONFIG_PREPEND_REPLY_TOPIC == '':
                index = 0
            else:
                index = len(CONFIG_PREPEND_REPLY_TOPIC)+1
            index += topic[index:].index('.')
            index2 = index + 1 + topic[index+1:].index('.')
            device_name = topic[index+1:index2]
            myqueue = 'mqtt-subscription-{}qos{}'.format(device_name, CONFIG_QOS)
            g_messaging_client.queue_bind(queue=myqueue, exchange='amq.topic', routing_key=topic)
            #print("SUB: queue={}".format(myqueue))
            #print("SUB: topic={}".format(topic))

            g_messaging_client.basic_consume(queue=myqueue, on_message_callback=on_ampq_message)
            x = threading.Thread(target=subscribe_ampq_thread, args=(g_messaging_client,))
            x.start()

def publish_messaging_packet(topic, payload):
    if CONFIG_USE_AMPQ:
       publish_ampq_packet(topic, payload)
    else:
       publish_mqtt_packet(topic, payload)

def subscribe_messaging_topic(topic, subscribe=True):
    if CONFIG_USE_AMPQ:
       subscribe_ampq_topic(topic, subscribe=subscribe)
    else:
       subscribe_mqtt_topic(topic, subscribe=subscribe)

def receive_messaging_topic(topic):
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
# Messaging client initialization
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
        client.connect(CONFIG_MQTT_HOST, CONFIG_MQTT_TLS_PORT)
        client.loop_start()
    except:
        client = None

    return client

def init_ampq_client():

    use_tls = True

    # Set TLS certificates and access credentials
    credentials = pika.PlainCredentials('guest', 'guest')
    ssl_options = None
    if use_tls:
        context = ssl._create_unverified_context()
        #context = ssl.create_default_context(cafile=CONFIG_AMPQ_TLS_CA)
        #context.load_cert_chain(CONFIG_AMPQ_TLS_CERT, CONFIG_AMPQ_TLS_PKEY)
        ssl_options = pika.SSLOptions(context) 
        parameters = pika.ConnectionParameters(
            CONFIG_AMPQ_HOST, 
            CONFIG_AMPQ_TLS_PORT, 
            credentials=credentials, 
            ssl_options=ssl_options)
    else:
        parameters = pika.ConnectionParameters(
            CONFIG_AMPQ_HOST, 
            CONFIG_AMPQ_PORT, 
            credentials=credentials, 
            ssl_options=ssl_options)

    # Connect to AMPQ server
    connection = pika.BlockingConnection(parameters)
    client = connection.channel()

    return client

def init_messaging_client():
    if CONFIG_USE_AMPQ:
       client = init_ampq_client()
       print("Using AMPQ for webserver-messagebroker communication!")
    else:
       client = init_mqtt_client()
       print("Using MQTT for webserver-messagebroker communication!")
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


    # Initialize MQTT/AMPQ client
    g_messaging_client = init_messaging_client()
    if g_messaging_client is None:
        print("Error: {} server is down!!!".format("AMPQ" if CONFIG_USE_AMPQ else "MQTT"))

    # Initialize HTTP server
    g_http_server = init_http_server()


