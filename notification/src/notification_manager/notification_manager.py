from aws_config import config as aws_config
from notification_client import notification_client
from notification_client import notification_types
from notification_client import notification_models
from notification_config import config as notification_config
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
from s3_client import s3_client
import pycountry
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import (
    region_code_for_country_code,
    region_code_for_number,
)



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

g_messaging_client    = None
g_notification_client = None
g_database_client     = None
g_storage_client      = None
g_sms_country_points  = None



###################################################################################
# MQTT and AMQP default configurations
###################################################################################

CONFIG_DEVICE_ID                = "notification_manager"

CONFIG_USERNAME                 = notification_config.CONFIG_MQTT_DEFAULT_USER
CONFIG_PASSWORD                 = notification_config.CONFIG_MQTT_DEFAULT_PASS

if CONFIG_USE_ECC:
    CONFIG_TLS_CA               = "../cert_ecc/rootca.pem"
    CONFIG_TLS_CERT             = "../cert_ecc/notification_manager_cert.pem"
    CONFIG_TLS_PKEY             = "../cert_ecc/notification_manager_pkey.pem"
else:
    CONFIG_TLS_CA               = "../cert/rootca.pem"
    CONFIG_TLS_CERT             = "../cert/notification_manager_cert.pem"
    CONFIG_TLS_PKEY             = "../cert/notification_manager_pkey.pem"

CONFIG_HOST                     = "localhost"
CONFIG_MQTT_TLS_PORT            = 8883
CONFIG_AMQP_TLS_PORT            = 5671

CONFIG_PREPEND_REPLY_TOPIC      = "server"
CONFIG_SEPARATOR                = '/'

CONFIG_MODEL_EMAIL              = int(notification_config.CONFIG_USE_EMAIL_MODEL)
CONFIG_MODEL_SMS                = int(notification_config.CONFIG_USE_SMS_MODEL)
CONFIG_MODEL_PUSH_NOTIFICATION  = int(notification_config.CONFIG_USE_PUSH_NOTIFICATION_MODEL)


###################################################################################
# MENOS Notification
###################################################################################

CONFIG_MENOS_PREVENT_SPAMMING   = False
MENOS_MOBILE       = "mobile"
MENOS_EMAIL        = "email"
MENOS_NOTIFICATION = "notification"
MENOS_MODEM        = "modem"
MENOS_STORAGE      = "storage"
MENOS_DEFAULT      = "default"



print("MODEL_EMAIL {}".format(CONFIG_MODEL_EMAIL))
print("MODEL_SMS {}".format(CONFIG_MODEL_SMS))
print("MODEL_PUSH_NOTIFICATION {}".format(CONFIG_MODEL_PUSH_NOTIFICATION))


###################################################################################
# MQTT/AMQP callback functions
###################################################################################


def send_usage_notice(messaging_client, deviceid, menos_type, subscription, recipients):
    topic = "{}{}{}{}email{}send_usage_notice".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, deviceid, CONFIG_SEPARATOR, CONFIG_SEPARATOR)
    payload = { 
        "menos_type": menos_type, 
        "subscription": subscription, 
        "recipients": recipients 
    }
    messaging_client.publish(topic, json.dumps(payload), False)

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
        messaging_client.publish(topic, payload, debug=False)
        #print("\r\nSending message='{}' to recipient='{}' done.\r\n\r\n".format(message, recipient))
        send_notification_status(messaging_client, deviceid, "OK. message sent to {}.".format(recipient))
    except:
        send_notification_status(messaging_client, deviceid, "NG")
        print("PUBLISH FAILED!")
        return False
    return True

