import ssl
import json
import time
import threading
import netifaces
import argparse
import sys
from messaging_client import messaging_client



###################################################################################
# Enable to use AMPQ for webserver-to-messagebroker communication
# Disable to use MQTT for webserver-to-messagebroker communication
CONFIG_USE_AMQP = True
###################################################################################



###################################################################################
# global variables
###################################################################################

g_messaging_client = None
g_mqtt_connect = False
g_gpio_values = {}


###################################################################################
# MQTT and AMPQ configurations
###################################################################################

CONFIG_CUSTOMER_ID          = "richmond_umagat@brtchip_com"
CONFIG_DEVICE_NAME          = "ft900device1"

CONFIG_USERNAME             = "guest"
CONFIG_PASSWORD             = "guest"
CONFIG_TLS_CA               = "cert/rootca.pem"
CONFIG_TLS_CERT             = "cert/ft900device1_cert.pem"
CONFIG_TLS_PKEY             = "cert/ft900device1_pkey.pem"

CONFIG_MQTT_HOST            = "localhost"
CONFIG_MQTT_TLS_PORT        = 8883
CONFIG_AMQP_HOST            = "localhost"
CONFIG_AMQP_TLS_PORT        = 5671

CONFIG_PREPEND_REPLY_TOPIC  = ""
CONFIG_QOS                  = 1
CONFIG_SEPARATOR            = '/'



###################################################################################
# API handling
###################################################################################

def handle_api(api, subtopic, subpayload):

    if api == "get_status":
        topic = "server" + CONFIG_SEPARATOR + subtopic
        payload = {}
        payload["status"] = "running"
        payload = json.dumps(payload)
        g_messaging_client.publish(topic, payload)

    elif api == "write_uart":
        topic = "server" + CONFIG_SEPARATOR + subtopic
        payload = {}
        subpayload = json.loads(subpayload)
        payload["data"] = subpayload["data"]
        payload = json.dumps(payload)
        g_messaging_client.publish(topic, payload)
        print(subpayload["data"])

    elif api == "get_gpio":
        topic = "server" + CONFIG_SEPARATOR + subtopic
        subpayload = json.loads(subpayload)

        try:
            value = g_gpio_values[str(subpayload["number"])]
        except:
            value = 0

        payload = {}
        payload["number"] = subpayload["number"]
        payload["value"] = value
        payload = json.dumps(payload)
        g_messaging_client.publish(topic, payload)

    elif api == "set_gpio":
        topic = "server" + CONFIG_SEPARATOR + subtopic
        subpayload = json.loads(subpayload)

        value = int(subpayload["value"])
        g_gpio_values[str(subpayload["number"])] = value

        payload = {}
        payload["number"] = subpayload["number"]
        payload["value"] = value
        payload = json.dumps(payload)
        g_messaging_client.publish(topic, payload)


    elif api == "get_rtc":
        topic = "server" + CONFIG_SEPARATOR + subtopic
        subpayload = json.loads(subpayload)

        value = int(time.time())

        payload = {}
        payload["value"] = value
        payload = json.dumps(payload)
        g_messaging_client.publish(topic, payload)

    elif api == "set_rtc":
        topic = "server" + CONFIG_SEPARATOR + subtopic
        subpayload = json.loads(subpayload)

        value = subpayload["value"]

        payload = {}
        payload["value"] = value
        payload = json.dumps(payload)
        g_messaging_client.publish(topic, payload)


    elif api == "get_mac":
        topic = "server" + CONFIG_SEPARATOR + subtopic
        subpayload = json.loads(subpayload)

        gws = netifaces.gateways()
        ifw = gws['default'][netifaces.AF_INET][1]
        addrs = netifaces.ifaddresses(ifw)[netifaces.AF_LINK][0]
        value = addrs['addr']

        payload = {}
        payload["value"] = value
        payload = json.dumps(payload)
        g_messaging_client.publish(topic, payload)

    elif api == "get_ip":
        topic = "server" + CONFIG_SEPARATOR + subtopic
        subpayload = json.loads(subpayload)

        gws = netifaces.gateways()
        ifw = gws['default'][netifaces.AF_INET][1]
        addrs = netifaces.ifaddresses(ifw)[netifaces.AF_INET][0]
        value = addrs['addr']

        payload = {}
        payload["value"] = value
        payload = json.dumps(payload)
        g_messaging_client.publish(topic, payload)

    elif api == "get_subnet":
        topic = "server" + CONFIG_SEPARATOR + subtopic
        subpayload = json.loads(subpayload)

        gws = netifaces.gateways()
        ifw = gws['default'][netifaces.AF_INET][1]
        addrs = netifaces.ifaddresses(ifw)[netifaces.AF_INET][0]
        value = addrs['netmask']

        payload = {}
        payload["value"] = value
        payload = json.dumps(payload)
        g_messaging_client.publish(topic, payload)

    elif api == "get_gateway":
        topic = "server" + CONFIG_SEPARATOR + subtopic
        subpayload = json.loads(subpayload)

        gws = netifaces.gateways()
        value = gws['default'][netifaces.AF_INET][0]

        payload = {}
        payload["value"] = value
        payload = json.dumps(payload)
        g_messaging_client.publish(topic, payload)


    elif api == "set_status":
        topic = "server" + CONFIG_SEPARATOR + subtopic
        subpayload = json.loads(subpayload)

        status = "restarting"

        payload = {}
        payload["status"] = status
        payload = json.dumps(payload)
        g_messaging_client.publish(topic, payload)



