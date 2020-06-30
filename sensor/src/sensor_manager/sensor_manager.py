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
g_queue_activated_sensors = {}



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
API_PUBLISH_SENSOR_READING  = "pub_sensor_reading"



###################################################################################
# Sensor value thresholding for notification triggering
###################################################################################

CONFIG_THRESHOLDING_NOTIFICATIONS       = True
CONFIG_THRESHOLDING_NOTIFICATIONS_DEBUG = True

MODE_THRESHOLD_SINGLE       = 0
MODE_THRESHOLD_DUAL         = 1
MODE_CONTINUOUS             = 2
ACTIVATE_OUT_OF_RANGE       = 0
ACTIVATE_WITHIN_RANGE       = 1
ALERT_ONCE                  = 0
ALERT_CONTINUOUSLY          = 1

MENOS_MOBILE                = "mobile"
MENOS_EMAIL                 = "email"
MENOS_NOTIFICATION          = "notification"
MENOS_MODEM                 = "modem"
MENOS_STORAGE               = "storage"
MENOS_DEFAULT               = "default"



###################################################################################
# MQTT/AMQP callback functions
###################################################################################


def print_json(json_object):
    json_formatted_str = json.dumps(json_object, indent=2)
    print(json_formatted_str)


def store_sensor_reading(database_client, username, devicename, deviceid, source, number, value, timestamp):

    try:
        #
        # get last record
        #print("{} source:{} number:{} value:{}".format(deviceid, source, number, value))
        sensor_readings = database_client.get_sensor_reading_by_deviceid(deviceid, source, number)
        if sensor_readings is None:
            #print("no readings")
            sensor_readings = {}
            sensor_readings["value"] = value
            sensor_readings["lowest"] = value
            sensor_readings["highest"] = value
        else:
            #
            # handle class
            sensor_readings["value"] = value
            if value > sensor_readings["highest"]:
                sensor_readings["highest"] = value
            elif value < sensor_readings["lowest"]:
                sensor_readings["lowest"] = value

        #
        # update sensor reading
        #print(sensor_readings)
        sensor_readings["value"] = float(sensor_readings["value"])
        sensor_readings["lowest"] = float(sensor_readings["lowest"])
        sensor_readings["highest"] = float(sensor_readings["highest"])
        database_client.add_sensor_reading(username, deviceid, source, number, sensor_readings)

        #
        # update sensor reading with timestamp for charting/graphing
        if sensor_config.CONFIG_ENABLE_DATASET:
            database_client.add_sensor_reading_dataset(username, deviceid, source, number, value, timestamp)
    except Exception as e:
        print(e)
        print("exception store_sensor_reading")
        pass


# for notification triggering used in thresholding modes
def menos_publish(menos, deviceid, recipient=None, message=None, peripheral="uart", number="", activate=None, condition=None):

    # set the topic
    topic = "{}/{}/trigger_notification/{}{}/{}".format(CONFIG_PREPEND_REPLY_TOPIC, deviceid, peripheral, number, menos)

    # set the payload
    payload = {}
    if recipient is not None:
        payload["recipient"] = recipient
    if message is not None:
        payload["message"] = message
    if activate is not None:
        payload["activate"] = activate
    if condition is not None:
        payload["condition"] = condition

    # publish the payload on the topic
    payload = json.dumps(payload)
    g_messaging_client.publish(topic, payload, debug=False)
    if CONFIG_THRESHOLDING_NOTIFICATIONS_DEBUG:
        print("{} {}".format(deviceid, condition))


