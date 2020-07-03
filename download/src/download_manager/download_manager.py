from download_config import config as download_config
from web_server_database import database_client
from datetime import datetime
import json
import time
import argparse
import threading
import sys
import os
import inspect
import zipfile
import shutil
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from messaging_client import messaging_client
from s3_client import s3_client
from pinpoint_client import pinpoint_client



###################################################################################
# Use ECC or RSA certificates
CONFIG_USE_ECC = True if int(os.environ["CONFIG_USE_ECC"]) == 1 else False
# Enable to use AMQP for webserver-to-messagebroker communication
# Disable to use MQTT for webserver-to-messagebroker communication
CONFIG_USE_AMQP = False
CONFIG_DBHOST = download_config.CONFIG_MONGODB_HOST
###################################################################################



###################################################################################
# global variables
###################################################################################

g_messaging_client = None
g_database_client = None
g_pinpoint_client = None
g_s3_client = None


###################################################################################
# MQTT and AMQP default configurations
###################################################################################

CONFIG_DEVICE_ID            = "download_manager"

CONFIG_USERNAME             = download_config.CONFIG_MQTT_DEFAULT_USER
CONFIG_PASSWORD             = download_config.CONFIG_MQTT_DEFAULT_PASS

if CONFIG_USE_ECC:
    CONFIG_TLS_CA           = "../cert_ecc/rootca.pem"
    CONFIG_TLS_CERT         = "../cert_ecc/download_manager_cert.pem"
    CONFIG_TLS_PKEY         = "../cert_ecc/download_manager_pkey.pem"
else:
    CONFIG_TLS_CA           = "../cert/rootca.pem"
    CONFIG_TLS_CERT         = "../cert/download_manager_cert.pem"
    CONFIG_TLS_PKEY         = "../cert/download_manager_pkey.pem"

CONFIG_HOST                 = "localhost"
CONFIG_MQTT_TLS_PORT        = 8883
CONFIG_AMQP_TLS_PORT        = 5671

CONFIG_PREPEND_REPLY_TOPIC  = "server"
CONFIG_SEPARATOR            = '/'

API_DOWNLOAD_SENSOR_DATA    = "download_device_sensor_data"



###################################################################################
# MQTT/AMQP callback functions
###################################################################################


def print_json(json_object):
    json_formatted_str = json.dumps(json_object, indent=2)
    print(json_formatted_str)

def create_folder(foldername):
    try:
        os.makedirs(foldername)
    except Exception as e:
        print("exception create_folder")
        print(e)

def delete_folder(foldername):
    try:
        shutil.rmtree(foldername)
    except Exception as e:
        #print(e)
        pass

def write_file(foldername, filename, contents):
    file = foldername + "/" + filename + ".csv"
    try:
        f = open(file, "w")
        f.write(contents)
        f.close()
    except Exception as e:
        print("exception write_file")
        print(e)

def tuple_to_string(timestamp, value):
    return "{},{}\n".format(timestamp, value)

def generate_file(database_client, deviceid, uid, said, format, accuracy):
    contents = tuple_to_string("timestamp", "value")
    dataset = database_client.get_sensor_reading_dataset_by_deviceid(deviceid, uid, said)
    if format == "integer":
        for data in dataset:
            contents += tuple_to_string(data["timestamp"], int(data["value"]))
    else:
        if int(accuracy) == 0:
            for data in dataset:
                contents += tuple_to_string(data["timestamp"], int(data["value"]))
        elif int(accuracy) == 1:
            for data in dataset:
                contents += tuple_to_string(data["timestamp"], "{:.1f}".format(data["value"]))
        else:
            for data in dataset:
                contents += tuple_to_string(data["timestamp"], "{:.2f}".format(data["value"]))
    write_file(deviceid, "{}-{}".format(uid, said), contents)

def generate_files(database_client, deviceid, ldsus):
    threaded = True
    create_folder(deviceid)

    if not threaded:
        for ldsu in ldsus:
            generate_file(database_client, deviceid, ldsu["UID"], ldsu["SAID"], ldsu["FORMAT"], int(ldsu["ACCURACY"]))
    else:
        thr_list = []
        for ldsu in ldsus:
            thr1 = threading.Thread(target = generate_file, args = (database_client, deviceid, ldsu["UID"], ldsu["SAID"], ldsu["FORMAT"], int(ldsu["ACCURACY"]), ) )
            thr1.start()
            thr_list.append(thr1)
        for thr in thr_list:
            thr.join()

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

