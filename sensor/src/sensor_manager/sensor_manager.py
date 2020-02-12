from sensor_config import config as sensor_config
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
CONFIG_DBHOST = sensor_config.CONFIG_MONGODB_HOST
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

CONFIG_DEVICE_ID            = "sensor_manager"

CONFIG_USERNAME             = sensor_config.CONFIG_MQTT_DEFAULT_USER
CONFIG_PASSWORD             = sensor_config.CONFIG_MQTT_DEFAULT_PASS

if CONFIG_USE_ECC:
    CONFIG_TLS_CA           = "../cert_ecc/rootca.pem"
    CONFIG_TLS_CERT         = "../cert_ecc/sensor_manager_cert.pem"
    CONFIG_TLS_PKEY         = "../cert_ecc/sensor_manager_pkey.pem"
else:
    CONFIG_TLS_CA           = "../cert/rootca.pem"
    CONFIG_TLS_CERT         = "../cert/sensor_manager_cert.pem"
    CONFIG_TLS_PKEY         = "../cert/sensor_manager_pkey.pem"

CONFIG_HOST                 = "localhost"
CONFIG_MQTT_TLS_PORT        = 8883
CONFIG_AMQP_TLS_PORT        = 5671

CONFIG_PREPEND_REPLY_TOPIC  = "server"
CONFIG_SEPARATOR            = '/'

API_RECEIVE_SENSOR_READING  = "rcv_sensor_reading"
API_REQUEST_SENSOR_READING  = "req_sensor_reading"
API_PUBLISH_SENSOR_READING  = "sensor_reading"



###################################################################################
# MQTT/AMQP callback functions
###################################################################################


def print_json(json_object):
    json_formatted_str = json.dumps(json_object, indent=2)
    print(json_formatted_str)


def store_sensor_reading(database_client, deviceid, source, address, value, subclass_value):

    try:
        #
        # get last record
        #print("{} source:{} address:{} value:{}".format(deviceid, source, address, value))
        sensor_readings = database_client.get_sensor_reading_by_deviceid(deviceid, source, address)
        if sensor_readings is None:
            #print("no readings")
            sensor_readings = {}
            sensor_readings["value"] = value
            sensor_readings["lowest"] = value
            sensor_readings["highest"] = value
            if subclass_value is not None:
                sensor_readings["subclass"] = {}
                sensor_readings["subclass"]["value"] = subclass_value
                sensor_readings["subclass"]["lowest"] = subclass_value
                sensor_readings["subclass"]["highest"] = subclass_value

        else:
            #
            # handle class
            sensor_readings["value"] = value
            if value > sensor_readings["highest"]:
                sensor_readings["highest"] = value
            elif value < sensor_readings["lowest"]:
                sensor_readings["lowest"] = value

            #
            # handle subclass
            if subclass_value is not None:
                sensor_readings["subclass"]["value"] = subclass_value
                if subclass_value > sensor_readings["subclass"]["highest"]:
                    sensor_readings["subclass"]["highest"] = subclass_value
                elif subclass_value < sensor_readings["subclass"]["lowest"]:
                    sensor_readings["subclass"]["lowest"] = subclass_value

        #
        # update sensor reading
        #print(sensor_readings)
        sensor_readings["value"] = float(sensor_readings["value"])
        sensor_readings["lowest"] = float(sensor_readings["lowest"])
        sensor_readings["highest"] = float(sensor_readings["highest"])
        if sensor_readings.get("subclass"):
            sensor_readings["subclass"]["value"] = float(sensor_readings["subclass"]["value"])
            sensor_readings["subclass"]["lowest"] = float(sensor_readings["subclass"]["lowest"])
            sensor_readings["subclass"]["highest"] = float(sensor_readings["subclass"]["highest"])
        database_client.add_sensor_reading(deviceid, source, address, sensor_readings)

        #
        # update sensor reading with timestamp for charting/graphing
        if sensor_config.CONFIG_ENABLE_DATASET:
            sensor_readings.pop("lowest")
            sensor_readings.pop("highest")
            if sensor_readings.get("subclass"):
                sensor_readings["subclass"].pop("lowest")
                sensor_readings["subclass"].pop("highest")
            database_client.add_sensor_reading_dataset(deviceid, source, address, sensor_readings)
    except:
        print("exception store_sensor_reading")
        pass