def send_notification_storage(messaging_client, deviceid, recipient, message, source, sensorname, date_time, condition, sensor):
    if sensor is None:
        contents = date_time + ": " + message + " - " + source.upper()
        if sensorname:
            contents += ":" + sensorname
        if condition:
            contents += " (" + condition + ")"
    else:
        contents = date_time + ": " + message + " - " + "LDS Bus " + sensor["port"] + ": " + sensor["name"]
        if sensorname:
            contents += ": " + sensorname
        if condition:
            contents += " (" + condition + ")"

    try:
        result = g_storage_client.append_to_file(recipient, deviceid, contents)
        if result:
            send_notification_status(messaging_client, deviceid, "OK. message sent to storage.")
            try:
                if source.startswith("uart"):
                    source_new = source
                    if sensorname:
                        source_new = "{}{}".format(source, sensorname)
                    notification = g_database_client.get_device_notification_by_deviceid(deviceid, source_new, None)
                    if notification:
                        if notification["endpoints"][MENOS_STORAGE]["recipients"] == "":
                            notification["endpoints"][MENOS_STORAGE]["recipients"] = result
                            g_database_client.update_device_notification_by_deviceid(deviceid, source_new, None, notification)
                else:
                    notification = g_database_client.get_device_notification_by_deviceid(deviceid, source[:-1], int(source[-1:]))
                    if notification:
                        if notification["endpoints"][MENOS_STORAGE]["recipients"] == "":
                            notification["endpoints"][MENOS_STORAGE]["recipients"] = result
                            g_database_client.update_device_notification_by_deviceid(deviceid, source[:-1], int(source[-1:]), notification)
            except:
                print("exception")
                pass
        else:
            send_notification_status(messaging_client, deviceid, "NG")
            return False, None
    except:
        send_notification_status(messaging_client, deviceid, "NG")
        return False, None
    return True, contents

def construct_message(deviceid, message, source, sensorname, date_time, condition, sensor):

    new_message = message

    # append condition string
    if condition is not None:
        new_message += "\r\n- condition triggered: " + condition

    # append devicename, source peripheral, sensorname
    devicename = g_database_client.get_devicename(deviceid)
    if devicename is None:
        return None
    from_source = ""
    if sensorname is None:
        source = source.upper()
        from_source += "- from {}:{}".format(devicename, source)
    else:
        from_source += "- from {}:LDS Bus {}:{}:{}".format(devicename, sensor["port"], sensor["name"], sensorname)
    new_message += "\r\n" + from_source

    # append timestamp on the message
    new_message += " " + date_time

    return new_message, date_time

def get_sms_details(phonenumber):
    pn = phonenumbers.parse(phonenumber)
    isocode = region_code_for_country_code(pn.country_code)
    country = pycountry.countries.get(alpha_2=isocode)
    try:
        networkcarrier = carrier.name_for_number(pn, "en")
    except:
        networkcarrier = None
    return country.name, isocode, networkcarrier


def check_cost(type, recipient=None, country=None, isocode=None, networkcarrier=None):
    if type == notification_types.SMS:
        for item in g_sms_country_points:
            if item["code"] == isocode:
                return int(item["points"])
    elif type == notification_types.EMAIL or type == notification_types.PUSH_NOTIFICATION:
        return 1
    return 0

def check_balance(username, deviceid, type, cost):
    subscription = g_database_client.get_subscription(deviceid)
    if subscription is None:
        return False, 0

    if type == notification_types.SMS:
        usage = int(subscription['current']['sms'])
        allowance = int(subscription['current']['plan']['sms'])

        print("{} {}/{} [{}]".format('sms', usage, allowance, cost))

        new_usage = usage + cost
        if usage >= allowance:
            return False, 0
        elif new_usage >= allowance:
            if subscription['current'].get('notice'):
                if subscription['current']['notice']['sms']:
                    return False, 0
            subscription['current']['sms'] = str(new_usage)

            # send notice regarding sms fully consumed
            recipients = []
            recipients.append(username)
            send_usage_notice(g_messaging_client, deviceid, 'sms', subscription, recipients)

            g_database_client.set_subscription_notice(deviceid, 'sms')

        return True, new_usage

    elif type == notification_types.EMAIL:
        usage = int(subscription['current']['email'])
        allowance = int(subscription['current']['plan']['email'])

        print("{} {}/{} [{}]".format('email', usage, allowance, cost))

        new_usage = usage + cost
        if new_usage > allowance:
            return False, 0
        elif new_usage == allowance:
            if subscription['current'].get('notice'):
                if subscription['current']['notice']['email']:
                    return False, 0
            subscription['current']['email'] = str(new_usage)

            # send notice regarding email fully consumed
            recipients = []
            recipients.append(username)
            send_usage_notice(g_messaging_client, deviceid, 'email', subscription, recipients)

            g_database_client.set_subscription_notice(deviceid, 'email')

        return True, new_usage

    elif type == notification_types.PUSH_NOTIFICATION:
        usage = int(subscription['current']['notification'])
        allowance = int(subscription['current']['plan']['notification'])

        print("{} {}/{} [{}]".format('notification', usage, allowance, cost))

        new_usage = usage + cost
        if new_usage > allowance:
            return False, 0
        elif new_usage == allowance:
            if subscription['current'].get('notice'):
                if subscription['current']['notice']['notification']:
                    return False, 0
            subscription['current']['notification'] = str(new_usage)

            # send notice regarding push notification fully consumed
            recipients = []
            recipients.append(username)
            send_usage_notice(g_messaging_client, deviceid, 'notification', subscription, recipients)

            g_database_client.set_subscription_notice(deviceid, 'notification')

        return True, new_usage

    else:
        return True, 0


    return False, 0