def create_zipfile(deviceid):
    filename = deviceid + '.zip'
    try:
        zipf = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)
        zipdir(deviceid + '/', zipf)
        zipf.close()
    except:
        return None
    return filename

def delete_zipfile(deviceid):
    filename = deviceid + '.zip'
    try:
        os.remove(filename)
    except Exception as e:
        #print(e)
        return False
    return True

def read_zipfile(filename):
    try:
        f = open(filename, "rb")
        contents = f.read()
        f.close()
        return contents
    except:
        pass
    return None

def upload_zipfile(zip_file, contents):
    try:
        url = s3_client().upload_sensordata_zipfile(zip_file, contents)
        return url
    except:
        pass
    return None

def construct_invoice_message(name, email, url, devicename, deviceid):
    message =  "Hi {},\r\n\r\n\r\n".format(name)

    message += "Sensor data for device {} with UUID {} is now available.\r\n".format(devicename, deviceid)
    message += "Click the link below to download.\r\n\r\n"
    message += url
    message += "\r\n\r\n"

    message += "\r\nBest Regards,\r\n"
    message += "Bridgetek Pte. Ltd.\r\n"
    return message

def send_email(name, email, url, devicename, deviceid):
    try:
        message = construct_invoice_message(name, email, url, devicename, deviceid)
        client = pinpoint_client()
        client.initialize()
        response = client.send_message(email, message)
    except Exception as e:
        print(e)
        return False

    try:
        result = response["ResponseMetadata"]["HTTPStatusCode"]==200 and response["MessageResponse"]["Result"][email]["StatusCode"]==200
        print("DOWNLOAD {} {} {} [{}]".format(email, deviceid, url, result))
    except Exception as e:
        print(e)
        return False

    return result

def download_device_sensor_data(database_client, deviceid, topic, payload):
    start_time = time.time()
    print(deviceid)

    payload = json.loads(payload)
    if payload.get("name") is None or payload.get("email") is None or payload.get("devicename") is None or payload.get("ldsus") is None:
        return
    #print_json(payload)

    username, devicename = database_client.get_username_devicename(deviceid)
    if username is None or devicename is None:
        return


    delete_folder(deviceid)
    delete_zipfile(deviceid)

    generate_files(database_client, deviceid, payload["ldsus"])
    zip_file = create_zipfile(deviceid)
    if zip_file:
        contents = read_zipfile(zip_file)
        if contents:
            url = upload_zipfile(zip_file, contents)
            if url:
                send_email(payload["name"], payload["email"], url, payload["devicename"], deviceid)

    #delete_folder(deviceid)
    #delete_zipfile(deviceid)


    # print elapsed time
    print(time.time() - start_time) 
    print("")



def on_message(subtopic, subpayload):

    #print(subtopic)
    #print(subpayload)

    arr_subtopic = subtopic.split("/", 2)
    if len(arr_subtopic) != 3:
        return

    deviceid = arr_subtopic[1]
    topic = arr_subtopic[2]
    payload = subpayload.decode("utf-8")

    if topic == API_DOWNLOAD_SENSOR_DATA:
        try:
            thr = threading.Thread(target = download_device_sensor_data, args = (g_database_client, deviceid, topic, payload ))
            thr.start()
        except Exception as e:
            print("exception API_DOWNLOAD_SENSOR_DATA")
            print(e)
            return

def on_mqtt_message(client, userdata, msg):

    try:
        if download_config.CONFIG_DEBUG_SENSOR_READING:
            print("RCV: MQTT {} {}".format(msg.topic, msg.payload))
        on_message(msg.topic, msg.payload)
    except:
        return

def on_amqp_message(ch, method, properties, body):

    try:
        if download_config.CONFIG_DEBUG_SENSOR_READING:
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
    subtopic = "{}{}+{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_SEPARATOR, API_DOWNLOAD_SENSOR_DATA)
    g_messaging_client.subscribe(subtopic, subscribe=True, declare=True, consume_continuously=True)


    while g_messaging_client.is_connected():
        time.sleep(3)
        pass

    print("application exits!")
