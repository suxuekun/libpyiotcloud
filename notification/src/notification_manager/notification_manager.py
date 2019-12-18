from aws_config import config as aws_config
from notification_client import notification_client
from notification_client import notification_types
from notification_client import notification_models
from notification_config import config as notification_config
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
CONFIG_DBHOST = notification_config.CONFIG_MONGODB_HOST
###################################################################################



###################################################################################
# global variables
###################################################################################

g_messaging_client = None
g_notification_client = None
g_database_client = None



###################################################################################
# MQTT and AMQP default configurations
###################################################################################

CONFIG_DEVICE_ID            = "notification_manager"

CONFIG_USERNAME             = notification_config.CONFIG_MQTT_DEFAULT_USER
CONFIG_PASSWORD             = notification_config.CONFIG_MQTT_DEFAULT_PASS

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

CONFIG_MODEL_EMAIL          = int(notification_config.CONFIG_USE_EMAIL_MODEL)
CONFIG_MODEL_SMS            = int(notification_config.CONFIG_USE_SMS_MODEL)
print("MODEL_EMAIL {}".format(CONFIG_MODEL_EMAIL))
print("MODEL_SMS {}".format(CONFIG_MODEL_SMS))


###################################################################################
# MQTT/AMQP callback functions
###################################################################################


def send_notification_status(messaging_client, deviceid, status):
    topic = "{}{}status_notification".format(deviceid, CONFIG_SEPARATOR)
    payload = { "status": status }
    messaging_client.publish(topic, json.dumps(payload), False)

def send_notification_device(messaging_client, deviceid, recipient, message):
    topic = "{}{}recv_notification".format(recipient, CONFIG_SEPARATOR)
    #print("topic={}".format(topic))
    payload = {}
    payload["recipient"] = recipient
    payload["message"] = message
    payload["sender"] = deviceid
    payload = json.dumps(payload)
    #print("payload={}".format(payload))
    try:
        messaging_client.publish(topic, payload)
        #print("\r\nSending message='{}' to recipient='{}' done.\r\n\r\n".format(message, recipient))
        send_notification_status(messaging_client, deviceid, "OK. message sent to {}.".format(recipient))
    except:
        send_notification_status(messaging_client, deviceid, "NG")
        print("PUBLISH FAILED!")

def notification_thread(messaging_client, deviceid, recipient, message, subject, type, options):

    if type == notification_types.DEVICE:
        # Send to another device
        send_notification_device(messaging_client, deviceid, recipient, message)
    else:
        # Send to SMS or email
        if options >= 0:
            # With options parameter
            print("OPTIONS = {}".format(options))

            if options == 1:
                options = 0
            new_client = notification_client(notification_models.PINPOINT, options)
            new_client.initialize()
            try:
                response = new_client.send_message(recipient, message, subject=subject, type=type)
            except:
                send_notification_status(messaging_client, deviceid, "NG")
                return
        else:
            # No options parameter
            try:
                response = g_notification_client.send_message(recipient, message, subject=subject, type=type)
            except:
                send_notification_status(messaging_client, deviceid, "NG")
                return

        # Display result
        if notification_config.CONFIG_DEBUG_NOTIFICATION:
            try:
                print("\r\nSending message='{}' to recipient='{}' done. {} {}\r\n\r\n".format(
                    message, recipient,
                    response["ResponseMetadata"]["HTTPStatusCode"]==200, 
                    response["MessageResponse"]["Result"][recipient]["StatusCode"]==200))
                send_notification_status(messaging_client, deviceid, "OK. message sent to {}.".format(recipient))
            except:
                try:
                    print("\r\nSending message='{}' to recipient='{}' done. {}\r\n\r\n".format(
                        message, recipient,
                        response["ResponseMetadata"]["HTTPStatusCode"]==200))
                    send_notification_status(messaging_client, deviceid, "OK. message sent to {}.".format(recipient))
                except:
                    print("\r\nSending message='{}' to recipient='{}' done.\r\n\r\n".format(
                        message, recipient))
        else:
            typeStr = "SMS  " if type == notification_types.SMS else "Email"
            try:
                res = response["ResponseMetadata"]["HTTPStatusCode"]==200 and response["MessageResponse"]["Result"][recipient]["StatusCode"]==200
                print("{}: {} options={} [{} {}] {}".format(deviceid, typeStr, options, len(recipient), len(message), res))
                if res == True:
                    send_notification_status(messaging_client, deviceid, "OK. message sent to {}.".format(recipient))
                else:
                    send_notification_status(messaging_client, deviceid, "NG")
            except:
                try:
                    res = response["ResponseMetadata"]["HTTPStatusCode"]==200
                    print("{}: {} options={} [{} {}] {}".format(deviceid, typeStr, options, len(recipient), len(message), res))
                    if res == True:
                        send_notification_status(messaging_client, deviceid, "OK. message sent to {}.".format(recipient))
                    else:
                        send_notification_status(messaging_client, deviceid, "NG")
                except:
                    print("{}: {} options={} [{} {}] True".format(deviceid, typeStr, options, len(recipient), len(message) ))

def send_notification_mobile_threaded(messaging_client, deviceid, recipient, message):
    #print("mobile")
    if recipient[0] != '+':
        recipient = "+{}".format(recipient)
    #print("recipient={} message={}".format(recipient, message))
    thr = threading.Thread(target = notification_thread, args = (messaging_client, deviceid, recipient, message, None, notification_types.SMS, -1, ))
    thr.start()
    return thr

def send_notification_email_threaded(messaging_client, deviceid, recipient, message):
    #print("email")
    #print("recipient={} message={}".format(recipient, message))
    thr = threading.Thread(target = notification_thread, args = (messaging_client, deviceid, recipient, message, aws_config.CONFIG_PINPOINT_EMAIL_SUBJECT, notification_types.EMAIL, -1, ))
    thr.start()
    return thr

