from configuration_config import config as configuration_config
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
CONFIG_DBHOST = configuration_config.CONFIG_MONGODB_HOST
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

CONFIG_DEVICE_ID            = "configuration_manager"

CONFIG_USERNAME             = configuration_config.CONFIG_MQTT_DEFAULT_USER
CONFIG_PASSWORD             = configuration_config.CONFIG_MQTT_DEFAULT_PASS

if CONFIG_USE_ECC:
    CONFIG_TLS_CA           = "../cert_ecc/rootca.pem"
    CONFIG_TLS_CERT         = "../cert_ecc/configuration_manager_cert.pem"
    CONFIG_TLS_PKEY         = "../cert_ecc/configuration_manager_pkey.pem"
else:
    CONFIG_TLS_CA           = "../cert/rootca.pem"
    CONFIG_TLS_CERT         = "../cert/configuration_manager_cert.pem"
    CONFIG_TLS_PKEY         = "../cert/configuration_manager_pkey.pem"

CONFIG_HOST                 = "localhost"
CONFIG_MQTT_TLS_PORT        = 8883
CONFIG_AMQP_TLS_PORT        = 5671

CONFIG_PREPEND_REPLY_TOPIC  = "server"
CONFIG_SEPARATOR            = '/'

API_RECEIVE_CONFIGURATION   = "rcv_configuration"
API_REQUEST_CONFIGURATION   = "req_configuration"
API_DELETE_CONFIGURATION    = "del_configuration"
API_SET_CONFIGURATION       = "set_configuration"



###################################################################################
# MQTT/AMQP callback functions
###################################################################################


def print_json(json_object):
    json_formatted_str = json.dumps(json_object, indent=2)
    print(json_formatted_str)


def get_configuration(database_client, deviceid, topic, payload):

    print("{} {}".format(topic, deviceid))

    # find if deviceid exists
    devicename = database_client.get_devicename(deviceid)
    if devicename is None:
        # if no entry found, just send an empty json
        new_payload = {}
        new_payload = json.dumps(new_payload)
        g_messaging_client.publish(new_topic, new_payload, debug=False) # NOTE: enable to DEBUG
        return

    # set topic and payload template for the response
    new_topic = "{}{}{}".format(deviceid, CONFIG_SEPARATOR, API_RECEIVE_CONFIGURATION)
    new_payload = {
        "uart"   : [{}],
        "gpio"   : [{}, {}, {}, {}],
        "i2c"    : [[], [], [], []],
        "adc"    : [{},{}],
        "1wire"  : [{}],
        "tprobe" : [{}],
    }

    # read configurations from the database
    configurations = database_client.get_all_device_peripheral_configuration(deviceid)
    if len(configurations) == 0:
        # if no entry found, just send an empty json
        new_payload = {}
        new_payload = json.dumps(new_payload)
        g_messaging_client.publish(new_topic, new_payload, debug=False) # NOTE: enable to DEBUG
        return
    #print_json(configurations)

    # set all counters to 0
    count_uart = 0
    count_gpio = 0
    count_i2c = 0
    count_adc = 0
    count_1wire = 0
    count_tprobe = 0

    # add configuration to the payload response
    for configuration in configurations:
        number = configuration["number"] - 1
        source = configuration["source"]
        configuration.pop("source")
        configuration.pop("number")
        if source == "i2c":
            new_payload[source][number].append(configuration)
            count_i2c += 1
        else:
            new_payload[source][number] = configuration
            if source == "uart":
                count_uart += 1
            elif source == "gpio":
                count_gpio += 1
            elif source == "adc":
                count_adc += 1
            elif source == "1wire":
                count_1wire += 1
            elif source == "tprobe":
                count_tprobe += 1

    # if GET_ALL_PERIPHERAL_CONFIGURATION,
    #   only peripherals with configured sensors will be included
    #   peripherals with no configured sensors will NOT be included to reduce size
    # if GET_SPECIFIED_PERIPHERAL_CONFIGURATION,
    #   specify the peripherals using "peripheral" list parameter (ex. "peripherals": ["i2c", "adc"])
    #   only specified peripherals with configured sensors will be included
    #   specified peripherals with no configured sensors will NOT be included to reduce size
    payload = json.loads(payload)
    if payload.get("peripherals"):
        # peripherals specified
        # remove if not specified
        # include if have data
        if "uart" not in payload["peripherals"]:
            new_payload.pop("uart")
        else:
            # include if have data
            if count_uart == 0:
                new_payload.pop("uart")

        if "gpio" not in payload["peripherals"]:
            new_payload.pop("gpio")
        else:
            # include if have data
            if count_gpio == 0:
                new_payload.pop("gpio")

        if "i2c" not in payload["peripherals"]:
            new_payload.pop("i2c")
        else:
            # include if have data
            if count_i2c == 0:
                new_payload.pop("i2c")

        if "adc" not in payload["peripherals"]:
            new_payload.pop("adc")
        else:
            # include if have data
            if count_adc == 0:
                new_payload.pop("adc")

        if "1wire" not in payload["peripherals"]:
            new_payload.pop("1wire")
        else:
            # include if have data
            if count_1wire == 0:
                new_payload.pop("1wire")

        if "tprobe" not in payload["peripherals"]:
            new_payload.pop("tprobe")
        else:
            # include if have data
            if count_tprobe == 0:
                new_payload.pop("tprobe")
    else:
        # no peripherals specified
        # include all if have data
        if count_uart == 0:
            new_payload.pop("uart")
        if count_gpio == 0:
            new_payload.pop("gpio")
        if count_i2c == 0:
            new_payload.pop("i2c")
        if count_adc == 0:
            new_payload.pop("adc")
        if count_1wire == 0:
            new_payload.pop("1wire")
        if count_tprobe == 0:
            new_payload.pop("tprobe")

    # publish packet response to device
    #print_json(new_payload)
    new_payload = json.dumps(new_payload)
    g_messaging_client.publish(new_topic, new_payload, debug=False) # NOTE: enable to DEBUG