# for notification triggering used in thresholding modes
def process_thresholding_notification(attributes, value, classname, sensor, source, deviceid, peripheral, number):
    mode = attributes["mode"]
    threshold = attributes["threshold"]
    alert_type = attributes["alert"]["type"]
    #alert_period = attributes["alert"]["alert_period"]

    if mode == MODE_THRESHOLD_SINGLE:
        # single threshold
        deviceid_source_sensor = "{}.{}{}.{}.single".format(deviceid, source, sensor["sensorname"], classname)

        threshold_value = threshold["value"]
        #print("MODE_THRESHOLD_SINGLE {} {} {}".format(classname, value, threshold_value))

        if value > threshold_value:
            # check for activation
            if alert_type == ALERT_ONCE:
                if deviceid_source_sensor not in g_queue_activated_sensors:
                    #print("activate: value > threshold_value; alert once")
                    condition = "{} {} > {} (activation)".format(classname, value, threshold_value)
                    menos_publish(MENOS_DEFAULT, deviceid, None, None, peripheral, number, 1, condition )
                g_queue_activated_sensors[deviceid_source_sensor] = threshold_value
            elif alert_type == ALERT_CONTINUOUSLY:
                #print("activate: value > threshold_value; alert continuously")
                g_queue_activated_sensors[deviceid_source_sensor] = threshold_value
                condition = "{} {} > {} (activation)".format(classname, value, threshold_value)
                menos_publish(MENOS_DEFAULT, deviceid, None, None, peripheral, number, 1, condition )
        else:
            # check for deactivation
            if deviceid_source_sensor in g_queue_activated_sensors:
                # if previously activated, send deactivation
                queue_value = g_queue_activated_sensors[deviceid_source_sensor]
                g_queue_activated_sensors.pop(deviceid_source_sensor)
                condition = "{} {} <= {} (deactivation)".format(classname, value, threshold_value)
                menos_publish(MENOS_DEFAULT, deviceid, None, None, peripheral, number, 0, condition )

    elif mode == MODE_THRESHOLD_DUAL:
        # dual threshold
        deviceid_source_sensor = "{}.{}{}.{}.dual".format(deviceid, source, sensor["sensorname"], classname)

        threshold_min = threshold["min"]
        threshold_max = threshold["max"]
        threshold_activate = threshold["activate"]
        #print("MODE_THRESHOLD_DUAL {} {} [{} {}] {}".format(classname, value, threshold_min, threshold_max, threshold_activate))

        if threshold_activate == ACTIVATE_OUT_OF_RANGE:

            if value < threshold_min or value > threshold_max:
                # check for activation
                if alert_type == ALERT_ONCE:
                    if deviceid_source_sensor not in g_queue_activated_sensors:
                        #print("activate: value > threshold_value; alert once")
                        if value < threshold_min:
                            condition = "{} {} < {} (activation)".format(classname, value, threshold_min)
                        else:
                            condition = "{} {} > {} (activation)".format(classname, value, threshold_max)
                        menos_publish(MENOS_DEFAULT, deviceid, None, None, peripheral, number, 1, condition )
                    g_queue_activated_sensors[deviceid_source_sensor] = value
                elif alert_type == ALERT_CONTINUOUSLY:
                    #print("activate: value > threshold_value; alert continuously")
                    g_queue_activated_sensors[deviceid_source_sensor] = value
                    if value < threshold_min:
                        condition = "{} {} < {} (activation)".format(classname, value, threshold_min)
                    else:
                        condition = "{} {} > {} (activation)".format(classname, value, threshold_max)
                    menos_publish(MENOS_DEFAULT, deviceid, None, None, peripheral, number, 1, condition )
            else:
                # check for deactivation
                if deviceid_source_sensor in g_queue_activated_sensors:
                    # if previously activated, send deactivation
                    queue_value = g_queue_activated_sensors[deviceid_source_sensor]
                    g_queue_activated_sensors.pop(deviceid_source_sensor)
                    condition = "{} {} <= {} <= {} (deactivation)".format(classname, threshold_min, value, threshold_max)
                    menos_publish(MENOS_DEFAULT, deviceid, None, None, peripheral, number, 0, condition)

        elif threshold_activate == ACTIVATE_WITHIN_RANGE:

            if value >= threshold_min and value <= threshold_max:
                # check for activation
                if alert_type == ALERT_ONCE:
                    if deviceid_source_sensor not in g_queue_activated_sensors:
                        #print("activate: value > threshold_value; alert once")
                        condition = "{} {} <= {} <= {} (activation)".format(classname, threshold_min, value, threshold_max)
                        menos_publish(MENOS_DEFAULT, deviceid, None, None, peripheral, number, 1, condition)
                    g_queue_activated_sensors[deviceid_source_sensor] = value
                elif alert_type == ALERT_CONTINUOUSLY:
                    #print("activate: value > threshold_value; alert continuously")
                    g_queue_activated_sensors[deviceid_source_sensor] = value
                    condition = "{} {} <= {} <= {} (activation)".format(classname, threshold_min, value, threshold_max)
                    menos_publish(MENOS_DEFAULT, deviceid, None, None, peripheral, number, 1, condition)
            else:
                # check for deactivation
                if deviceid_source_sensor in g_queue_activated_sensors:
                    # if previously activated, send deactivation
                    queue_value = g_queue_activated_sensors[deviceid_source_sensor]
                    g_queue_activated_sensors.pop(deviceid_source_sensor)
                    if value < threshold_min:
                        condition = "{} {} < {} (deactivation)".format(classname, value, threshold_min)
                    else:
                        condition = "{} {} > {} (deactivation)".format(classname, value, threshold_max)
                    menos_publish(MENOS_DEFAULT, deviceid, None, None, peripheral, number, 0, value)


