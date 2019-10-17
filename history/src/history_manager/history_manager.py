from web_server_database import database_client
import json
import time
import argparse
import threading
import sys
import os
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from messaging_client import messaging_client



###################################################################################
# Use ECC or RSA certificates
CONFIG_USE_ECC = True if int(os.environ["CONFIG_USE_ECC"]) == 1 else False
# Enable to use AMQP for webserver-to-messagebroker communication
# Disable to use MQTT for webserver-to-messagebroker communication
CONFIG_USE_AMQP = False
###################################################################################



###################################################################################
# global variables
###################################################################################

g_messaging_client = None
g_history_client = None
g_gpio_values = {}


###################################################################################
# MQTT and AMQP default configurations
###################################################################################

CONFIG_DEVICE_ID            = "history_manager"

CONFIG_USERNAME             = None
CONFIG_PASSWORD             = None

if CONFIG_USE_ECC:
    CONFIG_TLS_CA           = "../cert_ecc/rootca.pem"
    CONFIG_TLS_CERT         = "../cert_ecc/history_manager_cert.pem"
    CONFIG_TLS_PKEY         = "../cert_ecc/history_manager_pkey.pem"
else:
    CONFIG_TLS_CA           = "../cert/rootca.pem"
    CONFIG_TLS_CERT         = "../cert/history_manager_cert.pem"
    CONFIG_TLS_PKEY         = "../cert/history_manager_pkey.pem"

CONFIG_HOST                 = "rabbitmq"
CONFIG_MQTT_TLS_PORT        = 8883
CONFIG_AMQP_TLS_PORT        = 5671

CONFIG_PREPEND_REPLY_TOPIC  = "server"
CONFIG_SEPARATOR            = '/'



###################################################################################
# MQTT/AMQP callback functions
###################################################################################


def add_history(deviceid, topic, payload, direction):

    # Write to database
    g_history_client.add_device_history(deviceid, topic, payload, direction)

    # Display database
    if True:
        histories = g_history_client.get_device_history(deviceid)
        for history in histories:
            #print(history)
            #print(history["deviceid"])
            print(history["topic"])
            print(history["payload"])
            print(history["direction"])
            print(history["timestamp"])
            print("")
        print(len(histories))
    else:
        histories = g_history_client.get_device_history(deviceid)
        print(len(histories))


def on_message(subtopic, subpayload):

    try:
        item = {}
        if subtopic.startswith("server"):
            arr_subtopic = subtopic.split("/", 2)
            add_history(arr_subtopic[1], arr_subtopic[2], subpayload.decode("utf-8"), "From")
        else:
            arr_subtopic = subtopic.split("/", 1)
            add_history(arr_subtopic[0], arr_subtopic[1], subpayload.decode("utf-8"), "To")
    except:
        print("exception")
        return


def on_mqtt_message(client, userdata, msg):

    #print("RCV: MQTT {} {}".format(msg.topic, msg.payload))
    on_message(msg.topic, msg.payload)


def on_amqp_message(ch, method, properties, body):

    #print("RCV: AMQP {} {}".format(method.routing_key, body))
    on_message(method.routing_key, body)



###################################################################################
# Main entry point
###################################################################################

def parse_arguments(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--USE_AMQP', required=False, default=1 if CONFIG_USE_AMQP else 0, help='Use AMQP instead of MQTT')
    parser.add_argument('--USE_DEVICE_ID', required=False, default=CONFIG_DEVICE_ID,    help='Device ID to use')
    parser.add_argument('--USE_DEVICE_CA',   required=False, default=CONFIG_TLS_CA,   help='Device CA certificate to use')
    parser.add_argument('--USE_DEVICE_CERT', required=False, default=CONFIG_TLS_CERT, help='Device certificate to use')
    parser.add_argument('--USE_DEVICE_PKEY', required=False, default=CONFIG_TLS_PKEY, help='Device private key to use')
    parser.add_argument('--USE_HOST',        required=False, default=CONFIG_HOST,     help='Host server to connect to')
    parser.add_argument('--USE_USERNAME',    required=False, default=CONFIG_USERNAME, help='Username to use in connection')
    parser.add_argument('--USE_PASSWORD',    required=False, default=CONFIG_PASSWORD, help='Password to use in connection')
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


    # Initialize MongoDB
    g_history_client = database_client()
    g_history_client.initialize()


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
    while True:
        try:
            result = g_messaging_client.initialize(timeout=5)
            if not result:
                print("Could not connect to message broker! ECC={}".format(CONFIG_USE_ECC))
            else:
                break
        except:
            print("Could not connect to message broker! exception!")


    # Subscribe to messages sent for this device
    time.sleep(1)
    subtopic = "#"
    g_messaging_client.subscribe(subtopic, subscribe=True, declare=True, consume_continuously=True)


    while g_messaging_client.is_connected():
        pass

    print("application exits!")