def update_balance(deviceid, type, new_usage):

    if type == notification_types.SMS:
        g_database_client.set_subscription_usage(deviceid, 'sms', new_usage)
    elif type == notification_types.EMAIL:
        g_database_client.set_subscription_usage(deviceid, 'email', new_usage)
    elif type == notification_types.PUSH_NOTIFICATION:
        g_database_client.set_subscription_usage(deviceid, 'notification', new_usage)


def notification_thread(username, messaging_client, deviceid, recipient, message, subject, type, options, source, sensor, payload, notification):

    number = None
    if not source.startswith("uart"):
        number = source[-1:]
        source = source[:-1]

    # generate information to append to the message
    timestamp = int(time.time())
    date_time = "[" + datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S") + " UTC]"
    condition = None
    if payload.get("condition"):
        condition = payload["condition"]
    sensorname = None
    if sensor is not None:
        sensorname = sensor["sensorname"]
    type_str = g_notification_client.get_notification_types_string(type)

    # append information to the message
    message_updated, date_time = construct_message(deviceid, message, source, sensorname, date_time, condition, sensor)
    if message_updated is None:
        send_notification_status(messaging_client, deviceid, "NG")
        return


    # send message
    if type == notification_types.DEVICE:
        #
        # Device
        #

        isgroup = False
        if notification:
            modem = notification["endpoints"]["modem"]
            if modem.get("isgroup") is not None:
                isgroup = modem["isgroup"]

        recipients = recipient.split(",")
        for x in range(len(recipients)):
            recipients[x] = recipients[x].strip()

        if isgroup == False:
            # send to all devices in the list
            for devicename_recipient in recipients:
                result = False
                deviceid_recipient = g_database_client.get_deviceid(username, devicename_recipient)
                if deviceid_recipient is not None:
                    result = send_notification_device(messaging_client, deviceid, deviceid_recipient, message_updated)
                    print("{}: {} [{} {}] {}".format(deviceid, type_str, len(deviceid_recipient), len(message_updated), result ))
                g_database_client.add_menos_transaction(username, deviceid, deviceid_recipient, message_updated, type_str, source.upper(), number, timestamp, condition, result)
        else:
            # send to all group members in the list
            for devicegroup_recipient in recipients:
                # get the group details
                devicegroup = g_database_client.get_devicegroup(username, devicegroup_recipient)
                if devicegroup:
                    # send to group members
                    for deviceid_recipient in devicegroup["devices"]:
                        result = send_notification_device(messaging_client, deviceid, deviceid_recipient, message_updated)
                        print("{}: {} [{} {}] {}".format(deviceid, type_str, len(deviceid_recipient), len(message_updated), result ))
                        g_database_client.add_menos_transaction(username, deviceid, deviceid_recipient, message_updated, type_str, source.upper(), number, timestamp, condition, result)

    elif type == notification_types.STORAGE:
        #
        # Storage
        #
        result, contents = send_notification_storage(messaging_client, deviceid, recipient, message, source, sensorname, date_time, condition, sensor)
        print("{}: {} [{}] {}".format(deviceid, type_str, len(contents), result ))

        g_database_client.add_menos_transaction(username, deviceid, recipient, message, type_str, source.upper(), number, timestamp, condition, result)

    elif type == notification_types.PUSH_NOTIFICATION:
        #
        # Notification (push notification)
        #
        if recipient.get("devicetoken") is None or recipient.get("service") is None:
            return
        devicetokens = recipient["devicetoken"]
        services = recipient["service"]

        for x in range(len(devicetokens)):

            # check push notification balance
            allow, new_usage = check_balance(username, deviceid, type, check_cost(type))
            if not allow:
                print("sending push notification not permitted, no more available balance.")
                send_notification_status(messaging_client, deviceid, "NG. no more available push notification balance.")
                return

            rec = {"devicetoken": devicetokens[x], "service": services[x]}
            try:
                response = g_notification_client.send_message(rec, message_updated, subject=subject, type=type)
            except:
                response = ""

            if response != "":
                result = response["ResponseMetadata"]["HTTPStatusCode"]==200
                send_notification_status(messaging_client, deviceid, "NG" if result == False else "OK. message sent to mobile phone/s.".format(rec))
            else:
                result = False
                send_notification_status(messaging_client, deviceid, "NG")

            recipient_label = "Android" if rec["service"] == "GCM" else "iOS"
            g_database_client.add_menos_transaction(username, deviceid, recipient_label, message, type_str, source, number, timestamp, condition, result)
            print("{} {} {}".format(deviceid, recipient_label, result))

            # update push notification balance
            if result:
                update_balance(deviceid, type, new_usage)

    elif type == notification_types.EMAIL:
        #
        # Email
        #
        recipients = recipient.split(",")
        for x in range(len(recipients)):
            recipients[x] = recipients[x].strip()

        for recipient in recipients:

            # check email balance
            allow, new_usage = check_balance(username, deviceid, type, check_cost(type))
            if not allow:
                print("sending email not permitted, no more available balance.")
                send_notification_status(messaging_client, deviceid, "NG. no more available email balance.")
                return

            try:
                response = g_notification_client.send_message(recipient, message_updated, subject=subject, type=type)
            except:
                response = ""

            if response != "":
                result = response["ResponseMetadata"]["HTTPStatusCode"]==200
                send_notification_status(messaging_client, deviceid, "NG" if result == False else "OK. message sent to {}.".format(recipient))
            else:
                result = False
                send_notification_status(messaging_client, deviceid, "NG")

            g_database_client.add_menos_transaction(username, deviceid, recipient, message, type_str, source.upper(), number, timestamp, condition, result)
            print("{} {} {}".format(deviceid, recipient, result))

            # update push notification balance
            if result:
                update_balance(deviceid, type, new_usage)

    elif type == notification_types.SMS:
        #
        # Mobile (sms)
        #
        recipients = recipient.split(",")
        for x in range(len(recipients)):
            recipients[x] = recipients[x].strip()

        for recipient in recipients:
            country, isocode, networkcarrier = get_sms_details(recipient)

            # check sms balance
            cost = check_cost(type, recipient, country, isocode, networkcarrier)
            allow, new_usage = check_balance(username, deviceid, type, cost)
            if not allow:
                print("sending sms not permitted, no more available balance.")
                send_notification_status(messaging_client, deviceid, "NG. no more available sms balance.")
                return

            try:
                response = g_notification_client.send_message(recipient, message_updated, subject=subject, type=type)
            except:
                response = ""

            if response != "":
                result = response["ResponseMetadata"]["HTTPStatusCode"]==200
                send_notification_status(messaging_client, deviceid, "NG" if result == False else "OK. message sent to {}.".format(recipient))
            else:
                result = False
                send_notification_status(messaging_client, deviceid, "NG")

            g_database_client.add_menos_transaction(username, deviceid, recipient, message, type_str, source.upper(), number, timestamp, condition, result)
            print("{} {} {} [{}-{}-{}] {}".format(deviceid, recipient, result, country, isocode, networkcarrier, cost))

            # update push notification balance
            if result:
                update_balance(deviceid, type, new_usage)

    #print(g_database_client.get_menos_transaction(deviceid))
    #g_database_client.delete_menos_transaction(deviceid)