def forward_sensor_reading(database_client, username, devicename, deviceid, source, number, value):

    #
    # forward the packet to the specified recipient in the properties
    try:
        peripheral = source
        #print("source {} {} {} {}".format(source, peripheral, str(number), number))

        configuration = database_client.get_device_peripheral_configuration(deviceid, peripheral, number)
        #print_json(configuration)
        if configuration is not None:
            mode = configuration["attributes"]["mode"]
            # check if continuous mode (sensor forwarding) or thresholding mode (notification triggering)
            if mode == MODE_CONTINUOUS: 
                enabled = False
                if configuration["attributes"]["hardware"].get("enable") is not None:
                    enabled = configuration["attributes"]["hardware"]["enable"]
                #print(enabled)

                if enabled:
                    # continuous mode (sensor forwarding)
                    dest_devicename = configuration["attributes"]["hardware"]["devicename"]
                    if dest_devicename != "":
                        #print(dest_devicename)
                        sensor = database_client.get_sensor_by_deviceid(deviceid, peripheral, str(number))
                        if sensor is not None:
                            #print_json(sensor)
                            #print("")
                            dest_deviceid = database_client.get_deviceid(username, dest_devicename)
                            if dest_deviceid is None:
                                return
                            dest_topic = "{}/{}".format(dest_deviceid, API_RECEIVE_SENSOR_READING)
                            #print("Hello")
                            dest_payload = {"sensors": []}
                            packet = {}
                            if sensor["format"] == "integer":
                                packet = {
                                    "UID":   sensor["source"],
                                    "SAID":  sensor["number"],
                                    "value": int(value), 
                                }
                            else:
                                packet = {
                                    "UID":   sensor["source"],
                                    "SAID":  sensor["number"],
                                    "value": value, 
                                }

                            dest_payload["sensors"].append(packet)
                            #print_json(dest_payload)
                            #print("")
                            dest_payload = json.dumps(dest_payload)
                            g_messaging_client.publish(dest_topic, dest_payload, debug=False) # NOTE: enable to DEBUG
            else:
                # thresholding mode (notification triggering)
                if CONFIG_THRESHOLDING_NOTIFICATIONS:
                    sensor = database_client.get_sensor_by_deviceid(deviceid, peripheral, str(number))
                    if sensor is not None:
                        process_thresholding_notification(configuration["attributes"], value, sensor["class"], sensor, source, deviceid, peripheral, str(number))

    except:
        print("exception forward_sensor_reading")
        pass


def add_sensor_reading(database_client, deviceid, topic, payload):

    #start_time = time.time()
    #print(deviceid)
    #print(topic)
    payload = json.loads(payload)

    username, devicename = database_client.get_username_devicename(deviceid)
    if username is None or devicename is None:
        return

    thr_list = []
    for number in range(len(payload["SNS"])):
        value = payload["SNS"][number]
        # Ignore if value is "NaN"
        if payload["SNS"][number] != "NaN":
            #
            # store sensor reading
            thr1 = threading.Thread(target = store_sensor_reading, args = (database_client, username, devicename, deviceid, payload["UID"], number, float(value), int(payload["TS"]), ))
            thr1.start()
            thr_list.append(thr1)

            #
            # forward sensor reading (if applicable)
            thr2 = threading.Thread(target = forward_sensor_reading, args = (database_client, username, devicename, deviceid, payload["UID"], number, float(value), ))
            thr2.start()
            thr_list.append(thr2)

    for thr in thr_list:
        thr.join()


    # print elapsed time
    #print(time.time() - start_time) 
    #print("")


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
    #print("USE_USERNAME={}".format(args.USE_USERNAME))
    #print("USE_PASSWORD={}".format(args.USE_PASSWORD))
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
