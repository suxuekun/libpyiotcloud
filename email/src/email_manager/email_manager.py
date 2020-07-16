from aws_config import config as aws_config
from email_client import email_client
from email_config import config as email_config
from email_templates import email_templates
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
CONFIG_DBHOST = email_config.CONFIG_MONGODB_HOST
###################################################################################



###################################################################################
# global variables
###################################################################################

g_messaging_client = None
g_email_client = None
g_database_client = None
g_email_templates = None



###################################################################################
# MQTT and AMQP default configurations
###################################################################################

CONFIG_DEVICE_ID                = "email_manager"

CONFIG_USERNAME                 = email_config.CONFIG_MQTT_DEFAULT_USER
CONFIG_PASSWORD                 = email_config.CONFIG_MQTT_DEFAULT_PASS

if CONFIG_USE_ECC:
    CONFIG_TLS_CA               = "../cert_ecc/rootca.pem"
    CONFIG_TLS_CERT             = "../cert_ecc/email_manager_cert.pem"
    CONFIG_TLS_PKEY             = "../cert_ecc/email_manager_pkey.pem"
else:
    CONFIG_TLS_CA               = "../cert/rootca.pem"
    CONFIG_TLS_CERT             = "../cert/email_manager_cert.pem"
    CONFIG_TLS_PKEY             = "../cert/email_manager_pkey.pem"

CONFIG_HOST                     = "localhost"
CONFIG_MQTT_TLS_PORT            = 8883
CONFIG_AMQP_TLS_PORT            = 5671

CONFIG_PREPEND_REPLY_TOPIC      = "server"
CONFIG_SEPARATOR                = '/'
CONFIG_WILDCARD                 = '#'
CONFIG_EMAIL                    = "email"

CONFIG_USE_APIURL                 = aws_config.CONFIG_USE_APIURL

CONFIG_MODEL_EMAIL                        = int(email_config.CONFIG_USE_EMAIL_MODEL)
CONFIG_EMAIL_SUBJECT_RECEIPT              = aws_config.CONFIG_PINPOINT_EMAIL_SUBJECT_RECEIPT
CONFIG_EMAIL_SUBJECT_ORGANIZATION         = aws_config.CONFIG_PINPOINT_EMAIL_SUBJECT_ORGANIZATION
CONFIG_EMAIL_SUBJECT_USAGENOTICE          = aws_config.CONFIG_PINPOINT_EMAIL_SUBJECT_USAGENOTICE
CONFIG_EMAIL_SUBJECT_SENSORDATADL         = aws_config.CONFIG_PINPOINT_EMAIL_SUBJECT_SENSORDATADL
CONFIG_EMAIL_SUBJECT_DEVICEREGISTRATION   = aws_config.CONFIG_PINPOINT_EMAIL_SUBJECT_DEVICEREGISTRATION
CONFIG_EMAIL_SUBJECT_DEVICEUNREGISTRATION = aws_config.CONFIG_PINPOINT_EMAIL_SUBJECT_DEVICEUNREGISTRATION
CONFIG_EMAIL_SUBJECT_ACCOUNTCREATION      = aws_config.CONFIG_PINPOINT_EMAIL_SUBJECT_ACCOUNTCREATION
CONFIG_EMAIL_SUBJECT_ACCOUNTDELETION      = aws_config.CONFIG_PINPOINT_EMAIL_SUBJECT_ACCOUNTDELETION

API_SEND_RECEIPT                  = "send_invoice"
API_SEND_INVITATION_ORGANIZATION  = "send_invitation_organization"
API_SEND_USAGE_NOTICE             = "send_usage_notice"
API_SEND_SENSORDATA_DOWNLOAD_LINK = "send_sensordata_download_link"
API_SEND_DEVICE_REGISTRATION      = "send_device_registration"
API_SEND_DEVICE_UNREGISTRATION    = "send_device_unregistration"
API_SEND_ACCOUNT_CREATION         = "send_account_creation"
API_SEND_ACCOUNT_DELETION         = "send_account_deletion"