def send_notification_mobile_threaded(username, messaging_client, deviceid, recipient, message, source, sensor, payload, notification):
    #print("mobile")
    if recipient[0] != '+':
        recipient = "+{}".format(recipient)
    #print("recipient={} message={}".format(recipient, message))
    thr = threading.Thread(target = notification_thread, args = (username, messaging_client, deviceid, recipient, message, None, notification_types.SMS, -1, source, sensor, payload, notification, ))
    thr.start()
    return thr

def send_notification_email_threaded(username, messaging_client, deviceid, recipient, message, source, sensor, payload, notification):
    #print("email")
    #print("recipient={} message={}".format(recipient, message))
    thr = threading.Thread(target = notification_thread, args = (username, messaging_client, deviceid, recipient, message, aws_config.CONFIG_PINPOINT_EMAIL_SUBJECT, notification_types.EMAIL, -1, source, sensor, payload, notification, ))
    thr.start()
    return thr

def send_notification_notification_threaded(username, messaging_client, deviceid, recipient, message, source, sensor, payload, notification):
    #print("push_notification")
    #print("recipient={} message={}".format(recipient, message))
    thr = threading.Thread(target = notification_thread, args = (username, messaging_client, deviceid, recipient, message, aws_config.CONFIG_PINPOINT_PUSH_NOTIFICATION_SUBJECT, notification_types.PUSH_NOTIFICATION, -1, source, sensor, payload, notification, ))
    thr.start()
    return thr

