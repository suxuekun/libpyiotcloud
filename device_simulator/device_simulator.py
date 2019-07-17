import json
import time
import netifaces
import argparse
import sys
import os
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from messaging_client import messaging_client # common module from parent directory



###################################################################################
# Enable to use AMQP for webserver-to-messagebroker communication
# Disable to use MQTT for webserver-to-messagebroker communication
CONFIG_USE_AMQP = True
###################################################################################



###################################################################################
# global variables
###################################################################################

g_messaging_client = None
g_gpio_values = {}


###################################################################################
# MQTT and AMQP default configurations
###################################################################################

CONFIG_DEVICE_ID            = ""

CONFIG_USERNAME             = None
CONFIG_PASSWORD             = None
CONFIG_TLS_CA               = "../cert/rootca.pem"
CONFIG_TLS_CERT             = "../cert/ft900device1_cert.pem"
CONFIG_TLS_PKEY             = "../cert/ft900device1_pkey.pem"

CONFIG_HOST                 = "localhost"
CONFIG_MQTT_TLS_PORT        = 8883
CONFIG_AMQP_TLS_PORT        = 5671

CONFIG_PREPEND_REPLY_TOPIC  = "server"
CONFIG_SEPARATOR            = '/'



###################################################################################
# API handling
###################################################################################

def publish(topic, payload):
    payload = json.dumps(payload)
    g_messaging_client.publish(topic, payload)

def generate_pubtopic(subtopic):
    return CONFIG_PREPEND_REPLY_TOPIC + CONFIG_SEPARATOR + subtopic

def handle_api(api, subtopic, subpayload):

    if api == "get_status":
        topic = generate_pubtopic(subtopic)
        payload = {}
        payload["value"] = "running"
        publish(topic, payload)

    elif api == "write_uart":
        topic = generate_pubtopic(subtopic)
        payload = {}
        subpayload = json.loads(subpayload)
        payload["value"] = subpayload["value"]
        publish(topic, payload)
        print(subpayload["value"])

    elif api == "get_gpio":
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        try:
            value = g_gpio_values[str(subpayload["number"])]
        except:
            value = 0

        payload = {}
        payload["number"] = subpayload["number"]
        payload["value"] = value
        publish(topic, payload)

    elif api == "set_gpio":
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        value = int(subpayload["value"])
        g_gpio_values[str(subpayload["number"])] = value

        payload = {}
        payload["number"] = subpayload["number"]
        payload["value"] = value
        publish(topic, payload)


    elif api == "get_rtc":
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        value = int(time.time())

        payload = {}
        payload["value"] = value
        publish(topic, payload)

    elif api == "set_rtc":
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        value = subpayload["value"]

        payload = {}
        payload["value"] = value
        publish(topic, payload)


    elif api == "get_mac":
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        gws = netifaces.gateways()
        ifw = gws['default'][netifaces.AF_INET][1]
        addrs = netifaces.ifaddresses(ifw)[netifaces.AF_LINK][0]
        value = addrs['addr']

        payload = {}
        payload["value"] = value
        publish(topic, payload)

    elif api == "get_ip":
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        gws = netifaces.gateways()
        ifw = gws['default'][netifaces.AF_INET][1]
        addrs = netifaces.ifaddresses(ifw)[netifaces.AF_INET][0]
        value = addrs['addr']

        payload = {}
        payload["value"] = value
        publish(topic, payload)

    elif api == "get_subnet":
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        gws = netifaces.gateways()
        ifw = gws['default'][netifaces.AF_INET][1]
        addrs = netifaces.ifaddresses(ifw)[netifaces.AF_INET][0]
        value = addrs['netmask']

        payload = {}
        payload["value"] = value
        publish(topic, payload)

    elif api == "get_gateway":
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        gws = netifaces.gateways()
        value = gws['default'][netifaces.AF_INET][0]

        payload = {}
        payload["value"] = value
        publish(topic, payload)


    elif api == "set_status":
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        status = "restarting"

        payload = {}
        payload["value"] = status
        publish(topic, payload)


    elif api == "trigger_notification":
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        publish(topic, subpayload)



###################################################################################
# MQTT/AMQP callback functions
###################################################################################

def on_message(subtopic, subpayload):

    expected_topic = "{}{}".format(CONFIG_DEVICE_ID, CONFIG_SEPARATOR)
    expected_topic_len = len(expected_topic)

    if subtopic[:expected_topic_len] != expected_topic:
        return

    api = subtopic[expected_topic_len:]
    #print(api)
    handle_api(api, subtopic, subpayload)