def del_configuration(database_client, deviceid, topic, payload):

    print("{} {}".format(topic, deviceid))

    # find if deviceid exists
    devicename = database_client.get_devicename(deviceid)
    if devicename is None:
        return

    payload = json.loads(payload)
    if payload.get("peripherals"):
        # peripherals specified
        # delete configurations for specified peripheral
        for peripheral in payload["peripherals"]:
            database_client.delete_device_peripheral_configuration(deviceid, peripheral)
    else:
        # no peripherals specified
        # delete all peripheral configurations
        database_client.delete_all_device_peripheral_configuration(deviceid)


def set_configuration(database_client, deviceid, topic, payload):

    print("{} {}".format(topic, deviceid))

    payload = json.loads(payload)

    # find if deviceid exists
    devicename = database_client.get_devicename(deviceid)
    if devicename is None:
        return

    # process UART configuration
    source = "uart"
    if payload.get(source):
        for x in range(len(payload[source])):
            print(payload[source][x])

            address = None
            classid = None
            subclassid = None

            enabled = 0
            if payload[source][x].get("enabled"):
                enabled = payload[source][x]["enabled"]

            properties = None
            if payload[source][x].get("attributes"):
                properties = payload[source][x]["attributes"]

            database_client.update_device_peripheral_configuration_by_deviceid(deviceid, source, x+1, address, classid, subclassid, enabled, properties)

    # process GPIO configuration
    source = "gpio"
    if payload.get(source):
        for x in range(len(payload[source])):
            print(payload[source][x])

            address = None
            classid = None
            subclassid = None

            enabled = 0
            if payload[source][x].get("enabled"):
                enabled = payload[source][x]["enabled"]

            properties = None
            if payload[source][x].get("attributes"):
                properties = payload[source][x]["attributes"]
            else:
                continue

            database_client.update_device_peripheral_configuration_by_deviceid(deviceid, source, x+1, address, classid, subclassid, enabled, properties)

    # process I2C device configuration
    source = "i2c"
    if payload.get(source):
        for x in range(len(payload[source])):
            for y in range(len(payload[source][x])):
                print(payload[source][x][y])

                address = None
                if payload[source][x][y].get("address"):
                    address = payload[source][x][y]["address"]

                classid = None
                if payload[source][x][y].get("class"):
                    classid = payload[source][x][y]["class"]

                subclassid = None
                if payload[source][x][y].get("subclass"):
                    subclassid = payload[source][x][y]["subclass"]

                enabled = 0
                if payload[source][x][y].get("enabled"):
                    enabled = payload[source][x][y]["enabled"]

                properties = None
                if payload[source][x][y].get("attributes"):
                    properties = payload[source][x][y]["attributes"]
                else:
                    continue

                database_client.update_device_peripheral_configuration_by_deviceid(deviceid, source, x+1, address, classid, subclassid, enabled, properties)

    # process ADC device configuration
    source = "adc"
    if payload.get(source):
        for x in range(len(payload[source])):
            print(payload[source][x])

            address = None
            classid = None
            if payload[source][x].get("class"):
                classid = payload[source][x]["class"]

            subclassid = None
            if payload[source][x].get("subclass"):
                subclassid = payload[source][x]["subclass"]

            enabled = 0
            if payload[source][x].get("enabled"):
                enabled = payload[source][x]["enabled"]

            properties = None
            if payload[source][x].get("attributes"):
                properties = payload[source][x]["attributes"]
            else:
                continue

            database_client.update_device_peripheral_configuration_by_deviceid(deviceid, source, x+1, address, classid, subclassid, enabled, properties)

    # process TPROBE device configuration
    source = "tprobe"
    if payload.get(source):
        for x in range(len(payload[source])):
            print(payload[source][x])

            address = None
            classid = None
            if payload[source][x].get("class"):
                classid = payload[source][x]["class"]

            subclassid = None
            if payload[source][x].get("subclass"):
                subclassid = payload[source][x]["subclass"]

            enabled = 0
            if payload[source][x].get("enabled"):
                enabled = payload[source][x]["enabled"]

            properties = None
            if payload[source][x].get("attributes"):
                properties = payload[source][x]["attributes"]
            else:
                continue

            database_client.update_device_peripheral_configuration_by_deviceid(deviceid, source, x+1, address, classid, subclassid, enabled, properties)

    # process 1WIRE device configuration
    source = "1wire"
    if payload.get(source):
        for x in range(len(payload[source])):
            print(payload[source][x])

            address = None
            classid = None
            if payload[source][x].get("class"):
                classid = payload[source][x]["class"]

            subclassid = None
            if payload[source][x].get("subclass"):
                subclassid = payload[source][x]["subclass"]

            enabled = 0
            if payload[source][x].get("enabled"):
                enabled = payload[source][x]["enabled"]

            properties = None
            if payload[source][x].get("attributes"):
                properties = payload[source][x]["attributes"]
            else:
                continue

            database_client.update_device_peripheral_configuration_by_deviceid(deviceid, source, x+1, address, classid, subclassid, enabled, properties)