def forward_sensor_reading(database_client, deviceid, source, address, value, subclass_value):

    #
    # forward the packet to the specified recipient in the properties
    try:
        peripheral = source[0:len(source)-1]
        number = source[len(source)-1:]
        #print("source {} {} {} {}".format(source, peripheral, number, address))

        configuration = database_client.get_device_peripheral_configuration(deviceid, peripheral, int(number), address)
        #print_json(configuration)
        if configuration is not None:
            # check if continuous mode
            if configuration["attributes"]["mode"] == 2: 
                # get the device name
                dest_devicename = configuration["attributes"]["hardware"]["devicename"]
                if dest_devicename != "":
                    #print(dest_devicename)
                    sensor = database_client.get_sensor_by_deviceid(deviceid, peripheral, number, address)
                    if sensor is not None:
                        #print_json(sensor)
                        #print("")
                        dest_deviceid = database_client.get_deviceid(sensor["username"], dest_devicename)
                        if dest_deviceid is None:
                            return
                        dest_topic = "{}/{}".format(dest_deviceid, API_RECEIVE_SENSOR_READING)
                        #print("Hello")
                        dest_payload = {"sensors": []}
                        packet = {}
                        if sensor["formats"][0] == "int":
                            packet = {
                                "devicename": sensor["devicename"],
                                "peripheral": sensor["source"].upper(),
                                "sensorname": sensor["sensorname"],
                                "attribute":  sensor["attributes"][0],
                                "value":      int(value), 
                                #"peripheral": sensor["source"].upper(), 
                                #"number":     int(sensor["number"]), 
                                #"address":    int(sensor["address"]), 
                                #"class":      int
                            }
                        else:
                            packet = {
                                "devicename": sensor["devicename"],
                                "peripheral": sensor["source"].upper(),
                                "sensorname": sensor["sensorname"],
                                "attribute":  sensor["attributes"][0],
                                "value":      value, 
                            }
                        if subclass_value is not None:
                            if sensor["formats"][1] == "int":
                                packet["subclass"] = { 
                                    "attribute":  sensor["attributes"][1], 
                                    "value": int(subclass_value) 
                                }
                            else:
                                packet["subclass"] = { 
                                    "attribute":  sensor["attributes"][1], 
                                    "value": subclass_value 
                                }

                        dest_payload["sensors"].append(packet)
                        #print_json(dest_payload)
                        #print("")
                        dest_payload = json.dumps(dest_payload)
                        g_messaging_client.publish(dest_topic, dest_payload, debug=False) # NOTE: enable to DEBUG
    except:
        print("exception forward_sensor_reading")
        pass


def process_sensor_reading(database_client, deviceid, source, sensor):

    #
    # get address
    address = None
    if sensor.get("address"):
        address = sensor["address"]

    #
    # get value (for class and subclass)
    value = sensor["value"]
    # handle subclass
    subclass_value = None
    if sensor.get("subclass"):
        subclass_value = sensor["subclass"]["value"]

    #
    # store sensor reading
    thr1 = threading.Thread(target = store_sensor_reading, args = (database_client, deviceid, source, address, value, subclass_value, ))
    thr1.start()
    #store_sensor_reading(database_client, deviceid, source, address, value, subclass_value)

    #
    # forward sensor reading (if applicable)
    thr2 = threading.Thread(target = forward_sensor_reading, args = (database_client, deviceid, source, address, value, subclass_value, ))
    thr2.start()
    #forward_sensor_reading(database_client, deviceid, source, address, value, subclass_value)

    #
    # wait for store and forward threads to complete
    thr1.join()
    thr2.join()


