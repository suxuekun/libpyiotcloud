from notification_config import config as notification_config
from notification_client import notification_client
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
g_notification_client = None
g_gpio_values = {}


###################################################################################
# MQTT and AMQP default configurations
###################################################################################

CONFIG_DEVICE_ID            = "notification_manager"

CONFIG_USERNAME             = None
CONFIG_PASSWORD             = None

if CONFIG_USE_ECC:
    CONFIG_TLS_CA           = "../cert_ecc/rootca.pem"
    CONFIG_TLS_CERT         = "../cert_ecc/notification_manager_cert.pem"
    CONFIG_TLS_PKEY         = "../cert_ecc/notification_manager_pkey.pem"
else:
    CONFIG_TLS_CA           = "../cert/rootca.pem"
    CONFIG_TLS_CERT         = "../cert/notification_manager_cert.pem"
    CONFIG_TLS_PKEY         = "../cert/notification_manager_pkey.pem"

CONFIG_HOST                 = "localhost"
CONFIG_MQTT_TLS_PORT        = 8883
CONFIG_AMQP_TLS_PORT        = 5671

CONFIG_PREPEND_REPLY_TOPIC  = "server"
CONFIG_SEPARATOR            = '/'



###################################################################################
# MQTT/AMQP callback functions
###################################################################################


def notification_thread(recipient, message, subject):

    try:
        response = g_notification_client.send_message(recipient, message, subject=subject)
    except:
        return

    try:
        print("\r\nSending message='{}' to recipient='{}' done. {} {}\r\n\r\n".format(
            message, recipient,
            response["ResponseMetadata"]["HTTPStatusCode"]==200, 
            response["MessageResponse"]["Result"][recipient]["StatusCode"]==200))
    except:
        print("\r\nSending message='{}' to recipient='{}' done. {}\r\n\r\n".format(
            message, recipient,
            response["ResponseMetadata"]["HTTPStatusCode"]==200))


def on_message(subtopic, subpayload):

    try:
        payload = json.loads(subpayload)
        recipient = payload["recipient"]
        message = payload["message"]

        is_email = True if recipient.find("@")!=-1 else False
        subject = notification_config.CONFIG_PINPOINT_EMAIL_SUBJECT if is_email else None

        thr = threading.Thread(target = notification_thread, args = (recipient, message, subject, ))
        thr.start()
    except:
        return


def on_mqtt_message(client, userdata, msg):

    try:
        print("RCV: MQTT {} {}".format(msg.topic, msg.payload))
        on_message(msg.topic, msg.payload)
    except:
        return

def on_amqp_message(ch, method, properties, body):

    try:
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


    # Initialize Notification client (Pinpoint or SNS)
    g_notification_client = notification_client()
    g_notification_client.initialize()


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
    subtopic = "{}{}+{}trigger_notification".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_SEPARATOR)
    g_messaging_client.subscribe(subtopic, subscribe=True, declare=True, consume_continuously=True)


    while g_messaging_client.is_connected():
        pass

    print("application exits!")
