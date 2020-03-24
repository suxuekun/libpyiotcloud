from registration_config import config as registration_config
from web_server_database import database_client
from datetime import datetime
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
CONFIG_DBHOST = registration_config.CONFIG_MONGODB_HOST
###################################################################################



###################################################################################
# global variables
###################################################################################

g_messaging_client = None
g_sensor_client = None
g_database_client = None



###################################################################################
# MQTT and AMQP default configurations
###################################################################################

CONFIG_DEVICE_ID            = "registration_manager"

CONFIG_USERNAME             = registration_config.CONFIG_MQTT_DEFAULT_USER
CONFIG_PASSWORD             = registration_config.CONFIG_MQTT_DEFAULT_PASS

if CONFIG_USE_ECC:
    CONFIG_TLS_CA           = "../cert_ecc/rootca.pem"
    CONFIG_TLS_CERT         = "../cert_ecc/registration_manager_cert.pem"
    CONFIG_TLS_PKEY         = "../cert_ecc/registration_manager_pkey.pem"
else:
    CONFIG_TLS_CA           = "../cert/rootca.pem"
    CONFIG_TLS_CERT         = "../cert/registration_manager_cert.pem"
    CONFIG_TLS_PKEY         = "../cert/registration_manager_pkey.pem"

CONFIG_HOST                 = "localhost"
CONFIG_MQTT_TLS_PORT        = 8883
CONFIG_AMQP_TLS_PORT        = 5671

CONFIG_PREPEND_REPLY_TOPIC  = "server"
CONFIG_SEPARATOR            = '/'

API_SET_REGISTRATION        = "set_registration"
#API_RECEIVE_CONFIGURATION   = "rcv_configuration"
#API_DELETE_CONFIGURATION    = "del_configuration"
#API_SET_CONFIGURATION       = "set_configuration"



###################################################################################
# MQTT/AMQP callback functions
###################################################################################


def print_json(json_object):
    json_formatted_str = json.dumps(json_object, indent=2)
    print(json_formatted_str)


def set_registration(database_client, deviceid, topic, payload):

    print("{} {}".format(topic, deviceid))

    # find if deviceid exists
    devicename = database_client.get_devicename(deviceid)
    if devicename is None:
        return

    payload = json.loads(payload)
    print_json(payload)

    for sensor in payload["sensors"]:
        # parse sensor
        peripheral = sensor["source"]
        sensor.pop("source")
        source = peripheral[:len(peripheral)-1]
        number = peripheral[len(peripheral)-1:]

        # add enabled and configured states
        sensor["enabled"] = 0
        sensor["configured"] = 0

        # generate sensorname
        sensorname = ""
        index = 1
        while True:
            sensorname = "{} {}".format(sensor["model"], index)
            item = database_client.check_sensor_by_deviceid(deviceid, sensorname)
            if item is None:
                break
            #print_json(item)
            if item["source"] == source and item["number"] == number:
                if item["manufacturer"] == sensor["manufacturer"] and item["model"] == sensor["model"]:
                    if item["class"] == sensor["class"] and item["type"] == sensor["type"]:
                        #if item["units"][0] == sensor["units"][0] and item["formats"][0] == sensor["formats"][0]:
                        if source == "i2c":
                            if item["address"] == sensor["address"]:
                                index = 0
                                print("Sensor already registered! {}".format(sensorname))
                                break
                        else:
                            index = 0
                            print("Sensor already registered! {}".format(sensorname))
                            break
            index += 1
        if index == 0:
            continue

        # register sensor
        print()
        print(sensorname)
        print(source)
        print(number)
        print_json(sensor)
        print()
        database_client.add_sensor_by_deviceid(deviceid, source, number, sensorname, sensor)

    print()


def on_message(subtopic, subpayload):

    #print(subtopic)
    #print(subpayload)

    arr_subtopic = subtopic.split(CONFIG_SEPARATOR, 2)
    if len(arr_subtopic) != 3:
        return

    deviceid = arr_subtopic[1]
    topic = arr_subtopic[2]
    payload = subpayload.decode("utf-8")

    if topic == API_SET_REGISTRATION:
        try:
            thr = threading.Thread(target = set_registration, args = (g_database_client, deviceid, topic, payload ))
            thr.start()
        except Exception as e:
            print("exception API_SET_REGISTRATION")
            print(e)
            return


def on_mqtt_message(client, userdata, msg):

    try:
        if registration_config.CONFIG_DEBUG:
            print("RCV: MQTT {} {}".format(msg.topic, msg.payload))
        on_message(msg.topic, msg.payload)
    except:
        return

def on_amqp_message(ch, method, properties, body):

    try:
        if registration_config.CONFIG_DEBUG:
            print("RCV: AMQP {} {}".format(method.routing_key, body))
        on_message(method.routing_key, body)
    except:
        return



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
    parser.add_argument('--USE_DBHOST',      required=False, default=CONFIG_DBHOST,   help='Host DB server to connect to')
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
    CONFIG_DBHOST      = args.USE_DBHOST
    CONFIG_USERNAME    = args.USE_USERNAME
    CONFIG_PASSWORD    = args.USE_PASSWORD
    print("")
    print("USE_AMQP={}".format(args.USE_AMQP))
    print("USE_DEVICE_ID={}".format(args.USE_DEVICE_ID))
    print("USE_DEVICE_CA={}".format(args.USE_DEVICE_CA))
    print("USE_DEVICE_CERT={}".format(args.USE_DEVICE_CERT))
    print("USE_DEVICE_PKEY={}".format(args.USE_DEVICE_PKEY))
    print("USE_HOST={}".format(args.USE_HOST))
    print("USE_DBHOST={}".format(args.USE_DBHOST))
    print("USE_USERNAME={}".format(args.USE_USERNAME))
    print("USE_PASSWORD={}".format(args.USE_PASSWORD))
    print("")


    # Initialize MongoDB
    g_database_client = database_client(host=CONFIG_DBHOST)
    g_database_client.initialize()


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
    subtopic = "{}{}+{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_SEPARATOR, API_SET_REGISTRATION)
    g_messaging_client.subscribe(subtopic, subscribe=True, declare=True, consume_continuously=True)


    while g_messaging_client.is_connected():
        time.sleep(3)
        pass

    print("application exits!")