def send_notification_modem_threaded(username, messaging_client, deviceid, recipient, message, source, sensor, payload, notification):
    #print("modem")
    #print("recipient={} message={}".format(recipient, message))
    thr = threading.Thread(target = notification_thread, args = (username, messaging_client, deviceid, recipient, message, None, notification_types.DEVICE, -1, source, sensor, payload, notification, ))
    thr.start()
    return thr

def send_notification_storage_threaded(username, messaging_client, deviceid, recipient, message, source, sensor, payload, notification):
    #print("modem")
    #print("recipient={} message={}".format(recipient, message))
    thr = threading.Thread(target = notification_thread, args = (username, messaging_client, deviceid, recipient, message, None, notification_types.STORAGE, -1, source, sensor, payload, notification, ))
    thr.start()
    return thr

def send_notification_default_threaded(username, messaging_client, deviceid, notification, message, source, sensor, payload):
    #print("default")
    if notification is not None:
        if CONFIG_MENOS_PREVENT_SPAMMING:
            # Prevent spamming for unreasonable threshold values
            # Temporarily enable EMAIL only for AT+D for I2C/ADC/1WIRE/TPROBE
            if source.startswith("uart") or source.startswith("gpio"):
                if notification["endpoints"][MENOS_MOBILE]["enable"] == True:
                    recipients = notification["endpoints"][MENOS_MOBILE]["recipients"]
                    thr = send_notification_mobile_threaded(username, messaging_client, deviceid, recipients, message, source, sensor, payload, notification)
                    thr.join()
                if notification["endpoints"][MENOS_EMAIL]["enable"] == True:
                    recipients = notification["endpoints"][MENOS_EMAIL]["recipients"]
                    thr = send_notification_email_threaded(username, messaging_client, deviceid, recipients, message, source, sensor, payload, notification)
                    thr.join()
                if notification["endpoints"][MENOS_NOTIFICATION]["enable"] == True:
                    recipients = g_database_client.get_mobile_device_token_by_deviceid(deviceid)
                    thr = send_notification_notification_threaded(username, messaging_client, deviceid, recipients, message, source, sensor, payload, notification)
                    thr.join()
                if notification["endpoints"][MENOS_MODEM]["enable"] == True:
                    recipients = notification["endpoints"][MENOS_MODEM]["recipients"]
                    thr = send_notification_modem_threaded(username, messaging_client, deviceid, recipients, message, source, sensor, payload, notification)
                    thr.join()
                if notification["endpoints"][MENOS_STORAGE]["enable"] == True:
                    thr = send_notification_storage_threaded(username, messaging_client, deviceid, username, message, source, sensor, payload, notification)
                    thr.join()
            else:
                # TODO: temporarily send only email for AT+D for I2C/ADC/1WIRE/TPROBE
                if notification["endpoints"][MENOS_EMAIL]["enable"] == True:
                    recipients = notification["endpoints"][MENOS_EMAIL]["recipients"]
                    thr = send_notification_email_threaded(username, messaging_client, deviceid, recipients, message, source, sensor, payload, notification)
                    thr.join()
        else:
            if notification["endpoints"][MENOS_MOBILE]["enable"] == True:
                recipients = notification["endpoints"][MENOS_MOBILE]["recipients"]
                thr = send_notification_mobile_threaded(username, messaging_client, deviceid, recipients, message, source, sensor, payload, notification)
                thr.join()
            if notification["endpoints"][MENOS_EMAIL]["enable"] == True:
                recipients = notification["endpoints"][MENOS_EMAIL]["recipients"]
                thr = send_notification_email_threaded(username, messaging_client, deviceid, recipients, message, source, sensor, payload, notification)
                thr.join()
            if notification["endpoints"][MENOS_NOTIFICATION]["enable"] == True:
                recipients = g_database_client.get_mobile_device_token_by_deviceid(deviceid)
                thr = send_notification_notification_threaded(username, messaging_client, deviceid, recipients, message, source, sensor, payload, notification)
                thr.join()
            if notification["endpoints"][MENOS_MODEM]["enable"] == True:
                recipients = notification["endpoints"][MENOS_MODEM]["recipients"]
                thr = send_notification_modem_threaded(username, messaging_client, deviceid, recipients, message, source, sensor, payload, notification)
                thr.join()
            if notification["endpoints"][MENOS_STORAGE]["enable"] == True:
                thr = send_notification_storage_threaded(username, messaging_client, deviceid, username, message, source, sensor, payload, notification)
                thr.join()
    else:
        send_notification_status(messaging_client, deviceid, "NG. database entry not found.")