def on_mqtt_message(client, userdata, msg):

    print("RCV: MQTT {} {}".format(msg.topic, msg.payload))
    on_message(msg.topic, msg.payload)

  
def on_amqp_message(ch, method, properties, body):

    print("RCV: AMQP {} {}".format(method.routing_key, body))
    on_message(method.routing_key, body)



###################################################################################
# Main entry point
###################################################################################

def parse_arguments(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--USE_AMQP',        required=False, default=1 if CONFIG_USE_AMQP else 0, help='Use AMQP instead of MQTT')
    parser.add_argument('--USE_DEVICE_ID',   required=False, default=CONFIG_DEVICE_ID, help='Device ID to use')
    parser.add_argument('--USE_DEVICE_CA',   required=False, default=CONFIG_TLS_CA,    help='Device CA certificate to use')
    parser.add_argument('--USE_DEVICE_CERT', required=False, default=CONFIG_TLS_CERT,  help='Device certificate to use')
    parser.add_argument('--USE_DEVICE_PKEY', required=False, default=CONFIG_TLS_PKEY,  help='Device private key to use')
    parser.add_argument('--USE_HOST',        required=False, default=CONFIG_HOST,      help='Host server to connect to')
    parser.add_argument('--USE_USERNAME',    required=False, default=CONFIG_USERNAME,  help='Username to use in connection')
    parser.add_argument('--USE_PASSWORD',    required=False, default=CONFIG_PASSWORD,  help='Password to use in connection')
    return parser.parse_args(argv)


if __name__ == '__main__':

    args = parse_arguments(sys.argv[1:])
    CONFIG_USE_AMQP    = True if int((args.USE_AMQP))==1 else False
    CONFIG_SEPARATOR   = "." if int((args.USE_AMQP))==1 else "/"
    CONFIG_DEVICE_ID   = args.USE_DEVICE_ID
    CONFIG_TLS_CA      = args.USE_DEVICE_CA
    CONFIG_TLS_CERT    = args.USE_DEVICE_CERT
    CONFIG_TLS_PKEY    = args.USE_DEVICE_PKEY
    CONFIG_HOST        = args.USE_HOST
    CONFIG_USERNAME    = args.USE_USERNAME
    CONFIG_PASSWORD    = args.USE_PASSWORD
    print("")
    print("USE_AMQP={}".format(args.USE_AMQP))
    print("USE_DEVICE_ID={}".format(args.USE_DEVICE_ID))
    print("USE_DEVICE_CA={}".format(args.USE_DEVICE_CA))
    print("USE_DEVICE_CERT={}".format(args.USE_DEVICE_CERT))
    print("USE_DEVICE_PKEY={}".format(args.USE_DEVICE_PKEY))
    print("USE_HOST={}".format(args.USE_HOST))
    print("USE_USERNAME={}".format(args.USE_USERNAME))
    print("USE_PASSWORD={}".format(args.USE_PASSWORD))
    print("")


    # Initialize MQTT/AMQP client
    print("Using {} for device-messagebroker communication!".format("AMQP" if CONFIG_USE_AMQP else "MQTT"))
    if CONFIG_USE_AMQP:
        g_messaging_client = messaging_client(CONFIG_USE_AMQP, on_amqp_message, device_id=CONFIG_DEVICE_ID)
        g_messaging_client.set_server(CONFIG_HOST, CONFIG_AMQP_TLS_PORT)
    else:
        g_messaging_client = messaging_client(CONFIG_USE_AMQP, on_mqtt_message, device_id=CONFIG_DEVICE_ID)
        g_messaging_client.set_server(CONFIG_HOST, CONFIG_MQTT_TLS_PORT)
    if CONFIG_USERNAME and CONFIG_PASSWORD:
        g_messaging_client.set_user_pass(CONFIG_USERNAME, CONFIG_PASSWORD)
    g_messaging_client.set_tls(CONFIG_TLS_CA, CONFIG_TLS_CERT, CONFIG_TLS_PKEY)
    try:
        g_messaging_client.initialize()
    except:
        print("Could not connect to message broker")


    # Subscribe to messages sent for this device
    time.sleep(1)
    subtopic = "{}{}#".format(CONFIG_DEVICE_ID, CONFIG_SEPARATOR)
    print(subtopic)
    g_messaging_client.subscribe(subtopic, subscribe=True, declare=True, consume_continuously=True)


    while g_messaging_client.is_connected():
        pass

    print("application exits!")