def send_notification_modem_threaded(messaging_client, deviceid, recipient, message):
    #print("modem")
    #print("recipient={} message={}".format(recipient, message))
    thr = threading.Thread(target = notification_thread, args = (messaging_client, deviceid, recipient, message, None, notification_types.DEVICE, -1, ))
    thr.start()
    return thr

def send_notification_default_threaded(messaging_client, deviceid, notification, message):
    #print("default")
    if notification is not None:
        if notification["endpoints"]["mobile"]["enable"] == True:
            thr = send_notification_mobile_threaded(messaging_client, deviceid, notification["endpoints"]["mobile"]["recipients"], message)
            thr.join()
        if notification["endpoints"]["email"]["enable"] == True:
            thr = send_notification_email_threaded(messaging_client, deviceid, notification["endpoints"]["email"]["recipients"], message)
            thr.join()
        if notification["endpoints"]["modem"]["enable"] == True:
            thr = send_notification_modem_threaded(messaging_client, deviceid, notification["endpoints"]["modem"]["recipients_id"], message)
            thr.join()
    else:
        send_notification_status(messaging_client, deviceid, "NG. database entry not found.")

def send_notification_menos(messaging_client, deviceid, payload, notification, menos):
    if menos == "mobile":
        send_notification_mobile_threaded(messaging_client, deviceid, payload["recipient"], payload["message"])
    elif menos == "email":
        send_notification_email_threaded(messaging_client, deviceid, payload["recipient"], payload["message"])
    elif menos == "notification":
        # TODO
        pass
    elif menos == "modem":
        send_notification_modem_threaded(messaging_client, deviceid, payload["recipient"], payload["message"])
    elif menos == "storage":
        # TODO
        pass
    elif menos == "default":
        send_notification_default_threaded(messaging_client, deviceid, notification, payload["message"])
    else:
        print("UNSUPPORTED {}".format(menos))


def on_message(subtopic, subpayload):

    #print(subtopic)
    notification = None
    topicarr = subtopic.split("/")
    try:
        if len(topicarr) == 5:
            deviceid = topicarr[1]
            source = topicarr[3]
            menos = topicarr[4]
            payload = json.loads(subpayload)
            if not payload.get("recipient") or not payload.get("message"):
                notification = g_database_client.get_device_notification_by_deviceid(deviceid, source)
                #print(notification)
            if not payload.get("recipient"):
                #print("no recipient")
                if notification is not None:
                    if menos == "modem":
                        if notification["endpoints"][menos]["enable"] == True:
                            payload["recipient"] = notification["endpoints"][menos]["recipients_id"]
                        else:
                            send_notification_status(g_messaging_client, deviceid, "NG. {} recipient is not enabled.".format(menos))
                            return
                    elif menos != "default":
                        if notification["endpoints"][menos]["enable"] == True:
                            payload["recipient"] = notification["endpoints"][menos]["recipients"]
                        else:
                            send_notification_status(g_messaging_client, deviceid, "NG. {} recipient is not enabled.".format(menos))
                            return
                else:
                    send_notification_status(g_messaging_client, deviceid, "NG. database entry not found.")
                    return
            if not payload.get("message"):
                #print("no message")
                if notification is not None:
                    payload["message"] = notification["messages"][0]["message"]
                    if len(payload["message"]) == 0:
                        send_notification_status(g_messaging_client, deviceid, "NG. message is empty.")
                        return
                    #print("new message: {}".format(payload["message"]))
                else:
                    send_notification_status(g_messaging_client, deviceid, "NG. database entry not found.")
                    return

            send_notification_menos(g_messaging_client, deviceid, payload, notification, menos)

        elif len(topicarr) == 3:
            # get device id
            deviceid = topicarr[1]

            payload = json.loads(subpayload)
            recipient = payload["recipient"]
            message = payload["message"]

            # get options value
            options = -1
            if payload.get("options") is not None:
                options = int(payload["options"])

            is_email = True if recipient.find("@")!=-1 else False
            is_mobile = True if recipient[0] == '+' else False
            subject = aws_config.CONFIG_PINPOINT_EMAIL_SUBJECT if is_email else None
            type = notification_types.UNKNOWN
            if is_email:
                type = notification_types.EMAIL
            elif is_mobile:
                type = notification_types.SMS
            else:
                type = notification_types.DEVICE

            thr = threading.Thread(target = notification_thread, args = (g_messaging_client, deviceid, recipient, message, subject, type, options, ))
            thr.start()
    except Exception as e:
        print("exception")
        print(e)
        return
    return


def on_mqtt_message(client, userdata, msg):

    try:
        if notification_config.CONFIG_DEBUG_NOTIFICATION:
            print("RCV: MQTT {} {}".format(msg.topic, msg.payload))
        on_message(msg.topic, msg.payload)
    except:
        return

def on_amqp_message(ch, method, properties, body):

    try:
        if notification_config.CONFIG_DEBUG_NOTIFICATION:
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
    model_email = CONFIG_MODEL_EMAIL
    model_sms   = CONFIG_MODEL_SMS
    g_notification_client = notification_client(model_email, model_sms)
    try:
        g_notification_client.initialize()
    except:
        print("Could not initialize notification model! exception!")


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
    subtopic2 = "{}{}+{}trigger_notification{}#".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_SEPARATOR, CONFIG_SEPARATOR)
    g_messaging_client.subscribe(subtopic2, subscribe=True, declare=True, consume_continuously=True)


    while g_messaging_client.is_connected():
        pass

    print("application exits!")