###################################################################################
# Invoice/Receipt
###################################################################################

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
        message = g_email_templates.construct_invoice_message(name, payment)
        response = g_email_client.send_message(recipient, message, subject=CONFIG_EMAIL_SUBJECT_RECEIPT)
    except Exception as e:
        print(e)
        return

    try:
        result = response["ResponseMetadata"]["HTTPStatusCode"]==200 and response["MessageResponse"]["Result"][recipient]["StatusCode"]==200
        print("RECEIPT {}: {} {}={} [{}]".format(paymentid, payment["username"], payment["value"], payment["amount"], result))
    except Exception as e:
        print(e)


###################################################################################
# Invitation organization
###################################################################################

def send_invitation_organization(database_client, orgname, topic, payload):

    payload = json.loads(payload)
    message = g_email_templates.construct_invitation_organization_message(orgname, payload["owner"])
    for recipient in payload["recipients"]:
        try:
            response = g_email_client.send_message(recipient, message, subject=CONFIG_EMAIL_SUBJECT_ORGANIZATION)
        except Exception as e:
            print(e)
            return

        try:
            result = response["ResponseMetadata"]["HTTPStatusCode"]==200 and response["MessageResponse"]["Result"][recipient]["StatusCode"]==200
            print("INVITATION {}: {} [{}]".format(orgname, recipient, result))
        except Exception as e:
            print(e)


###################################################################################
# Sensor data download link
###################################################################################

def send_sensordata_download_link(database_client, deviceid, topic, payload):

    payload = json.loads(payload)
    message = g_email_templates.construct_sensordata_download_link_message(payload["name"], payload["url"], payload["devicename"], deviceid)
    for recipient in payload["recipients"]:
        try:
            response = g_email_client.send_message(recipient, message, subject=CONFIG_EMAIL_SUBJECT_SENSORDATADL)
        except Exception as e:
            print(e)
            return

        try:
            result = response["ResponseMetadata"]["HTTPStatusCode"]==200 and response["MessageResponse"]["Result"][recipient]["StatusCode"]==200
            print("SENSORDATADL {}: {} [{}]".format(deviceid, recipient, result))
        except Exception as e:
            print(e)


###################################################################################
# Usage notice
###################################################################################

def send_usage_notice(database_client, deviceid, topic, payload):

    payload = json.loads(payload)
    message = g_email_templates.construct_usage_notice_message(deviceid, payload["menos_type"], payload["subscription"])
    for recipient in payload["recipients"]:
        try:
            response = g_email_client.send_message(recipient, message, subject=CONFIG_EMAIL_SUBJECT_USAGENOTICE)
        except Exception as e:
            print(e)
            return

        try:
            result = response["ResponseMetadata"]["HTTPStatusCode"]==200 and response["MessageResponse"]["Result"][recipient]["StatusCode"]==200
            print("USAGENOTICE {}: {} [{}]".format(deviceid, recipient, result))
        except Exception as e:
            print(e)


###################################################################################
# Device registration
###################################################################################

def send_device_registration(database_client, deviceid, topic, payload):

    payload = json.loads(payload)
    message = g_email_templates.construct_device_registration_message(deviceid, payload["serialnumber"])
    for recipient in payload["recipients"]:
        try:
            response = g_email_client.send_message(recipient, message, subject=CONFIG_EMAIL_SUBJECT_DEVICEREGISTRATION)
        except Exception as e:
            print(e)
            return

        try:
            result = response["ResponseMetadata"]["HTTPStatusCode"]==200 and response["MessageResponse"]["Result"][recipient]["StatusCode"]==200
            print("DEVICEREGISTRATION {}: {} [{}]".format(deviceid, recipient, result))
        except Exception as e:
            print(e)

###################################################################################
# Device unregistration
###################################################################################

def send_device_unregistration(database_client, deviceid, topic, payload):

    payload = json.loads(payload)
    message = g_email_templates.construct_device_unregistration_message(deviceid, payload["serialnumber"])
    for recipient in payload["recipients"]:
        try:
            response = g_email_client.send_message(recipient, message, subject=CONFIG_EMAIL_SUBJECT_DEVICEUNREGISTRATION)
        except Exception as e:
            print(e)
            return

        try:
            result = response["ResponseMetadata"]["HTTPStatusCode"]==200 and response["MessageResponse"]["Result"][recipient]["StatusCode"]==200
            print("DEVICEUNREGISTRATION {}: {} [{}]".format(deviceid, recipient, result))
        except Exception as e:
            print(e)