def send_notification_menos(username, messaging_client, deviceid, payload, notification, menos, source, sensor):
    if menos == MENOS_MOBILE:
        send_notification_mobile_threaded(username, messaging_client, deviceid, payload["recipient"], payload["message"], source, sensor, payload, notification)
    elif menos == MENOS_EMAIL:
        send_notification_email_threaded(username, messaging_client, deviceid, payload["recipient"], payload["message"], source, sensor, payload, notification)
    elif menos == MENOS_NOTIFICATION:
        send_notification_notification_threaded(username, messaging_client, deviceid, payload["recipient"], payload["message"], source, sensor, payload, notification)
    elif menos == MENOS_MODEM:
        send_notification_modem_threaded(username, messaging_client, deviceid, payload["recipient"], payload["message"], source, sensor, payload, notification)
    elif menos == MENOS_STORAGE:
        send_notification_storage_threaded(username, messaging_client, deviceid, username, payload["message"], source, sensor, payload, notification)
    elif menos == MENOS_DEFAULT:
        send_notification_default_threaded(username, messaging_client, deviceid, notification, payload["message"], source, sensor, payload)
    else:
        print("UNSUPPORTED {}".format(menos))


def on_message(subtopic, subpayload):

    #print(subtopic)
    notification = None
    topicarr = subtopic.split("/")
    try:
        if len(topicarr) >= 5:
            deviceid = topicarr[1]
            source = topicarr[3]
            menos = topicarr[4]
            payload = json.loads(subpayload)
            sensor = None

            # check if deviceid exists
            username = g_database_client.get_username(deviceid)
            if username is None:
                send_notification_status(g_messaging_client, deviceid, "NG. deviceid is invalid.")
                return
            print(username)

            # recipient or message is not provided, get notification info from database
            if not payload.get("recipient") or not payload.get("message"):
                if source.startswith("i2c"):
                    if len(topicarr) == 5:
                        send_notification_status(g_messaging_client, deviceid, "NG. address is not included in the topic.")
                        return
                    address = int(topicarr[5])
                    # find sensorname
                    peripheral = source[:len(source)-1]
                    number = source[len(source)-1:]
                    sensor = g_database_client.get_sensor_by_deviceid(deviceid, peripheral, number, address)
                    if sensor is None:
                        send_notification_status(g_messaging_client, deviceid, "NG. could not find sensor.")
                        return
                    source_new = "{}{}".format(source, sensor["sensorname"])
                    notification = g_database_client.get_device_notification_by_deviceid(deviceid, source_new)
                elif source.startswith("adc") or source.startswith("1wire") or source.startswith("tprobe"):
                    # find sensorname
                    peripheral = source[:len(source)-1]
                    number = source[len(source)-1:]
                    sensor = g_database_client.get_sensor_by_deviceid(deviceid, peripheral, number, None)
                    if sensor is None:
                        send_notification_status(g_messaging_client, deviceid, "NG. could not find sensor.")
                        return
                    source_new = "{}{}".format(source, sensor["sensorname"])
                    notification = g_database_client.get_device_notification_by_deviceid(deviceid, source_new)
                elif source.startswith("uart"):
                    notification = g_database_client.get_device_notification_by_deviceid(deviceid, source, None)
                else:
                    #print("xxxxx {} {}".format(source[:-1], int(source[-1:]) ))
                    sensor = g_database_client.get_sensor_by_deviceid(deviceid, source[:-1], source[-1:], None)
                    notification = g_database_client.get_device_notification_by_deviceid(deviceid, source[:-1], int(source[-1:]) )
                #print(notification)

            # recipient is not provided, process the notification info to get the recipient
            if not payload.get("recipient"):
                #print("no recipient")
                if notification is not None:
                    #if menos == "modem":
                    #    #print("modem")
                    #    #print(notification["endpoints"][menos])
                    #    if notification["endpoints"][menos]["enable"] == True:
                    #        payload["recipient"] = g_database_client.get_deviceid(username, notification["endpoints"][menos]["recipients"])
                    #    else:
                    #        send_notification_status(g_messaging_client, deviceid, "NG. {} recipient is not enabled.".format(menos))
                    #        return
                    if menos == "notification":
                        if notification["endpoints"][menos]["enable"] == True:
                            # read from database
                            payload["recipient"] = g_database_client.get_mobile_device_token_by_deviceid(deviceid)
                            #print(payload["recipient"])
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

            # message is not provided, process the notification info to get the message
            if not payload.get("message"):
                #print("no message")
                if notification is not None:
                    if source == "uart":
                        payload["message"] = notification["messages"][0]["message"]
                        if len(payload["message"]) == 0:
                            send_notification_status(g_messaging_client, deviceid, "NG. message is empty.")
                            return
                        #print("new message: {}".format(payload["message"]))
                    else:
                        # if source is gpio or i2c, there can be 2 messages, message on activation and message on deactivation
                        # check the activate parameter
                        index = 0
                        if payload.get("activate") is None:
                            send_notification_status(g_messaging_client, deviceid, "NG. activate parameter is not present.")
                            return
                        if payload["activate"] == 0:
                            index = 1
                        if notification["messages"][index]["enable"]:
                            payload["message"] = notification["messages"][index]["message"]
                        else:
                            # message on activation/deactivation is disabled
                            if payload["activate"]:
                                send_notification_status(g_messaging_client, deviceid, "NG. message on activation is disabled.")
                            else:
                                send_notification_status(g_messaging_client, deviceid, "NG. message on deactivation is disabled.")
                            return
                        if len(payload["message"]) == 0:
                            send_notification_status(g_messaging_client, deviceid, "NG. message is empty.")
                            return
                else:
                    send_notification_status(g_messaging_client, deviceid, "NG. database entry not found.")
                    return

            send_notification_menos(username, g_messaging_client, deviceid, payload, notification, menos, source, sensor)

        #elif len(topicarr) == 3:
        #    print("path 2")
        #    # get device id
        #    deviceid = topicarr[1]

        #    payload = json.loads(subpayload)
        #    recipient = payload["recipient"]
        #    message = payload["message"]

        #    # get options value
        #    options = -1
        #    if payload.get("options") is not None:
        #        options = int(payload["options"])

        #    is_email = True if recipient.find("@")!=-1 else False
        #    is_mobile = True if recipient[0] == '+' else False
        #    subject = aws_config.CONFIG_PINPOINT_EMAIL_SUBJECT if is_email else None
        #    type = notification_types.UNKNOWN
        #    if is_email:
        #        type = notification_types.EMAIL
        #    elif is_mobile:
        #        type = notification_types.SMS
        #    else:
        #        type = notification_types.DEVICE

        #    thr = threading.Thread(target = notification_thread, args = (g_messaging_client, deviceid, recipient, message, subject, type, options, ))
        #    thr.start()
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
    #print("USE_USERNAME={}".format(args.USE_USERNAME))
    #print("USE_PASSWORD={}".format(args.USE_PASSWORD))
    print("")


    # Initialize S3 client
    g_storage_client = s3_client()
    g_sms_country_points = g_storage_client.get_sms_country_points_list()


    # Initialize MongoDB
    g_database_client = database_client(host=CONFIG_DBHOST)
    g_database_client.initialize()


    # Initialize Notification client (Pinpoint, SNS, Twilio or Nexmo)
    model_email             = CONFIG_MODEL_EMAIL
    model_sms               = CONFIG_MODEL_SMS
    model_push_notification    = CONFIG_MODEL_PUSH_NOTIFICATION
    g_notification_client = notification_client(model_email, model_sms, model_push_notification)
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
    #subtopic = "{}{}+{}trigger_notification".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_SEPARATOR)
    #g_messaging_client.subscribe(subtopic, subscribe=True, declare=True, consume_continuously=True)
    subtopic = "{}{}+{}trigger_notification{}#".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_SEPARATOR, CONFIG_SEPARATOR)
    g_messaging_client.subscribe(subtopic, subscribe=True, declare=True, consume_continuously=True)


    while g_messaging_client.is_connected():
        time.sleep(3)
        pass

    print("application exits!")
