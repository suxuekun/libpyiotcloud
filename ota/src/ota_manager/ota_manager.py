from ota_config import config as ota_config
from web_server_database import database_client
from datetime import datetime
import json
import time
import argparse
import threading
import sys
import os
import inspect
import base64
import binascii
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from messaging_client import messaging_client
from s3_client import s3_client



###################################################################################
# Use ECC or RSA certificates
CONFIG_USE_ECC = True if int(os.environ["CONFIG_USE_ECC"]) == 1 else False
# Enable to use AMQP for webserver-to-messagebroker communication
# Disable to use MQTT for webserver-to-messagebroker communication
CONFIG_USE_AMQP = False
CONFIG_DBHOST = ota_config.CONFIG_MONGODB_HOST
###################################################################################



###################################################################################
# global variables
###################################################################################

g_messaging_client = None
g_sensor_client = None
g_database_client = None
g_storage_client = None

g_document_firmwares = None

g_timer_thread_timeout = 86400 # 1 day (60*60*24=86400 seconds)
g_timer_thread = None
g_timer_thread_stop = None



###################################################################################
# MQTT and AMQP default configurations
###################################################################################

CONFIG_DEVICE_ID            = "ota_manager"

CONFIG_USERNAME             = ota_config.CONFIG_MQTT_DEFAULT_USER
CONFIG_PASSWORD             = ota_config.CONFIG_MQTT_DEFAULT_PASS

if CONFIG_USE_ECC:
    CONFIG_TLS_CA           = "../cert_ecc/rootca.pem"
    CONFIG_TLS_CERT         = "../cert_ecc/ota_manager_cert.pem"
    CONFIG_TLS_PKEY         = "../cert_ecc/ota_manager_pkey.pem"
else:
    CONFIG_TLS_CA           = "../cert/rootca.pem"
    CONFIG_TLS_CERT         = "../cert/ota_manager_cert.pem"
    CONFIG_TLS_PKEY         = "../cert/ota_manager_pkey.pem"

CONFIG_HOST                 = "localhost"
CONFIG_MQTT_TLS_PORT        = 8883
CONFIG_AMQP_TLS_PORT        = 5671

CONFIG_PREPEND_REPLY_TOPIC  = "server"
CONFIG_SEPARATOR            = '/'

# download firmware via MQTT
API_UPGRADE_FIRMWARE             = "beg_ota"
API_UPGRADE_FIRMWARE_COMPLETION  = "end_ota"
#API_REQUEST_FIRMWARE             = "req_firmware"
#API_RECEIVE_FIRMWARE             = "rcv_firmware"
API_REQUEST_OTASTATUS            = "req_otastatus"
API_REQUEST_TIME                 = "req_time"
API_RECEIVE_TIME                 = "rcv_time"



###################################################################################
# Helper functions
###################################################################################

def print_json(json_object):
    json_formatted_str = json.dumps(json_object, indent=2)
    print(json_formatted_str)

#def read_file(filename, offset, size):
#    # read segment from file
#    f = open(filename, "rb")
#    f.seek(offset)
#    bin = f.read(size)
#    f.close()
#    return bin
#
#def read_file_chunk(payload):
#    # get file name
#    index = payload["location"].rindex("/")
#    if index == -1:
#        index = 0
#    else:
#        index += 1
#    filename = payload["location"][index:]
#
#    # read segment from file
#    bin = read_file(filename, payload["offset"], payload["size"])
#
#    # convert bin to be JSON compatible
#    actualsize = len(bin)
#    bin = base64.b64encode(bin).decode("utf-8")
#    return bin, actualsize


###################################################################################
# Threaded callback functions
###################################################################################

def request_time(database_client, deviceid, topic, payload):

    new_topic = "{}{}{}".format(deviceid, CONFIG_SEPARATOR, API_RECEIVE_TIME)
    new_payload = {
        "time": int(time.time())
    }
    new_payload = json.dumps(new_payload)
    g_messaging_client.publish(new_topic, new_payload, debug=False) # NOTE: enable to DEBUG