def on_message(subtopic, subpayload):

    #print(subtopic)
    #print(subpayload)

    arr_subtopic = subtopic.split(CONFIG_SEPARATOR, 2)
    if len(arr_subtopic) != 3:
        return

    deviceid = arr_subtopic[1]
    topic = arr_subtopic[2]
    payload = subpayload.decode("utf-8")

    if topic == API_REQUEST_CONFIGURATION:
        try:
            thr = threading.Thread(target = get_configuration, args = (g_database_client, deviceid, topic, payload ))
            thr.start()
        except Exception as e:
            print("exception API_REQUEST_CONFIGURATION")
            print(e)
            return
    elif topic == API_DELETE_CONFIGURATION:
        try:
            thr = threading.Thread(target = del_configuration, args = (g_database_client, deviceid, topic, payload ))
            thr.start()
        except Exception as e:
            print("exception API_DELETE_CONFIGURATION")
            print(e)
            return
    elif topic == API_SET_CONFIGURATION:
        try:
            thr = threading.Thread(target = set_configuration, args = (g_database_client, deviceid, topic, payload ))
            thr.start()
        except Exception as e:
            print("exception API_SET_CONFIGURATION")
            print(e)
            return


def on_mqtt_message(client, userdata, msg):

    try:
        if configuration_config.CONFIG_DEBUG:
            print("RCV: MQTT {} {}".format(msg.topic, msg.payload))
        on_message(msg.topic, msg.payload)
    except:
        return

def on_amqp_message(ch, method, properties, body):

    try:
        if configuration_config.CONFIG_DEBUG:
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
    subtopic = "{}{}+{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_SEPARATOR, API_REQUEST_CONFIGURATION)
    subtopic2 = "{}{}+{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_SEPARATOR, API_DELETE_CONFIGURATION)
    subtopic3 = "{}{}+{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_SEPARATOR, API_SET_CONFIGURATION)
    g_messaging_client.subscribe(subtopic, subscribe=True, declare=True, consume_continuously=True)
    g_messaging_client.subscribe(subtopic2, subscribe=True, declare=True, consume_continuously=True)
    g_messaging_client.subscribe(subtopic3, subscribe=True, declare=True, consume_continuously=True)


    while g_messaging_client.is_connected():
        time.sleep(3)
        pass

    print("application exits!")
