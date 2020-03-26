from aws_config import config as aws_config
from invoice_client import invoice_client
from invoice_config import config as invoice_config
from web_server_database import database_client
from datetime import datetime
import json
import time
import datetime
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
CONFIG_DBHOST = invoice_config.CONFIG_MONGODB_HOST
###################################################################################



###################################################################################
# global variables
###################################################################################

g_messaging_client = None
g_invoice_client = None
g_database_client = None



###################################################################################
# MQTT and AMQP default configurations
###################################################################################

CONFIG_DEVICE_ID                = "invoice_manager"

CONFIG_USERNAME                 = invoice_config.CONFIG_MQTT_DEFAULT_USER
CONFIG_PASSWORD                 = invoice_config.CONFIG_MQTT_DEFAULT_PASS

if CONFIG_USE_ECC:
    CONFIG_TLS_CA               = "../cert_ecc/rootca.pem"
    CONFIG_TLS_CERT             = "../cert_ecc/invoice_manager_cert.pem"
    CONFIG_TLS_PKEY             = "../cert_ecc/invoice_manager_pkey.pem"
else:
    CONFIG_TLS_CA               = "../cert/rootca.pem"
    CONFIG_TLS_CERT             = "../cert/invoice_manager_cert.pem"
    CONFIG_TLS_PKEY             = "../cert/invoice_manager_pkey.pem"

CONFIG_HOST                     = "localhost"
CONFIG_MQTT_TLS_PORT            = 8883
CONFIG_AMQP_TLS_PORT            = 5671

CONFIG_PREPEND_REPLY_TOPIC      = "server"
CONFIG_SEPARATOR                = '/'

CONFIG_MODEL_EMAIL              = int(invoice_config.CONFIG_USE_EMAIL_MODEL)
CONFIG_EMAIL_SUBJECT            = aws_config.CONFIG_PINPOINT_EMAIL_SUBJECT

API_SEND_INVOICE                = "send_invoice"


print("MODEL_EMAIL {}".format(CONFIG_MODEL_EMAIL))



###################################################################################
# MQTT/AMQP callback functions
###################################################################################


def construct_message(name, payment):

    message =  "Hi {},\r\n\r\n\r\n".format(name)
    message += "A Paypal payment of {} USD for {} credits was processed successfully.\r\n".format(payment["amount"], payment["value"])
    message += "To confirm your Paypal transaction, visit the Paypal website and check the transaction ID: {}.\r\n\r\n".format(payment["id"])

    message += "If unauthorised, please contact customer support.\r\n\r\n"
    message += "\r\nBest Regards,\r\n"
    message += "Bridgetek Pte. Ltd.\r\n"
    return message


def get_name(database_client, username):

    name = None
    info = database_client.find_user_ex(username)
    if info:
        # handle no family name
        if 'given_name' in info:
            name = info['given_name']
        if 'family_name' in info:
            if info['family_name'] != "NONE":
                if 'identities' in info:
                    identity = json.loads(info['identities'].strip(']['))
                    if identity['providerName'] != 'LoginWithAmazon':
                        name += " " + info['family_name']
                else:
                    name += " " + info['family_name']
    return name, info


def send_invoice(database_client, paymentid, topic, payload):

    try:
        payment = database_client.get_paypal_payment_by_paymentid(paymentid)
        #print(payment)
        name, info = get_name(database_client, payment["username"])
        recipient = info["email"]
        message = construct_message(name, payment)
        response = g_invoice_client.send_message(recipient, message, subject=CONFIG_EMAIL_SUBJECT)
    except Exception as e:
        print(e)
        return

    try:
        result = response["ResponseMetadata"]["HTTPStatusCode"]==200 and response["MessageResponse"]["Result"][recipient]["StatusCode"]==200
        print("{}: {} {}={} [{}]".format(paymentid, payment["username"], payment["value"], payment["amount"], result))
    except Exception as e:
        print(e)


def on_message(subtopic, subpayload):

    #print(subtopic)
    #print(subpayload)

    arr_subtopic = subtopic.split(CONFIG_SEPARATOR, 2)
    if len(arr_subtopic) != 3:
        return

    paymentid = arr_subtopic[1]
    topic = arr_subtopic[2]
    payload = subpayload.decode("utf-8")

    if topic == API_SEND_INVOICE:
        try:
            thr = threading.Thread(target = send_invoice, args = (g_database_client, paymentid, topic, payload ))
            thr.start()
        except Exception as e:
            print("exception API_SEND_INVOICE")
            print(e)
            return
    return


def on_mqtt_message(client, userdata, msg):

    try:
        if invoice_config.CONFIG_DEBUG_INVOICE:
            print("RCV: MQTT {} {}".format(msg.topic, msg.payload))
        on_message(msg.topic, msg.payload)
    except:
        return

def on_amqp_message(ch, method, properties, body):

    try:
        if invoice_config.CONFIG_DEBUG_INVOICE:
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


    # Initialize Notification client (Pinpoint, SNS, Twilio or Nexmo)
    g_invoice_client = invoice_client()
    try:
        g_invoice_client.initialize()
    except:
        print("Could not initialize invoice model! exception!")


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
    subtopic = "{}{}+{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_SEPARATOR, API_SEND_INVOICE)
    g_messaging_client.subscribe(subtopic, subscribe=True, declare=True, consume_continuously=True)


    while g_messaging_client.is_connected():
        time.sleep(3)
        pass

    print("application exits!")