def request_otastatus(database_client, deviceid, topic, payload):

    new_topic = "{}{}{}".format(deviceid, CONFIG_SEPARATOR, API_REQUEST_OTASTATUS)

    # find if deviceid exists
    devicename = database_client.get_devicename(deviceid)
    if devicename is None:
        # if no entry found, just send an empty json
        new_payload = {}
        new_payload = json.dumps(new_payload)
        g_messaging_client.publish(new_topic, new_payload, debug=False) # NOTE: enable to DEBUG
        return

    ota_status = database_client.get_ota_status_by_deviceid(deviceid)
    #print_json(ota_status)
    if ota_status is None:
        # if no entry found, just send an empty json
        new_payload = {}
        new_payload = json.dumps(new_payload)
        g_messaging_client.publish(new_topic, new_payload, debug=False) # NOTE: enable to DEBUG
        return
    #print(ota_status["status"])
    if ota_status["status"] == "completed": #or ota_status["status"] == "failed":
        # if no entry found, just send an empty json
        new_payload = {}
        new_payload = json.dumps(new_payload)
        g_messaging_client.publish(new_topic, new_payload, debug=False) # NOTE: enable to DEBUG
        return


    print("REQUEST {} {} [status:{} version:{}]".format(deviceid, devicename, ota_status["status"], ota_status["version"]))
    start_time = time.time()

    # make sure we have the latest firmware details synching with AWS S3
    # get the details of the requested firmware
    download_firmwares()
    firmware = get_firmware_object(ota_status["version"])
    if firmware is None:
        print("Error: get_firmware_object is None")
        new_payload = {}
        new_payload = json.dumps(new_payload)
        g_messaging_client.publish(new_topic, new_payload, debug=False) # NOTE: enable to DEBUG
        return

    new_topic = "{}{}{}".format(deviceid, CONFIG_SEPARATOR, API_UPGRADE_FIRMWARE)
    new_payload = {
        "size"     : firmware["size"],
        "location" : firmware["location"],
        "version"  : firmware["version"],
        "checksum" : firmware["checksum"],
    }

    # publish packet response to device
    new_payload = json.dumps(new_payload)
    g_messaging_client.publish(new_topic, new_payload, debug=False) # NOTE: enable to DEBUG

    # set status to ongoing
    database_client.set_ota_status_ongoing_by_deviceid(deviceid, firmware["version"])


    # print elapsed time
    print(time.time() - start_time) 
    print("")


def upgrade_firmware_completion(database_client, deviceid, topic, payload):

    # find if deviceid exists
    devicename = database_client.get_devicename(deviceid)
    if devicename is None:
        return

    # parse parameter
    payload = json.loads(payload)
    if payload.get("value") is None:
        return
    if payload["value"].get("result") is None:
        return
    result = payload["value"]["result"]

    print("COMPLETE {} {} [{}]".format(deviceid, devicename, result))

    # set the status
    ota_status = database_client.get_ota_status_by_deviceid(deviceid)
    #print_json(ota_status)
    if ota_status["status"] != "completed":
        if result == "completed":
            database_client.set_ota_status_completed_by_deviceid(deviceid, "completed")
        else:
            database_client.set_ota_status_completed_by_deviceid(deviceid, "failed")

    #ota_status = database_client.get_ota_status_by_deviceid(deviceid)
    #print_json(ota_status)


#def request_firmware(database_client, deviceid, topic, payload):
#
#    new_topic = "{}{}{}".format(deviceid, CONFIG_SEPARATOR, API_RECEIVE_FIRMWARE)
#
#    # find if deviceid exists
#    devicename = database_client.get_devicename(deviceid)
#    if devicename is None:
#        # if no entry found, just send an empty json
#        new_payload = {}
#        new_payload = json.dumps(new_payload)
#        g_messaging_client.publish(new_topic, new_payload, debug=False) # NOTE: enable to DEBUG
#        return
#
#    payload = json.loads(payload)
#    if payload["offset"] == 0:
#        print("")
#    print("{}: {} {} {}".format(deviceid, payload["location"], payload["size"], payload["offset"]))
#
#    # read segment from file
#    bin, actualsize = read_file_chunk(payload)
#
#    # set topic and payload template for the response
#    new_payload = {
#        "location": payload["location"],
#        "size"    : actualsize,
#        "offset"  : payload["offset"],
#        "bin"     : bin
#    }
#
#    # publish packet response to device
#    #print_json(new_payload)
#    new_payload = json.dumps(new_payload)
#    g_messaging_client.publish(new_topic, new_payload, debug=False) # NOTE: enable to DEBUG


###################################################################################
# MQTT Packet Processing
###################################################################################

def on_message(subtopic, subpayload):

    #print(subtopic)
    #print(subpayload)

    # parse parameters
    arr_subtopic = subtopic.split(CONFIG_SEPARATOR, 2)
    if len(arr_subtopic) != 3:
        return
    deviceid = arr_subtopic[1]
    topic = arr_subtopic[2]
    payload = subpayload.decode("utf-8")

    # process mqtt packet based on topic
    if topic == API_REQUEST_OTASTATUS:
        try:
            thr = threading.Thread(target = request_otastatus, args = (g_database_client, deviceid, topic, payload ))
            thr.start()
        except Exception as e:
            print("exception API_REQUEST_OTASTATUS")
            print(e)
    elif topic == API_UPGRADE_FIRMWARE_COMPLETION:
        try:
            thr = threading.Thread(target = upgrade_firmware_completion, args = (g_database_client, deviceid, topic, payload ))
            thr.start()
        except Exception as e:
            print("exception API_UPGRADE_FIRMWARE_COMPLETION")
            print(e)
    elif topic == API_REQUEST_TIME:
        try:
            thr = threading.Thread(target = request_time, args = (g_database_client, deviceid, topic, payload ))
            thr.start()
        except Exception as e:
            print("exception API_REQUEST_TIME")
            print(e)
    #elif topic == API_REQUEST_FIRMWARE: 
    #    # to be removed later; device will download via HTTPS instead of MQTTS
    #    try:
    #        thr = threading.Thread(target = request_firmware, args = (g_database_client, deviceid, topic, payload ))
    #        thr.start()
    #    except Exception as e:
    #        print("exception API_REQUEST_FIRMWARE")
    #        print(e)