###################################################################################
# Account creation
###################################################################################

def send_account_creation(database_client, name, topic, payload):

    payload = json.loads(payload)
    message = g_email_templates.construct_account_creation_message()
    for recipient in payload["recipients"]:
        try:
            response = g_email_client.send_message(recipient, message, subject=CONFIG_EMAIL_SUBJECT_ACCOUNTCREATION)
        except Exception as e:
            print(e)
            return

        try:
            result = response["ResponseMetadata"]["HTTPStatusCode"]==200 and response["MessageResponse"]["Result"][recipient]["StatusCode"]==200
            print("ACCOUNTCREATION {}: {} [{}]".format(name, recipient, result))
        except Exception as e:
            print(e)

###################################################################################
# Account deletion
###################################################################################

def send_account_deletion(database_client, name, topic, payload):

    payload = json.loads(payload)
    message = g_email_templates.construct_account_deletion_message()
    for recipient in payload["recipients"]:
        try:
            response = g_email_client.send_message(recipient, message, subject=CONFIG_EMAIL_SUBJECT_ACCOUNTDELETION)
        except Exception as e:
            print(e)
            return

        try:
            result = response["ResponseMetadata"]["HTTPStatusCode"]==200 and response["MessageResponse"]["Result"][recipient]["StatusCode"]==200
            print("ACCOUNTDELETION {}: {} [{}]".format(name, recipient, result))
        except Exception as e:
            print(e)



###################################################################################
# MQTT subscription handling
###################################################################################

email_types = [
    API_SEND_RECEIPT, 
    API_SEND_INVITATION_ORGANIZATION, 
    API_SEND_USAGE_NOTICE, 
    API_SEND_SENSORDATA_DOWNLOAD_LINK, 
    API_SEND_DEVICE_REGISTRATION, 
    API_SEND_DEVICE_UNREGISTRATION,
    API_SEND_ACCOUNT_CREATION,
    API_SEND_ACCOUNT_DELETION,
]

email_handler = [
    send_invoice,
    send_invitation_organization,
    send_usage_notice,
    send_sensordata_download_link,
    send_device_registration,
    send_device_unregistration,
    send_account_creation,
    send_account_deletion,
]

def on_message(subtopic, subpayload):

    #print(subtopic)
    #print(subpayload)

    params = 4
    arr_subtopic = subtopic.split(CONFIG_SEPARATOR, params-1)
    if len(arr_subtopic) != params:
        return

    payload = subpayload.decode("utf-8")
    topic = arr_subtopic[2]
    subtopic = arr_subtopic[3]


    if len(email_handler) != len(email_types):
        print("email_handler != email_types")
        return 

    if topic == CONFIG_EMAIL:
        for x in range(len(email_types)):
            if subtopic == email_types[x]:
                try:
                    thr = threading.Thread(target = email_handler[x], args = (g_database_client, arr_subtopic[1], subtopic, payload ))
                    thr.start()
                except Exception as e:
                    print("exception {}".format(email_types[x]))
                    print(e)
                    return


def on_mqtt_message(client, userdata, msg):

    try:
        if email_config.CONFIG_DEBUG_INVOICE:
            print("RCV: MQTT {} {}".format(msg.topic, msg.payload))
        on_message(msg.topic, msg.payload)
    except:
        return

def on_amqp_message(ch, method, properties, body):

    try:
        if email_config.CONFIG_DEBUG_INVOICE:
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


    # Initialize Notification client (Pinpoint, SNS, Twilio or Nexmo)
    g_email_client = email_client()
    try:
        g_email_client.initialize()
    except:
        print("Could not initialize invoice model! exception!")


    # Initialize email templates
    g_email_templates = email_templates()


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
    time.sleep(1)


    # Subscribe to messages sent for this device
    subtopic  = "{}{}+{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_SEPARATOR, CONFIG_EMAIL, CONFIG_SEPARATOR, CONFIG_WILDCARD)
    g_messaging_client.subscribe(subtopic, subscribe=True, declare=True, consume_continuously=True)


    while g_messaging_client.is_connected():
        time.sleep(3)
        pass

    print("application exits!")