def add_sensor_reading(database_client, deviceid, topic, payload):

    start_time = time.time()
    #print(deviceid)
    #print(topic)
    payload = json.loads(payload)


    thr_list = []

    for source in payload["sensors"]:
        for sensor in payload["sensors"][source]:
            thr = threading.Thread(target = process_sensor_reading, args = (database_client, deviceid, source, sensor, ))
            thr.start()
            thr_list.append(thr)
            #process_sensor_reading(database_client, deviceid, source, sensor)

    for thr in thr_list:
        thr.join()


    # print elapsed time
    print(time.time() - start_time) 
    #print("")


def get_sensor_reading(database_client, deviceid, topic, payload):
    #print("get_sensor_reading")
    #print(deviceid)
    payload = json.loads(payload)
    #print(payload["type"])
    #print(payload["sensors"])

    new_payload = {"sensors": []}
    for sensor in payload["sensors"]:
        value = 0

        # TODO: handle multiclass using sensor["attribute"]

        # elements are incomplete
        if sensor.get("peripheral") is None or sensor.get("number") is None:
            new_payload["sensors"].append({"value": value})
            print("{} elements are incomplete".format(deviceid))
            continue

        # read value from database
        peripheral = sensor["peripheral"].lower()
        source = "{}{}".format(peripheral, sensor["number"])
        address = None
        if peripheral == "i2c":
            if sensor.get("address") is None:
                new_payload["sensors"].append({"value": value})
                print("{} elements are incomplete".format(deviceid))
                continue
            address = sensor["address"]
        sensor_readings = database_client.get_sensor_reading_by_deviceid(sensor["deviceid"], source, address)

        # use the retrieved value if exists
        entry = {}
        entry["sensorname"] = sensor["sensorname"]
        if sensor_readings is None:
            entry["value"] = value
        else:
            entry["value"] = sensor_readings["value"]
        new_payload["sensors"].append(entry)

    if len(new_payload["sensors"]) > 0:
        # add the source parameter
        if payload.get("source"):
            new_payload["source"] = payload["source"]

        new_topic = "{}/{}".format(deviceid, API_RECEIVE_SENSOR_READING)
        new_payload = json.dumps(new_payload)
        g_messaging_client.publish(new_topic, new_payload, debug=False) # NOTE: enable to DEBUG


def on_message(subtopic, subpayload):

    #print(subtopic)
    #print(subpayload)

    arr_subtopic = subtopic.split("/", 2)
    if len(arr_subtopic) != 3:
        return

    deviceid = arr_subtopic[1]
    topic = arr_subtopic[2]
    payload = subpayload.decode("utf-8")

    if topic == API_PUBLISH_SENSOR_READING:
        try:
            thr = threading.Thread(target = add_sensor_reading, args = (g_database_client, deviceid, topic, payload ))
            thr.start()
        except Exception as e:
            print("exception API_PUBLISH_SENSOR_READING")
            print(e)
            return
    elif topic == API_REQUEST_SENSOR_READING:
        try:
            thr = threading.Thread(target = get_sensor_reading, args = (g_database_client, deviceid, topic, payload ))
            thr.start()
        except Exception as e:
            print("exception API_REQUEST_SENSOR_READING")
            print(e)
            return


def on_mqtt_message(client, userdata, msg):

    try:
        if sensor_config.CONFIG_DEBUG_SENSOR_READING:
            print("RCV: MQTT {} {}".format(msg.topic, msg.payload))
        on_message(msg.topic, msg.payload)
    except:
        return

def on_amqp_message(ch, method, properties, body):

    try:
        if sensor_config.CONFIG_DEBUG_SENSOR_READING:
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
    subtopic = "{}{}+{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_SEPARATOR, API_PUBLISH_SENSOR_READING)
    #subtopic2 = "{}{}+{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_SEPARATOR, API_REQUEST_SENSOR_READING)
    g_messaging_client.subscribe(subtopic, subscribe=True, declare=True, consume_continuously=True)
    #g_messaging_client.subscribe(subtopic2, subscribe=True, declare=True, consume_continuously=True)


    while g_messaging_client.is_connected():
        time.sleep(3)
        pass

    print("application exits!")