def on_mqtt_message(client, userdata, msg):

    try:
        if ota_config.CONFIG_DEBUG:
            print("RCV: MQTT {} {}".format(msg.topic, msg.payload))
        on_message(msg.topic, msg.payload)
    except:
        return

def on_amqp_message(ch, method, properties, body):

    try:
        if ota_config.CONFIG_DEBUG:
            print("RCV: AMQP {} {}".format(method.routing_key, body))
        on_message(method.routing_key, body)
    except:
        return


###################################################################################
# Download files from Amazon S3
###################################################################################

def get_firmware_object(version):
    global g_document_firmwares
    for firmware in g_document_firmwares["ft900"]["firmware"]:
        if version == firmware["version"]:
            return firmware
    return None

def download_firmwares():
    global g_document_firmwares
    print(datetime.now())
    result, document_firmwares = g_storage_client.get_device_firmware_updates()
    if result:
        g_document_firmwares = document_firmwares
        for firmware in g_document_firmwares["ft900"]["firmware"]:
            print("{} {} {} {} {}".format(firmware["version"], firmware["date"], firmware["location"], firmware["size"], firmware["checksum"]))
            #result = download_firmware(firmware["location"], firmware["checksum"])
            #if result:
            #    print("Downloaded {} {} {} {} {} [{}]".format(firmware["version"], firmware["date"], firmware["location"], firmware["size"], firmware["checksum"], result))
    #print("")
    return result

#def get_filename(filename):
#    index = filename.rindex("/")
#    if index == -1:
#        index = 0
#    else:
#        index += 1
#    new_filename = filename[index:]
#    return new_filename
#
#def write_to_file(filename, contents):
#    f = open(filename, "wb")
#    f.write(contents)
#    f.close()
#
#def read_file(filename):
#    try:
#        f = open(filename, "rb")
#        contents = f.read()
#        f.close()
#        return contents
#    except:
#        pass
#    return None
#
#def compute_checksum(contents):
#    return binascii.crc32(contents)
#
#def download_firmware(location, checksum):
#    filename = get_filename(location)
#
#    # dont download file from S3 if existing file already exists
#    contents = read_file(filename)
#    if contents is not None:
#        # check if file is the same using checksum
#        if compute_checksum(contents) == checksum:
#            return True
#
#    # download the file from S3
#    print("{} does not exist (or checksum not same). Proceeding to download from S3.".format(filename))
#    file_path = "firmware/" + location
#    result, binary = g_storage_client.get_firmware(file_path)
#    if result:
#        # save contents to file
#        write_to_file(filename, binary)
#
#    return result


###################################################################################
# Timer thread for daily synching with AWS S3
###################################################################################

class TimerThread(threading.Thread):

    def __init__(self, event, timeout):
        threading.Thread.__init__(self)
        self.stopped = event
        self.timeout = timeout

    def run(self):
        while not self.stopped.wait(self.timeout) and g_messaging_client.is_connected(): 
            download_firmwares()
        print("TimerThread exits")


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


    # Initialize S3 client
    g_storage_client = s3_client()
    try:
        print("")
        download_firmwares()
    except Exception as e:
        print(e)


    # Subscribe to messages sent for this device
    time.sleep(1)
    subtopic  = "{}{}+{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_SEPARATOR, API_REQUEST_OTASTATUS)
    subtopic2 = "{}{}+{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_SEPARATOR, API_UPGRADE_FIRMWARE_COMPLETION)
    subtopic3 = "{}{}+{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_SEPARATOR, API_REQUEST_TIME)
    #subtopic4  = "{}{}+{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_SEPARATOR, API_REQUEST_FIRMWARE)
    g_messaging_client.subscribe(subtopic,  subscribe=True, declare=True, consume_continuously=True)
    g_messaging_client.subscribe(subtopic2, subscribe=True, declare=True, consume_continuously=True)
    g_messaging_client.subscribe(subtopic3, subscribe=True, declare=True, consume_continuously=True)
    #g_messaging_client.subscribe(subtopic4,  subscribe=True, declare=True, consume_continuously=True)


    # Initialize timer thread for synchronizing with AWS S3
    g_timer_thread_stop = threading.Event()
    g_timer_thread = TimerThread(g_timer_thread_stop, g_timer_thread_timeout)
    g_timer_thread.start()

    # Main loop
    while g_messaging_client.is_connected():
        time.sleep(3)
        pass

    # Uninitialize timer thread
    g_timer_thread_stop.set()
    g_timer_thread.join()

    print("application exits!")