###################################################################################
# MQTT/AMQP callback functions
###################################################################################

def on_mqtt_message(client, userdata, msg):
    #print("MQTT Recv {}".format(userdata))
    print("MQTT Recv {}".format(msg.topic))
    #print("MQTT Recv {}".format(msg.payload))

    expected_topic = "{}{}{}{}".format(CONFIG_CUSTOMER_ID, CONFIG_SEPARATOR, CONFIG_DEVICE_NAME, CONFIG_SEPARATOR)
    expected_topic_len = len(expected_topic)
    topic = msg.topic
    if topic[:expected_topic_len] != expected_topic:
        return

    api = topic[expected_topic_len:]
    #print(api)
    handle_api(api, topic, msg.payload)

def on_amqp_message(ch, method, properties, body):
    #print("RCV: {} {}".format(method.routing_key, body))

    expected_topic = "{}{}{}{}".format(CONFIG_CUSTOMER_ID, CONFIG_SEPARATOR, CONFIG_DEVICE_NAME, CONFIG_SEPARATOR)
    expected_topic_len = len(expected_topic)
    topic = method.routing_key
    if topic[:expected_topic_len] != expected_topic:
        print("exit")
        return

    api = topic[expected_topic_len:]
    print(api)
    handle_api(api, topic, body)



###################################################################################
# Main entry point
###################################################################################

def parse_arguments(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--USE_AMQP', required=False, default=1 if CONFIG_USE_AMQP else 0, help='Use AMQP instead of MQTT')
    parser.add_argument('--USE_DEVICE_NAME', required=False, default=CONFIG_DEVICE_NAME,   help='Device name to use')
    parser.add_argument('--USE_DEVICE_CERT', required=False, default=CONFIG_TLS_CERT,      help='Device certificate to use')
    parser.add_argument('--USE_DEVICE_PKEY', required=False, default=CONFIG_TLS_PKEY,      help='Device private key to use')
    return parser.parse_args(argv)


if __name__ == '__main__':

    args = parse_arguments(sys.argv[1:])
    CONFIG_USE_AMQP = True if int((args.USE_AMQP))==1 else False
    CONFIG_SEPARATOR = "." if int((args.USE_AMQP))==1 else "/"
    CONFIG_DEVICE_NAME = args.USE_DEVICE_NAME
    CONFIG_TLS_CERT = args.USE_DEVICE_CERT
    CONFIG_TLS_PKEY = args.USE_DEVICE_PKEY
    print("USE_AMQP={}".format(args.USE_AMQP))
    print("USE_DEVICE_NAME={}".format(args.USE_DEVICE_NAME))
    print("USE_DEVICE_CERT={}".format(args.USE_DEVICE_CERT))
    print("USE_DEVICE_PKEY={}".format(args.USE_DEVICE_PKEY))


    # Initialize MQTT/AMQP client
    print("Using {} for device-messagebroker communication!".format("AMQP" if CONFIG_USE_AMQP else "MQTT"))
    if CONFIG_USE_AMQP:
        g_messaging_client = messaging_client(CONFIG_USE_AMQP, on_amqp_message, device_name=CONFIG_DEVICE_NAME)
        g_messaging_client.set_server(CONFIG_AMQP_HOST, CONFIG_AMQP_TLS_PORT)
    else:
        g_messaging_client = messaging_client(CONFIG_USE_AMQP, on_mqtt_message, device_name=CONFIG_DEVICE_NAME)
        g_messaging_client.set_server(CONFIG_MQTT_HOST, CONFIG_MQTT_TLS_PORT)
    g_messaging_client.set_user_pass(CONFIG_USERNAME, CONFIG_PASSWORD)
    g_messaging_client.set_tls(CONFIG_TLS_CA, CONFIG_TLS_CERT, CONFIG_TLS_PKEY)
    g_messaging_client.initialize()


    time.sleep(1)
    subtopic = "{}{}{}{}#".format(CONFIG_CUSTOMER_ID, CONFIG_SEPARATOR, CONFIG_DEVICE_NAME, CONFIG_SEPARATOR)
    #print(subtopic)
    g_messaging_client.subscribe(subtopic, subscribe=True, declare=True, consume_continuously=True)

    while True:
        pass

