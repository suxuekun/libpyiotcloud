import json
import time
import datetime
import netifaces
import argparse
import sys
import os
import psutil # for dynamic app restart
import threading
import random
import queue
from messaging_client import messaging_client # common module from parent directory
import http.client
import ssl
import base64
import binascii
import logging
from logging.handlers import RotatingFileHandler
from logging import handlers
import jwt # now using pyjwt instead of jose
import device_client
import math



###################################################################################
CONFIG_USE_ECC = True
# Enable to use AMQP for webserver-to-messagebroker communication
# Disable to use MQTT for webserver-to-messagebroker communication
CONFIG_USE_AMQP = False
###################################################################################

###################################################################################
# global variables
###################################################################################

# query backend to compute device password
CONFIG_QUERY_BACKEND_TO_COMPUTE_DEVICE_PASSWORD = True

# add timestamp to sensor data
CONFIG_ADD_SENSOR_DATA_TIMESTAMP = True

# add timestamp to logs in console and file
CONFIG_ADD_LOG_FILE_TIMESTAMP = True
CONFIG_ADD_LOG_CONSOLE_TIMESTAMP = False
CONFIG_LOG_FILE_MAX_SIZE = 1048576*10 # 10MB
CONFIG_LOG_FILE_MAX_BACKUP = 10

# scan sensor for automatic registration
CONFIG_SCAN_SENSORS_AT_BOOTUP = True

# ota firmware update
CONFIG_OTA_AT_BOOTUP = True
# FT900 is advised to use HTTPS to download the firmware (if possible).
#   If not possible (due to memory constraints), then can use MQTTS.
#   When using MQTTS to download the firmware, the firmware is downloaded by chunks.
#   Since its not possible to add binary to a JSON packet, the binary chunks is Base64-encoded.
CONFIG_OTA_DOWNLOAD_FIRMWARE_VIA_MQTTS = False
# Below is the performance when using the device simulator.
# LIVE
# via HTTPS: 4 seconds
# via MQTTS:
#   chunk size: 8192 -  18 seconds
#   chunk size: 4096 -  33 seconds
#   chunk size: 2048 -  55 seconds
#   chunk size: 1024 - 123 seconds
#   chunk size:  512 - 237 seconds
# LOCALHOST
# via HTTPS: 4 seconds
# via MQTTS:
#   chunk size: 8192 -   5 seconds
#   chunk size: 4096 -   7 seconds
#   chunk size: 2048 -  15 seconds
#   chunk size: 1024 -  27 seconds
#   chunk size:  512 -  53 seconds
#   chunk size:  256 -  95 seconds
#   chunk size:  128 - 162 seconds
CONFIG_OTA_DOWNLOAD_FIRMWARE_MQTTS_CHUNK_SIZE = 8192

# device configuration on bootup
CONFIG_REQUEST_CONFIGURATION = True
CONFIG_REQUEST_CONFIGURATION_DEBUG = False
CONFIG_DELETE_CONFIGURATION = False
CONFIG_AUTO_ENABLE_CONFIGURATION = True
CONFIG_SAVE_CONFIGURATION_TO_FILE = True
CONFIG_LOAD_CONFIGURATION_FROM_FILE = False

# notification thread for triggering notifications (demo 4 testing)
CONFIG_SEND_NOTIFICATION_PERIODICALLY = False
CONFIG_SEND_NOTIFICATION_PERIOD = 3600 # 1 hour

# timer thread for publishing sensor data
g_timer_thread_timeout = 5
g_timer_thread = None
g_timer_thread_stop = None

# heartbeat thread for publishing heartbeat
g_heartbeat_thread_timeout = 60
g_heartbeat_thread = None
g_heartbeat_thread_stop = None

g_input_thread = None

g_download_thread_timeout = 5
g_download_thread = None
g_download_thread_stop = None

g_messaging_client = None
g_device_client = None

# FIRMWARE VERSION
g_firmware_version_MAJOR = 0
g_firmware_version_MINOR = 1
g_firmware_version = (g_firmware_version_MAJOR*100 + g_firmware_version_MINOR)
g_firmware_version_STR = "{}.{}".format(g_firmware_version_MAJOR, g_firmware_version_MINOR)

# STATUS
DEVICE_STATUS_STARTING    = 0
DEVICE_STATUS_RUNNING     = 1
DEVICE_STATUS_RESTART     = 2
DEVICE_STATUS_RESTARTING  = 3
DEVICE_STATUS_STOP        = 4
DEVICE_STATUS_STOPPING    = 5
DEVICE_STATUS_STOPPED     = 6
DEVICE_STATUS_START       = 7
DEVICE_STATUS_CONFIGURING = 8
g_device_status = DEVICE_STATUS_RUNNING
g_device_statuses = ["starting", "running", "restart", "restarting", "stop", "stopping", "stopped", "start", "configuring"]

# SETTINGS
g_device_settings = { 'sensorrate': g_timer_thread_timeout }

# UART
g_uart_properties = { 'baudrate': 7, 'parity': 0, 'flowcontrol': 0, 'stopbits': 0, 'databits': 1 }
g_uart_enabled = 1

g_uart_baudrate = ["110", "150", "300", "1200", "2400", "4800", "9600", "19200", "31250", "38400", "57600", "115200", "230400", "460800", "921600", "1000000"]
g_uart_parity  = ["None", "Odd", "Even"]
g_uart_flowcontrol = ["None", "Rts/Cts", "Xon/Xoff"]
g_uart_stopbits = ["1", "2"]
g_uart_databits = ["7", "8"]

# GPIO
g_gpio_properties = [
    { 'direction': 0, 'mode': 0, 'alert': 0, 'alertperiod':   0,   'polarity': 0, 'width': 0, 'mark': 0, 'space': 0, 'count': 0 },
    { 'direction': 0, 'mode': 3, 'alert': 1, 'alertperiod':  60,   'polarity': 0, 'width': 0, 'mark': 0, 'space': 0, 'count': 0 },
    { 'direction': 1, 'mode': 0, 'alert': 0, 'alertperiod':   0,   'polarity': 0, 'width': 0, 'mark': 0, 'space': 0, 'count': 0 },
    { 'direction': 1, 'mode': 2, 'alert': 1, 'alertperiod': 120,   'polarity': 1, 'width': 0, 'mark': 1, 'space': 2, 'count': 0 } ]
g_gpio_voltage = 1
g_gpio_voltages = ['3.3 V', '5 V']
g_gpio_enabled = [0, 0, 0, 0]
g_gpio_status = [0, 1, 0, 1]


g_device_classes = ["speaker", "display", "light", "potentiometer", "temperature", "humidity", "anemometer", "battery", "fluid"]

# I2C
g_i2c_properties = [
    {
        '0': { 'enabled': 0, 'class': 255, 'attributes': {} },
    },
    {
        '0': { 'enabled': 0, 'class': 255, 'attributes': {} },
    },
    {
        '0': { 'enabled': 0, 'class': 255, 'attributes': {} },
    },
    {
        '0': { 'enabled': 0, 'class': 255, 'attributes': {} },
    }
]
g_i2c_properties_enabled_output = [{},{},{},{}]

# ADC
g_adc_voltage = 1
g_adc_voltages = ["-5/+5V Range", "-10/+10V Range", "0/10V Range"]
g_adc_properties = [
    { 'enabled': 0, 'class': 255, 'attributes': {} },
    { 'enabled': 0, 'class': 255, 'attributes': {} },
]

# 1WIRE
g_1wire_properties = [
    { 'enabled': 0, 'class': 255, 'attributes': {} }
]

# TPROBE
g_tprobe_properties = [
    { 'enabled': 0, 'class': 255, 'attributes': {} }
]

# GW DESCRIPTOR
# Dynamically created based on gateway UUID
g_gateway_descriptor = {}

# LDSU DESCRIPTORS
# UID is dynamically created based on gateway UUID + running number to ensure unique UID across device simulators
g_ldsu_descriptors = []

# LDSU DEVICE Properties
# Dynamically created based on g_ldsu_descriptors
g_ldsu_properties = {}


start_timeX = 0



###################################################################################
# APIs
###################################################################################

# device status
API_GET_STATUS                   = "get_status"
API_SET_STATUS                   = "set_status"

# device settings
API_GET_SETTINGS                 = "get_settings"
API_SET_SETTINGS                 = "set_settings"

# uart
API_GET_UARTS                    = "get_uarts"
API_GET_UART_PROPERTIES          = "get_uart_prop"
API_SET_UART_PROPERTIES          = "set_uart_prop"
API_ENABLE_UART                  = "enable_uart"

# gpio
API_GET_GPIOS                    = "get_gpios"
API_GET_GPIO_PROPERTIES          = "get_gpio_prop"
API_SET_GPIO_PROPERTIES          = "set_gpio_prop"
API_ENABLE_GPIO                  = "enable_gpio"
API_GET_GPIO_VOLTAGE             = "get_gpio_voltage"
API_SET_GPIO_VOLTAGE             = "set_gpio_voltage"

# i2c
API_GET_I2C_DEVICES              = "get_i2c_devs"
API_ENABLE_I2C_DEVICE            = "enable_i2c_dev"
API_GET_I2C_DEVICE_PROPERTIES    = "get_i2c_dev_prop"
API_SET_I2C_DEVICE_PROPERTIES    = "set_i2c_dev_prop"

# adc
API_GET_ADC_DEVICES              = "get_adc_devs"
API_ENABLE_ADC_DEVICE            = "enable_adc_dev"
API_GET_ADC_DEVICE_PROPERTIES    = "get_adc_dev_prop"
API_SET_ADC_DEVICE_PROPERTIES    = "set_adc_dev_prop"

API_GET_ADC_VOLTAGE              = "get_adc_voltage"
API_SET_ADC_VOLTAGE              = "set_adc_voltage"

# 1wire
API_GET_1WIRE_DEVICES            = "get_1wire_devs"
API_ENABLE_1WIRE_DEVICE          = "enable_1wire_dev"
API_GET_1WIRE_DEVICE_PROPERTIES  = "get_1wire_dev_prop"
API_SET_1WIRE_DEVICE_PROPERTIES  = "set_1wire_dev_prop"

# tprobe
API_GET_TPROBE_DEVICES           = "get_tprobe_devs"
API_ENABLE_TPROBE_DEVICE         = "enable_tprobe_dev"
API_GET_TPROBE_DEVICE_PROPERTIES = "get_tprobe_dev_prop"
API_SET_TPROBE_DEVICE_PROPERTIES = "set_tprobe_dev_prop"

# i2c/adc/1wire/tprobe
API_GET_PERIPHERAL_DEVICES       = "get_devs"

# notification
API_RECEIVE_NOTIFICATION         = "recv_notification"
API_TRIGGER_NOTIFICATION         = "trigger_notification"
API_STATUS_NOTIFICATION          = "status_notification"

# sensor reading
API_RECEIVE_SENSOR_READING       = "rcv_sensor_reading"
API_REQUEST_SENSOR_READING       = "req_sensor_reading"
API_PUBLISH_SENSOR_READING       = "pub_sensor_reading"

# heartbeat
API_PUBLISH_HEARTBEAT            = "pub_heartbeat"

# configuration
API_REQUEST_CONFIGURATION        = "req_configuration"
API_RECEIVE_CONFIGURATION        = "rcv_configuration"
API_DELETE_CONFIGURATION         = "del_configuration"
API_SET_CONFIGURATION            = "set_configuration"

# ota firmware upgrade
API_UPGRADE_FIRMWARE             = "beg_ota"
API_UPGRADE_FIRMWARE_COMPLETION  = "end_ota"
API_REQUEST_FIRMWARE             = "req_firmware"
API_RECEIVE_FIRMWARE             = "rcv_firmware"
API_REQUEST_OTASTATUS            = "req_otastatus"
API_REQUEST_TIME                 = "req_time"
API_RECEIVE_TIME                 = "rcv_time"

# sensor registration 
API_SET_REGISTRATION             = "set_registration"

# descriptor
API_GET_DESCRIPTOR               = "get_descriptor"
API_SET_DESCRIPTOR               = "set_descriptor"

# lds bus
API_SET_LDSU_DESCS               = "set_ldsu_descs"
API_GET_LDSU_DESCS               = "get_ldsu_descs"
API_IDENTIFY_LDSU                = "identify_ldsu"

# ldsu
API_GET_LDSU_DEVICES             = "get_ldsu_devs"
API_ENABLE_LDSU_DEVICE           = "enable_ldsu_dev"
API_GET_LDSU_DEVICE_PROPERTIES   = "get_ldsu_dev_prop"
API_SET_LDSU_DEVICE_PROPERTIES   = "set_ldsu_dev_prop"



###################################################################################
# MQTT and AMQP default configurations
###################################################################################

CONFIG_DEVICE_ID            = ""

CONFIG_USERNAME             = None
CONFIG_PASSWORD             = None
CONFIG_TLS_CA               = "../cert_ecc/rootca.pem"
CONFIG_TLS_CERT             = "../cert_ecc/ft900device1_cert.pem"
CONFIG_TLS_PKEY             = "../cert_ecc/ft900device1_pkey.pem"

CONFIG_HOST                 = "localhost"
CONFIG_MQTT_TLS_PORT        = 8883
CONFIG_AMQP_TLS_PORT        = 5671

CONFIG_PREPEND_REPLY_TOPIC  = "server"
CONFIG_SEPARATOR            = '/'

CONFIG_HTTP_HOST            = "localhost"
CONFIG_HTTP_TLS_PORT        = 443
CONFIG_HTTP_TIMEOUT         = 10

CONFIG_DEVICE_SECRETKEY     = ''
CONFIG_DEVICE_ID            = ''
CONFIG_DEVICE_SERIAL        = ''
CONFIG_DEVICE_MACADD        = ''



###################################################################################
# Logging
###################################################################################

printf = None

def setup_logging(filename):
    global printf

    # initialize logger
    log = logging.getLogger('')
    log.setLevel(logging.DEBUG)
    if CONFIG_ADD_LOG_CONSOLE_TIMESTAMP or CONFIG_ADD_LOG_FILE_TIMESTAMP:
        format = logging.Formatter("[%(asctime)s] %(message)s", "%Y-%m-%d %H:%M:%S")

    # log to console
    ch = logging.StreamHandler(sys.stdout)
    if CONFIG_ADD_LOG_CONSOLE_TIMESTAMP:
        ch.setFormatter(format)
    log.addHandler(ch)

    # log to file
    fh = handlers.RotatingFileHandler(filename, maxBytes=CONFIG_LOG_FILE_MAX_SIZE, backupCount=CONFIG_LOG_FILE_MAX_BACKUP)
    if CONFIG_ADD_LOG_FILE_TIMESTAMP:
        fh.setFormatter(format)
    log.addHandler(fh)

    # set printf
    printf = logging.debug


###################################################################################
# API handling
###################################################################################

def printf_json(json_object, label=None):
    json_formatted_str = json.dumps(json_object, indent=2)
    if label is None:
        #printf(json_formatted_str)
        lines = json_formatted_str.split("\n")
        for line in lines:
            printf(line)
    else:
        printf(label)
        printf("")
        printf(json_formatted_str)

def publish(topic, payload, debug=True):
    payload = json.dumps(payload)
    g_messaging_client.publish(topic, payload, debug)

def generate_pubtopic(subtopic):
    return CONFIG_PREPEND_REPLY_TOPIC + CONFIG_SEPARATOR + subtopic

def setClassAttributes(device_class, class_attributes):
    attributes = None
    if class_attributes.get("number"):
        class_attributes.pop("number")
    if class_attributes.get("class"):
        class_attributes.pop("class")
    if class_attributes.get("address"):
        class_attributes.pop("address")
    # handle subclasses
    if class_attributes.get("subclass"):
        class_attributes.pop("subclass")
    if class_attributes.get("source"):
        class_attributes.pop("source")
    attributes = class_attributes
    return attributes

def reset_local_configurations():
    global g_uart_properties, g_gpio_properties
    global g_i2c_properties, g_i2c_properties_enabled_output
    global g_adc_properties, g_1wire_properties

    # UART
    g_uart_properties = { 'baudrate': 7, 'parity': 0, 'flowcontrol': 0, 'stopbits': 0, 'databits': 1 }

    # GPIO
    g_gpio_properties = [
        { 'direction': 0, 'mode': 0, 'alert': 0, 'alertperiod':   0,   'polarity': 0, 'width': 0, 'mark': 0, 'space': 0, 'count': 0 },
        { 'direction': 0, 'mode': 3, 'alert': 1, 'alertperiod':  60,   'polarity': 0, 'width': 0, 'mark': 0, 'space': 0, 'count': 0 },
        { 'direction': 1, 'mode': 0, 'alert': 0, 'alertperiod':   0,   'polarity': 0, 'width': 0, 'mark': 0, 'space': 0, 'count': 0 },
        { 'direction': 1, 'mode': 2, 'alert': 1, 'alertperiod': 120,   'polarity': 1, 'width': 0, 'mark': 1, 'space': 2, 'count': 0 } ]

    # I2C
    g_i2c_properties = [
        {
            '0': { 'enabled': 0, 'class': 255, 'attributes': {} },
        },
        {
            '0': { 'enabled': 0, 'class': 255, 'attributes': {} },
        },
        {
            '0': { 'enabled': 0, 'class': 255, 'attributes': {} },
        },
        {
            '0': { 'enabled': 0, 'class': 255, 'attributes': {} },
        }
    ]
    g_i2c_properties_enabled_output = [{},{},{},{}]

    # ADC
    g_adc_properties = [
        { 'enabled': 0, 'class': 255, 'attributes': {} },
        { 'enabled': 0, 'class': 255, 'attributes': {} },
    ]

    # 1WIRE
    g_1wire_properties = [
        { 'enabled': 0, 'class': 255, 'attributes': {} }
    ]

    # TPROBE
    g_tprobe_properties = [
        { 'enabled': 0, 'class': 255, 'attributes': {} }
    ]


def get_sensors_descriptors(obj, prv):
    descriptor = None
    for sensor in g_sensors:
        if obj == sensor["OBJ"] and float(prv) == float(sensor["VER"]):
            return sensor["SNS"]
    return None


def handle_api(api, subtopic, subpayload):
    global g_device_status
    global g_uart_properties, g_uart_enabled
    global g_gpio_properties, g_gpio_enabled, g_gpio_voltage, g_gpio_status
    global g_i2c_properties
    global g_adc_voltage
    global g_device_settings
    global g_download_thread, g_download_thread_stop



    ####################################################
    # STATUS
    ####################################################
    if api == API_GET_STATUS:
        topic = generate_pubtopic(subtopic)
        payload = {}
        payload["value"] = { "status": g_device_status, "version": g_firmware_version_STR }
        publish(topic, payload)

    elif api == API_SET_STATUS:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        status = subpayload["status"]
        if status == DEVICE_STATUS_RESTART:
            if g_device_status != DEVICE_STATUS_RESTARTING:
                g_device_status = DEVICE_STATUS_RESTARTING
                printf(g_device_statuses[g_device_status])
        elif status == DEVICE_STATUS_STOP:
            if g_device_status != DEVICE_STATUS_STOPPING and g_device_status != DEVICE_STATUS_STOPPED:
                g_device_status = DEVICE_STATUS_STOPPING
                printf(g_device_statuses[g_device_status])
        elif status == DEVICE_STATUS_START:
            if g_device_status != DEVICE_STATUS_STARTING and g_device_status != DEVICE_STATUS_RUNNING:
                g_device_status = DEVICE_STATUS_STARTING
                printf(g_device_statuses[g_device_status])

        payload = {}
        payload["value"] = {"status": g_device_status}
        publish(topic, payload)


    ####################################################
    # SENSOR READING
    ####################################################
    elif api == API_RECEIVE_SENSOR_READING:
        global start_timeX
        #printf(time.time())
        printf(time.time()-start_timeX)

        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)


        # if requested with API_REQUEST_SENSOR_READING which is already obsoleted
        if subpayload.get("source"):
            source = subpayload["source"]
            printf("{}{}:{} {}".format(source["peripheral"], source["number"], source["address"], g_device_classes[source["class"]]))
            #printf(subpayload["sensors"])

            if source["peripheral"] == "I2C":
                device_class = g_device_classes[source["class"]]
                x = source["number"]-1
                if device_class == "light":
                    for y in g_i2c_properties[x]:
                        if int(y) == source["address"]:
                            if g_i2c_properties[x][y]["attributes"]["color"]["usage"] == 0: 
                                # RGB as color
                                prop = g_i2c_properties[x][y]["attributes"]["color"]["single"]
                                index = 0
                                if prop["endpoint"] == 1:
                                    value = int(subpayload["sensors"][index]["value"])
                                    scaled_value = int(value * 0xFFFFFF / 255)
                                    printf("COLOR = {} scaled {} ({})".format(value, scaled_value, hex(scaled_value).upper()))
                            elif g_i2c_properties[x][y]["attributes"]["color"]["usage"] == 1:
                                # RGB as component
                                prop = g_i2c_properties[x][y]["attributes"]["color"]["individual"]
                                index = 0
                                if prop["red"]["endpoint"] == 1:
                                    value = int(subpayload["sensors"][index]["value"])
                                    printf("RED   : {} ({})".format(value, hex(value).upper()))
                                    index += 1
                                if prop["green"]["endpoint"] == 1:
                                    value = int(subpayload["sensors"][index]["value"])
                                    printf("GREEN : {} ({})".format(value, hex(value).upper()))
                                    index += 1
                                if prop["blue"]["endpoint"] == 1:
                                    value = int(subpayload["sensors"][index]["value"])
                                    printf("BLUE  : {} ({})".format(value, hex(value).upper()))
                                    index += 1
                            printf("")
                            break
                elif device_class == "display":
                    for y in g_i2c_properties[x]:
                        if int(y) == source["address"]:
                            index = 0
                            value = int(subpayload["sensors"][index]["value"])
                            if g_i2c_properties[x][y]["attributes"]["format"] == 0:
                                printf("HEX = {} ({})".format(hex(value).upper(), value))
                            elif g_i2c_properties[x][y]["attributes"]["format"] == 1:
                                printf("INT = {} ({})".format(value, hex(value).upper()))
                            printf("")
                            break
        else:
            found = False
            devicename = subpayload["sensors"][0]["devicename"]
            peripheral = subpayload["sensors"][0]["peripheral"]
            sensorname = subpayload["sensors"][0]["sensorname"]
            attribute = subpayload["sensors"][0]["attribute"]
            value = subpayload["sensors"][0]["value"]

            # all enabled output sensors are copied to g_i2c_properties_enabled_output during API_ENABLE_I2C_DEVICE
            for x in range(len(g_i2c_properties_enabled_output)):
                for y in g_i2c_properties_enabled_output[x]:
                    if g_i2c_properties_enabled_output[x][y]["enabled"] == 1:
                        if g_i2c_properties_enabled_output[x][y]["class"] <= 2:
                            device_class = g_device_classes[g_i2c_properties_enabled_output[x][y]["class"]]
                            if device_class == "light":
                                # if light class
                                if g_i2c_properties_enabled_output[x][y]["attributes"]["color"]["usage"] == 0:
                                    single = g_i2c_properties_enabled_output[x][y]["attributes"]["color"]["single"]
                                    if single["endpoint"] == 1:
                                        hardware = single["hardware"]
                                        if hardware["devicename"] == devicename and hardware["peripheral"] == peripheral and hardware["sensorname"] == sensorname and hardware["attribute"] == attribute:
                                            printf("color = {} ({})".format(value, hex(value).upper()))
                                            printf("")
                                            g_i2c_properties_enabled_output[x][y]["value"] = value
                                            found = True
                                            break
                                else:
                                    individual = g_i2c_properties_enabled_output[x][y]["attributes"]["color"]["individual"]
                                    if individual["red"]["endpoint"] == 1:
                                        hardware = individual["red"]["hardware"]
                                        if hardware["devicename"] == devicename and hardware["peripheral"] == peripheral and hardware["sensorname"] == sensorname and hardware["attribute"] == attribute:
                                            printf("red = {} ({})".format(value, hex(value).upper()))
                                            g_i2c_properties_enabled_output[x][y]["value"] &= 0x00FFFF
                                            g_i2c_properties_enabled_output[x][y]["value"] |= ((value & 0xFF) << 16)
                                            printf("color = {} ({})".format(g_i2c_properties_enabled_output[x][y]["value"], hex(g_i2c_properties_enabled_output[x][y]["value"]).upper()))
                                            printf("")
                                            found = True
                                            break
                                    if individual["green"]["endpoint"] == 1:
                                        hardware = individual["green"]["hardware"]
                                        if hardware["devicename"] == devicename and hardware["peripheral"] == peripheral and hardware["sensorname"] == sensorname and hardware["attribute"] == attribute:
                                            printf("green = {} ({})".format(value, hex(value).upper()))
                                            g_i2c_properties_enabled_output[x][y]["value"] &= 0xFF00FF
                                            g_i2c_properties_enabled_output[x][y]["value"] |= ((value & 0xFF) << 8)
                                            printf("color = {} ({})".format(g_i2c_properties_enabled_output[x][y]["value"], hex(g_i2c_properties_enabled_output[x][y]["value"]).upper()))
                                            printf("")
                                            found = True
                                            break
                                    if individual["blue"]["endpoint"] == 1:
                                        hardware = individual["blue"]["hardware"]
                                        if hardware["devicename"] == devicename and hardware["peripheral"] == peripheral and hardware["sensorname"] == sensorname and hardware["attribute"] == attribute:
                                            printf("blue = {} ({})".format(value, hex(value).upper()))
                                            g_i2c_properties_enabled_output[x][y]["value"] &= 0xFFFF00
                                            g_i2c_properties_enabled_output[x][y]["value"] |= ((value & 0xFF) << 0)
                                            printf("color = {} ({})".format(g_i2c_properties_enabled_output[x][y]["value"], hex(g_i2c_properties_enabled_output[x][y]["value"]).upper()))
                                            printf("")
                                            found = True
                                            break
                            elif device_class == "display":
                                # if display class
                                if g_i2c_properties_enabled_output[x][y]["attributes"]["endpoint"] == 1:
                                    hardware = g_i2c_properties_enabled_output[x][y]["attributes"]["hardware"]
                                    if hardware["devicename"] == devicename and hardware["peripheral"] == peripheral and hardware["sensorname"] == sensorname and hardware["attribute"] == attribute:
                                        value = int(value)
                                        printf("text = {} ({})".format(value, hex(value).upper()))
                                        printf("")
                                        found = True
                                        break
                if found == True:
                    break

    ####################################################
    # SETTINGS
    ####################################################
    elif api == API_GET_SETTINGS:
        topic = generate_pubtopic(subtopic)

        #printf("g_device_settings {}".format(g_device_settings))

        payload = {}
        payload["value"] = g_device_settings
        publish(topic, payload)

    elif api == API_SET_SETTINGS:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        g_device_settings = subpayload
        #printf("g_device_settings {}".format(g_device_settings))
        g_timer_thread_timeout = g_device_settings["sensorrate"]
        g_timer_thread.set_timeout(g_timer_thread_timeout)

        payload = {}
        publish(topic, payload)

    ####################################################
    # GATEWAY DESCRIPTOR
    ####################################################
    elif api == API_GET_DESCRIPTOR:
        topic = generate_pubtopic(subtopic)
        payload = {}
        payload["value"] = g_gateway_descriptor
        publish(topic, payload)


    ####################################################
    # LDS BUS
    ####################################################
    elif api == API_IDENTIFY_LDSU:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        payload = {}
        publish(topic, payload)

    elif api == API_GET_LDSU_DESCS:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        if subpayload.get("PORT") is not None:
            port = int(subpayload["PORT"])
            if port >= 1 and port <= 3:
                # if port number exist, then return LDSUs for specified port
                reg_ldsu_descriptors(port=str(port), as_response=True)
            else:
                # if port number not exist, then return LDSUs for all ports
                reg_ldsu_descriptors(port=None, as_response=True)
        else:
            # if port number not exist, then return LDSUs for all ports
            reg_ldsu_descriptors(port=None, as_response=True)


    ####################################################
    # LDSU
    ####################################################

    elif api == API_ENABLE_LDSU_DEVICE:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        #printf(subpayload)


        # get parameters
        #   enable
        #   source
        #   number
        #   mode
        enable = int(subpayload["enable"])
        source = str(subpayload["UID"])
        number = int(subpayload["SAID"])
        if subpayload.get("MODE"):
            mode = int(subpayload["MODE"])
        else:
            mode = 0

        # support caching (device receives on enable, not on set)
        if enable == 1:
            g_ldsu_properties[source][number]["enabled"] = enable
            g_ldsu_properties[source][number]["mode"] = mode

            if g_ldsu_properties[source][number].get("attributes") is None:
                # get OBJ given UID
                obj = None
                for ldsu_descriptor in g_ldsu_descriptors:
                    if ldsu_descriptor["UID"] == source:
                        obj = ldsu_descriptor["OBJ"]
                        break
                # get classname, minmax (given OBJ and number)
                descriptor = g_device_client.get_objidx(obj, number)
                classname = g_device_client.get_objidx_class(descriptor)
                min,max = g_device_client.get_objidx_minmax(descriptor, mode)
                format = g_device_client.get_objidx_format(descriptor)
                type = g_device_client.get_objidx_type(descriptor)
                accuracy = g_device_client.get_objidx_accuracy(descriptor)
                g_ldsu_properties[source][number]["attributes"] = {}
                g_ldsu_properties[source][number]["attributes"]["class"] = classname
                g_ldsu_properties[source][number]["attributes"]["minmax"] = [min,max]
                g_ldsu_properties[source][number]["attributes"]["format"] = format
                g_ldsu_properties[source][number]["attributes"]["type"] = type
                g_ldsu_properties[source][number]["attributes"]["accuracy"] = accuracy


            # actuator
            # if enabling output sensor, add properties to g_i2c_properties_enabled_output
            # if disabling output sensor, remove properties from g_i2c_properties_enabled_output
            #if g_ldsu_properties[source][number]["class"] <= 2:
            #    if enable:
            #        g_i2c_properties_enabled_output[source][number][address] = g_ldsu_properties[number][address]
            #        g_i2c_properties_enabled_output[source][number][address]["value"] = 0
            #    else:
            #        del g_i2c_properties_enabled_output[number][address]
        else:
            g_ldsu_properties[source][number]["enabled"] = enable

        #printf("")
        #printf_json(g_ldsu_properties[source])
        #printf("")

        payload = {}
        publish(topic, payload)

    elif api == API_GET_LDSU_DEVICES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        ldsu_properties = g_ldsu_properties.copy()
        ldsu_keys = list(ldsu_properties.keys())
        for ldsu_key in ldsu_keys:
            for ldsu_device in ldsu_properties[ldsu_key]:
                if ldsu_device.get("attributes"):
                    del ldsu_device["attributes"]

        payload = {}
        payload["value"] = ldsu_properties
        publish(topic, payload)

    #elif api == API_GET_LDSU_DEVICE_PROPERTIES:
    #    if True:
    #        pass
    #    else:
    #        topic = generate_pubtopic(subtopic)
    #        subpayload = json.loads(subpayload)
    #
    #        number = int(subpayload["number"])
    #        address = str(subpayload["address"])
    #        source = str(subpayload["source"])
    #        value = None 
    #        try:
    #            value = g_ldsu_properties[source][number]["attributes"]
    #        except:
    #            pass
    #
    #        payload = {}
    #        if value is not None:
    #            payload["value"] = value
    #        publish(topic, payload)

    #elif api == API_SET_LDSU_DEVICE_PROPERTIES:
    #    if True:
    #        pass
    #    else:
    #        # no longer needed for caching case
    #
    #        topic = generate_pubtopic(subtopic)
    #        printf(len(subpayload))
    #        subpayload = json.loads(subpayload)
    #        #printf(subpayload)
    #
    #        number = int(subpayload["number"])
    #        address = str(subpayload["address"])
    #        device_class = subpayload["class"]
    #        g_ldsu_properties[source][number] = {
    #            'address': address,
    #            'class': device_class,
    #            'attributes' : setClassAttributes(device_class, subpayload),
    #            'enabled': 0
    #        }
    #        #printf("")
    #        printf(g_ldsu_properties[source])
    #        #printf("")
    #
    #        payload = {}
    #        publish(topic, payload)


    ####################################################
    # UART
    ####################################################
    #elif api == API_GET_UARTS:
    #    topic = generate_pubtopic(subtopic)
    #    subpayload = json.loads(subpayload)
    #
    #    value = {
    #        'uarts': [
    #            {'enabled': g_uart_enabled },
    #        ]
    #    }
    #    #printf(g_uart_enabled)
    #
    #    payload = {}
    #    payload["value"] = value
    #    publish(topic, payload)
    #
    #elif api == API_GET_UART_PROPERTIES:
    #    topic = generate_pubtopic(subtopic)
    #    subpayload = json.loads(subpayload)
    #
    #    value = g_uart_properties
    #    #printf(g_uart_properties)
    #    #printf(g_uart_baudrate[g_uart_properties['baudrate']])
    #    #printf(g_uart_parity[g_uart_properties['parity']])
    #    #printf(g_uart_flowcontrol[g_uart_properties['flowcontrol']])
    #    #printf(g_uart_stopbits[g_uart_properties['stopbits']])
    #    #printf(g_uart_databits[g_uart_properties['databits']])
    #
    #    payload = {}
    #    payload["value"] = value
    #    publish(topic, payload)

    elif api == API_SET_UART_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        #printf(subpayload)

        g_uart_properties = { 
            'baudrate': subpayload["baudrate"], 
            'parity': subpayload["parity"],
            'flowcontrol': subpayload["flowcontrol"],
            'stopbits': subpayload["stopbits"],
            'databits': subpayload["databits"],
        }
        #printf(g_uart_properties)
        #printf(g_uart_baudrate[g_uart_properties['baudrate']])
        #printf(g_uart_parity[g_uart_properties['parity']])
        #printf(g_uart_flowcontrol[g_uart_properties['flowcontrol']])
        #printf(g_uart_stopbits[g_uart_properties['stopbits']])
        #printf(g_uart_databits[g_uart_properties['databits']])

        payload = {}
        publish(topic, payload)

    elif api == API_ENABLE_UART:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        #printf(subpayload)

        g_uart_enabled = int(subpayload["enable"])
        #printf(g_uart_enabled)

        payload = {}
        publish(topic, payload)


    ####################################################
    # GPIO
    ####################################################
    #elif api == API_GET_GPIOS:
    #    topic = generate_pubtopic(subtopic)
    #    subpayload = json.loads(subpayload)
    #
    #    value = {
    #        'voltage': g_gpio_voltage,
    #        'gpios': [
    #            {'direction': g_gpio_properties[0]['direction'], 'status': g_gpio_status[0], 'enabled': g_gpio_enabled[0] },
    #            {'direction': g_gpio_properties[1]['direction'], 'status': g_gpio_status[1], 'enabled': g_gpio_enabled[1] },
    #            {'direction': g_gpio_properties[2]['direction'], 'status': g_gpio_status[2], 'enabled': g_gpio_enabled[2] },
    #            {'direction': g_gpio_properties[3]['direction'], 'status': g_gpio_status[3], 'enabled': g_gpio_enabled[3] }
    #        ]
    #    }
    #    #printf(g_gpio_enabled)
    #
    #    payload = {}
    #    payload["value"] = value
    #    publish(topic, payload)
    #
    #elif api == API_GET_GPIO_PROPERTIES:
    #    topic = generate_pubtopic(subtopic)
    #    subpayload = json.loads(subpayload)
    #
    #    number = int(subpayload["number"])-1
    #    value = g_gpio_properties[number]
    #
    #    payload = {}
    #    payload["value"] = value
    #    publish(topic, payload)
    #
    #elif api == API_SET_GPIO_PROPERTIES:
    #    topic = generate_pubtopic(subtopic)
    #    subpayload = json.loads(subpayload)
    #    #printf(subpayload)
    #
    #    number = int(subpayload["number"])-1
    #    g_gpio_properties[number] = { 
    #        'direction' : subpayload["direction"], 
    #        'mode' : subpayload["mode"],
    #        'alert': subpayload["alert"],
    #        'alertperiod': subpayload["alertperiod"],
    #        'polarity': subpayload["polarity"],
    #        'width': subpayload["width"],
    #        'mark': subpayload["mark"],
    #        'space': subpayload["space"],
    #        'count': subpayload["count"] }
    #    value = g_gpio_properties[number]
    #
    #    payload = {}
    #    publish(topic, payload)
    #
    #elif api == API_ENABLE_GPIO:
    #    topic = generate_pubtopic(subtopic)
    #    subpayload = json.loads(subpayload)
    #    #printf(subpayload)
    #
    #    g_gpio_enabled[int(subpayload["number"])-1] = subpayload["enable"]
    #    #printf(g_gpio_enabled)
    #
    #    payload = {}
    #    publish(topic, payload)
    #
    #elif api == API_GET_GPIO_VOLTAGE:
    #    topic = generate_pubtopic(subtopic)
    #
    #    payload = {}
    #    payload["value"] = {"voltage": g_gpio_voltage}
    #    publish(topic, payload)
    #    #printf(g_gpio_voltages[g_gpio_voltage])
    #
    #elif api == API_SET_GPIO_VOLTAGE:
    #    topic = generate_pubtopic(subtopic)
    #    subpayload = json.loads(subpayload)
    #    #printf(subpayload)
    #
    #    g_gpio_voltage = subpayload["voltage"]
    #    #printf(g_gpio_voltages[g_gpio_voltage])
    #
    #    payload = {}
    #    publish(topic, payload)


    ####################################################
    # I2C
    ####################################################

    elif api == API_GET_I2C_DEVICES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        number = int(subpayload["number"])-1

        value = []
        for y in g_i2c_properties[number]:
            if (int(y) > 0 and g_i2c_properties[number][y]["class"] != 255):
                entry = {}
                entry["class"]   = g_i2c_properties[number][y]["class"]
                entry["enabled"] = g_i2c_properties[number][y]["enabled"]
                entry["address"] = int(y)
                value.append(entry)
        #printf(value)

        payload = {}
        payload["value"] = value
        publish(topic, payload)

    elif api == API_ENABLE_I2C_DEVICE:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        number = int(subpayload["number"])-1
        address = str(subpayload["address"])
        enable = int(subpayload["enable"])

        # support caching (device receives on enable, not on set)
        if subpayload.get("class") and enable == 1:
            device_class = subpayload["class"]
            g_i2c_properties[number][address] = {
                'class': device_class,
                'attributes' : setClassAttributes(device_class, subpayload),
                'enabled': 0
            }

        try:
            g_i2c_properties[number][address]["enabled"] = enable

            # if enabling output sensor, add properties to g_i2c_properties_enabled_output
            # if disabling output sensor, remove properties from g_i2c_properties_enabled_output
            if g_i2c_properties[number][address]["class"] <= 2:
                if enable:
                    g_i2c_properties_enabled_output[number][address] = g_i2c_properties[number][address]
                    g_i2c_properties_enabled_output[number][address]["value"] = 0
                else:
                    del g_i2c_properties_enabled_output[number][address]
        except:
            pass
        #printf("")
        #printf(g_i2c_properties[number])
        #printf("")

        payload = {}
        publish(topic, payload)

    elif api == API_GET_I2C_DEVICE_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        number = int(subpayload["number"])-1
        address = str(subpayload["address"])
        value = None 
        try:
            if g_i2c_properties[number].get(address):
                value = g_i2c_properties[number][address]["attributes"]
                #printf("")
                #printf(value)
                #printf("")
        except:
            pass

        payload = {}
        if value is not None:
            payload["value"] = value
        publish(topic, payload)

    elif api == API_SET_I2C_DEVICE_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        printf(len(subpayload))
        subpayload = json.loads(subpayload)
        #printf(subpayload)

        number = int(subpayload["number"])-1
        address = str(subpayload["address"])
        device_class = subpayload["class"]
        g_i2c_properties[number][address] = {
            'class': device_class,
            'attributes' : setClassAttributes(device_class, subpayload),
            'enabled': 0
        }
        #printf("")
        #printf(g_i2c_properties[number])
        #printf("")

        payload = {}
        publish(topic, payload)


    ####################################################
    # ADC
    ####################################################

    elif api == API_GET_ADC_DEVICES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        number = int(subpayload["number"])-1

        value = []
        if g_adc_properties[number]["class"] != 255:
            entry = {}
            entry["class"]   = g_adc_properties[number]["class"]
            entry["enabled"] = g_adc_properties[number]["enabled"]
            value.append(entry)
        #printf(value)

        payload = {}
        payload["value"] = value
        publish(topic, payload)    

    elif api == API_ENABLE_ADC_DEVICE:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        #printf(subpayload)

        number = int(subpayload["number"])-1
        enable = int(subpayload["enable"])
        try:
            g_adc_properties[number]["enabled"] = enable
        except:
            pass
        #printf("")
        #printf(g_adc_properties[number])
        #printf("")

        payload = {}
        publish(topic, payload)

    elif api == API_GET_ADC_DEVICE_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        number = int(subpayload["number"])-1
        value = None 
        try:
            value = g_adc_properties[number]["attributes"]
            #printf("")
            #printf(value)
            #printf("")
        except:
            pass

        payload = {}
        if value is not None:
            payload["value"] = value
        publish(topic, payload)

    elif api == API_SET_ADC_DEVICE_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        #printf(subpayload)

        number = int(subpayload["number"])-1
        device_class = subpayload["class"]
        g_adc_properties[number] = {
            'class': device_class,
            'attributes' : setClassAttributes(device_class, subpayload),
            'enabled': 0
        }
        #printf("")
        #printf(g_adc_properties[number])
        #printf("")

        payload = {}
        publish(topic, payload)

    elif api == API_GET_ADC_VOLTAGE:
        topic = generate_pubtopic(subtopic)

        payload = {}
        payload["value"] = {"voltage": g_adc_voltage}
        publish(topic, payload)
        printf(g_adc_voltages[g_adc_voltage])

    elif api == API_SET_ADC_VOLTAGE:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        printf(subpayload)

        g_adc_voltage = subpayload["voltage"]
        printf(g_adc_voltages[g_adc_voltage])

        payload = {}
        publish(topic, payload)


    ####################################################
    # 1WIRE
    ####################################################

    elif api == API_GET_1WIRE_DEVICES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        number = int(subpayload["number"])-1

        value = []
        if g_1wire_properties[number]["class"] != 255:
            entry = {}
            entry["class"]   = g_1wire_properties[number]["class"]
            entry["enabled"] = g_1wire_properties[number]["enabled"]
            value.append(entry)
        #printf(value)

        payload = {}
        payload["value"] = value
        publish(topic, payload)    

    elif api == API_ENABLE_1WIRE_DEVICE:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        #printf(subpayload)

        number = int(subpayload["number"])-1
        enable = int(subpayload["enable"])
        try:
            g_1wire_properties[number]["enabled"] = enable
        except:
            pass
        #printf("")
        #printf(g_1wire_properties[number])
        #printf("")

        payload = {}
        publish(topic, payload)

    elif api == API_GET_1WIRE_DEVICE_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        number = int(subpayload["number"])-1
        value = None 
        try:
            value = g_1wire_properties[number]["attributes"]
            #printf("")
            #printf(value)
            #printf("")
        except:
            pass

        payload = {}
        if value is not None:
            payload["value"] = value
        publish(topic, payload)

    elif api == API_SET_1WIRE_DEVICE_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        #printf(subpayload)

        number = int(subpayload["number"])-1
        device_class = subpayload["class"]
        g_1wire_properties[number] = {
            'class': device_class,
            'attributes' : setClassAttributes(device_class, subpayload),
            'enabled': 0
        }
        #printf("")
        #printf(g_1wire_properties[number])
        #printf("")

        payload = {}
        publish(topic, payload)


    ####################################################
    # TPROBE
    ####################################################

    elif api == API_GET_TPROBE_DEVICES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        number = int(subpayload["number"])-1

        value = []
        if g_tprobe_properties[number]["class"] != 255:
            entry = {}
            entry["class"]   = g_tprobe_properties[number]["class"]
            entry["enabled"] = g_tprobe_properties[number]["enabled"]
            value.append(entry)
        #printf(value)

        payload = {}
        payload["value"] = value
        publish(topic, payload)    

    elif api == API_ENABLE_TPROBE_DEVICE:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        #printf(subpayload)

        number = int(subpayload["number"])-1
        enable = int(subpayload["enable"])
        try:
            g_tprobe_properties[number]["enabled"] = enable
        except:
            pass
        #printf("")
        #printf(g_tprobe_properties[number])
        #printf("")

        payload = {}
        publish(topic, payload)

    elif api == API_GET_TPROBE_DEVICE_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        number = int(subpayload["number"])-1
        value = None 
        try:
            value = g_tprobe_properties[number]["attributes"]
            #printf("")
            #printf("GET: {}".format(value))
            #printf("")
        except:
            pass

        payload = {}
        if value is not None:
            payload["value"] = value
        publish(topic, payload)

    elif api == API_SET_TPROBE_DEVICE_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        #printf("SET: {}".format(subpayload))

        number = int(subpayload["number"])-1
        device_class = subpayload["class"]
        # handle subclass
        device_subclass = None
        if subpayload.get("subclass"):
            device_subclass = subpayload["subclass"]

        g_tprobe_properties[number] = {
            'class': device_class,
            'attributes' : setClassAttributes(device_class, subpayload),
            'enabled': 0
        }

        # handle subclass
        if device_subclass is not None:
            g_tprobe_properties[number]['subclass'] = device_subclass

        #printf("")
        #printf(g_tprobe_properties[number])
        #printf("")

        payload = {}
        publish(topic, payload)


    ####################################################
    # i2c/adc/1wire/tprobe
    ####################################################

    elif api == API_GET_PERIPHERAL_DEVICES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        value = {}

        #
        # i2c
        for x in range(len(g_i2c_properties)):
            i2c_value = []
            for y in g_i2c_properties[x]:
                if int(y) > 0 and g_i2c_properties[x][y]["class"] != 255:
                    entry = {}
                    entry["class"]   = g_i2c_properties[x][y]["class"]
                    entry["enabled"] = g_i2c_properties[x][y]["enabled"]
                    entry["address"] = int(y)
                    i2c_value.append(entry)

            label = "i2c{}".format(x+1)
            printf("{}: {}".format(label, i2c_value))

            if len(i2c_value) > 0:
                value[label] = {}
                value[label] = i2c_value

        #
        # adc
        for x in range(len(g_adc_properties)):
            adc_value = []
            if g_adc_properties[x]["class"] != 255:
                entry = {}
                entry["class"]   = g_adc_properties[x]["class"]
                entry["enabled"] = g_adc_properties[x]["enabled"]
                adc_value.append(entry)

            label = "adc{}".format(x+1)
            printf("{}: {}".format(label, adc_value))

            if len(adc_value) > 0:
                value[label] = {}
                value[label] = adc_value

        #
        # onewire
        for x in range(len(g_1wire_properties)):
            onewire_value = []
            if g_1wire_properties[x]["class"] != 255:
                entry = {}
                entry["class"]   = g_1wire_properties[x]["class"]
                entry["enabled"] = g_1wire_properties[x]["enabled"]
                onewire_value.append(entry)

            label = "1wire{}".format(x+1)
            printf("{}: {}".format(label, onewire_value))

            if len(onewire_value) > 0:
                value[label] = {}
                value[label] = onewire_value

        #
        # tprobe
        for x in range(len(g_tprobe_properties)):
            tprobe_value = []
            if g_tprobe_properties[x]["class"] != 255:
                entry = {}
                entry["class"]   = g_tprobe_properties[x]["class"]
                entry["enabled"] = g_tprobe_properties[x]["enabled"]
                tprobe_value.append(entry)

            label = "tprobe{}".format(x+1)
            printf("{}: {}".format(label, tprobe_value))

            if len(tprobe_value) > 0:
                value[label] = {}
                value[label] = tprobe_value

        printf("")
        payload = {}
        payload["value"] = value
        #printf(payload["value"])
        publish(topic, payload)    


    ####################################################
    # NOTIFICATION
    ####################################################

    #elif api == API_TRIGGER_NOTIFICATION:
    #    topic = generate_pubtopic(subtopic)
    #    subpayload = json.loads(subpayload)
    #    # Notification from cloud
    #    publish(topic, subpayload)
    #    printf("Notification triggered to email/SMS recipient!")

    elif api == API_RECEIVE_NOTIFICATION:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        # Notification from another device
        printf("Notification received from device {}:".format(subpayload["sender"]))
        printf(subpayload["message"])
        printf("")

    elif api == API_STATUS_NOTIFICATION:
        printf("")
        pass


    ####################################################
    # CONFIGURATION
    ####################################################

    elif api == API_RECEIVE_CONFIGURATION:
        topic = generate_pubtopic(subtopic)
        if len(subpayload) > 2:
            printf(len(subpayload))
        subpayload = json.loads(subpayload)

        if CONFIG_SAVE_CONFIGURATION_TO_FILE:
            save_configuration(subpayload)

        if CONFIG_REQUEST_CONFIGURATION_DEBUG:
            printf("")
            if subpayload.get("ldsu"):
                printf("ldsu   {} - {}".format(subpayload["ldsu"],   len(subpayload["ldsu"])   ))
                printf("")
            if subpayload.get("uart"):
                printf("uart   {} - {}".format(subpayload["uart"],   len(subpayload["uart"])   ))
                printf("")
            if subpayload.get("gpio"):
                printf("gpio   {} - {}".format(subpayload["gpio"],   len(subpayload["gpio"])   ))
                printf("")
            if subpayload.get("i2c"):
                printf("i2c    {} - {}".format(subpayload["i2c"],    len(subpayload["i2c"])    ))
                printf("")
                printf("  i2c0 {} - {}".format(subpayload["i2c"][0], len(subpayload["i2c"][0]) ))
                printf("")
                printf("  i2c1 {} - {}".format(subpayload["i2c"][1], len(subpayload["i2c"][1]) ))
                printf("")
                printf("  i2c2 {} - {}".format(subpayload["i2c"][2], len(subpayload["i2c"][2]) ))
                printf("")
                printf("  i2c3 {} - {}".format(subpayload["i2c"][3], len(subpayload["i2c"][3]) ))
                printf("")
            if subpayload.get("adc"):
                printf("adc    {} - {}".format(subpayload["adc"],    len(subpayload["adc"])    ))
                printf("")
            if subpayload.get("1wire"):
                printf("1wire  {} - {}".format(subpayload["1wire"],  len(subpayload["1wire"])  ))
                printf("")
            if subpayload.get("tprobe"):
                printf("tprobe {} - {}".format(subpayload["tprobe"], len(subpayload["tprobe"]) ))
                printf("")
            printf("")

        # LDSU
        if subpayload.get("ldsu"):
            ldsus = subpayload["ldsu"]
            for ldsu in ldsus:
                #printf(ldsu)
                source = ldsu["UID"]
                number = int(ldsu["SAID"])
                mode = int(ldsu["MODE"])
                g_ldsu_properties[source][number]["enabled"] = ldsu["enabled"]
                g_ldsu_properties[source][number]["mode"] = mode

                if g_ldsu_properties[source][number].get("attributes") is None:
                    # get OBJ given UID
                    obj = None
                    for ldsu_descriptor in g_ldsu_descriptors:
                        if ldsu_descriptor["UID"] == source:
                            obj = ldsu_descriptor["OBJ"]
                            break
                    # get classname, minmax (given OBJ and number)
                    descriptor = g_device_client.get_objidx(obj, number)
                    classname = g_device_client.get_objidx_class(descriptor)
                    min,max = g_device_client.get_objidx_minmax(descriptor, mode)
                    format = g_device_client.get_objidx_format(descriptor)
                    type = g_device_client.get_objidx_type(descriptor)
                    accuracy = g_device_client.get_objidx_accuracy(descriptor)
                    g_ldsu_properties[source][number]["attributes"] = {}
                    g_ldsu_properties[source][number]["attributes"]["class"] = classname
                    g_ldsu_properties[source][number]["attributes"]["minmax"] = [min,max]
                    g_ldsu_properties[source][number]["attributes"]["format"] = format
                    g_ldsu_properties[source][number]["attributes"]["type"] = type
                    g_ldsu_properties[source][number]["attributes"]["accuracy"] = accuracy
                    #print(g_ldsu_properties[source][number])

            #printf_json(g_ldsu_properties[source])

        # UART
        if subpayload.get("uart"):
            if subpayload["uart"][0].get("attributes"):
                g_uart_properties = subpayload["uart"][0]["attributes"]
                #printf(g_uart_properties)

        # GPIO
        if subpayload.get("gpio"):
            for x in range(len(g_gpio_properties)):
                if subpayload["gpio"][x].get("attributes"):
                    g_gpio_properties[x] = subpayload["gpio"][x]["attributes"]

        # ADC
        if subpayload.get("adc"):
            for x in range(len(g_adc_properties)):
                if subpayload["adc"][x].get("attributes"):
                    if CONFIG_AUTO_ENABLE_CONFIGURATION:
                        if subpayload["adc"][x]["enabled"]:
                            g_adc_properties[x]["enabled"] = subpayload["adc"][x]["enabled"]
                        else:
                            g_adc_properties[x]["enabled"] = 0
                    else:
                        g_adc_properties[x]["enabled"] = 0
                    g_adc_properties[x]["class"] = subpayload["adc"][x]["class"]
                    g_adc_properties[x]["attributes"] = subpayload["adc"][x]["attributes"]
                    if subpayload["adc"][x].get("subclass"):
                        g_adc_properties[x]["subclass"] = subpayload["adc"][x]["subclass"]

        # 1WIRE
        if subpayload.get("1wire"):
            for x in range(len(g_1wire_properties)):
                if subpayload["1wire"][x].get("attributes"):
                    if CONFIG_AUTO_ENABLE_CONFIGURATION:
                        if subpayload["1wire"][x]["enabled"]:
                            g_1wire_properties[x]["enabled"] = subpayload["1wire"][x]["enabled"]
                        else:
                            g_1wire_properties[x]["enabled"] = 0
                    else:
                        g_1wire_properties[x]["enabled"] = 0
                    g_1wire_properties[x]["class"] = subpayload["1wire"][x]["class"]
                    g_1wire_properties[x]["attributes"] = subpayload["1wire"][x]["attributes"]
                    if subpayload["1wire"][x].get("subclass"):
                        g_1wire_properties[x]["subclass"] = subpayload["1wire"][x]["subclass"]

        # TPROBE
        if subpayload.get("tprobe"):
            for x in range(len(g_tprobe_properties)):
                if subpayload["tprobe"][x].get("attributes"):
                    if CONFIG_AUTO_ENABLE_CONFIGURATION:
                        if subpayload["tprobe"][x]["enabled"]:
                            g_tprobe_properties[x]["enabled"] = subpayload["tprobe"][x]["enabled"]
                        else:
                            g_tprobe_properties[x]["enabled"] = 0
                    else:
                        g_tprobe_properties[x]["enabled"] = 0
                    g_tprobe_properties[x]["class"] = subpayload["tprobe"][x]["class"]
                    g_tprobe_properties[x]["attributes"] = subpayload["tprobe"][x]["attributes"]
                    if subpayload["tprobe"][x].get("subclass"):
                        g_tprobe_properties[x]["subclass"] = subpayload["tprobe"][x]["subclass"]

        # I2C
        if subpayload.get("i2c"):
            for x in range(len(g_i2c_properties)):
                for y in range(len(subpayload["i2c"][x])):
                    if subpayload["i2c"][x][y].get("attributes"):
                        address = str(subpayload["i2c"][x][y]["address"])
                        g_i2c_properties[x][address] = {}
                        g_i2c_properties[x][address]["class"] = subpayload["i2c"][x][y]["class"]
                        g_i2c_properties[x][address]["attributes"] = subpayload["i2c"][x][y]["attributes"]
                        if CONFIG_AUTO_ENABLE_CONFIGURATION:
                            if subpayload["i2c"][x][y].get("enabled"):
                                g_i2c_properties[x][address]["enabled"] = subpayload["i2c"][x][y]["enabled"]
                                # if enabling output sensor, add properties to g_i2c_properties_enabled_output
                                # if disabling output sensor, remove properties from g_i2c_properties_enabled_output
                                if g_i2c_properties[x][address]["class"] <= 2:
                                    if g_i2c_properties[x][address]["enabled"]:
                                        g_i2c_properties_enabled_output[x][address] = g_i2c_properties[x][address]
                                        g_i2c_properties_enabled_output[x][address]["value"] = 0
                            else:
                                g_i2c_properties[x][address]["enabled"] = 0
                        else:
                            g_i2c_properties[x][address]["enabled"] = 0
                        if subpayload["i2c"][x][y].get("subclass"):
                            g_i2c_properties[x][address]["subclass"] = subpayload["i2c"][x][y]["subclass"]

        if CONFIG_REQUEST_CONFIGURATION_DEBUG:
            printf_json(g_ldsu_properties,   "ldsu")
            printf_json(g_uart_properties,   "uart")
            printf_json(g_gpio_properties,   "gpio")
            printf_json(g_adc_properties,    "adc")
            printf_json(g_1wire_properties,  "1wire")
            printf_json(g_tprobe_properties, "tprobe")
            printf_json(g_i2c_properties,    "i2c")

        printf("")
        printf("DEVICE CONFIGURATION")
        printf("Device is now configured with cached values from cloud.")
        printf("")
        printf("")
        g_device_status = DEVICE_STATUS_RUNNING


    ####################################################
    # FIRMWARE UPGRADE
    ####################################################

    elif api == API_REQUEST_OTASTATUS:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        printf("")


    elif api == API_UPGRADE_FIRMWARE:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        # stop the timer thread and heartbeat thread
        while g_timer_thread is None or g_heartbeat_thread is None:
            time.sleep(1)
        g_timer_thread.set_pause(True)
        g_heartbeat_thread.set_pause(True)

        # reply
        payload = {}
        publish(topic, payload)

        # start the download thread
        printf("")
        printf("")
        printf("")
        printf("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        printf("")
        printf("Device is now starting to download the firmware !!!")
        printf("")
        g_download_thread_stop = threading.Event()
        g_download_thread_stop.set()
        g_download_thread = DownloadThread(g_download_thread_stop, g_download_thread_timeout)
        g_download_thread.set_parameters(subpayload["location"], subpayload["size"], subpayload["version"], subpayload["checksum"])
        g_download_thread.start()


    elif api == API_RECEIVE_FIRMWARE:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        # write to file
        if subpayload["offset"] == 0:
            f = open(g_download_thread.get_filename(), "wb")
            bin = subpayload["bin"].encode("utf-8")
            bin = base64.b64decode(bin)
            f.write(bin)
            f.close()
        else:
            f = open(g_download_thread.get_filename(), "ab")
            bin = subpayload["bin"].encode("utf-8")
            bin = base64.b64decode(bin)
            f.write(bin)
            f.close()
        #printf("\r\nReceived {} bytes {} offset.\r\n".format(subpayload["size"], subpayload["offset"]))

        # inform download thread
        g_download_thread.set_downloaded(subpayload["size"])
        g_download_thread_stop.set()


    elif api == API_RECEIVE_TIME:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        printf("")


    ####################################################
    # UNSUPPORTED
    ####################################################

    else:
        printf("UNSUPPORTED")



###################################################################################
# LDSU helper functions
###################################################################################

def saveToLDSFile():
    lds_filename = CONFIG_DEVICE_ID + ".json"
    json_obj = { "LDS": g_ldsu_descriptors }
    json_obj = json.dumps(json_obj, indent=2)
    g_device_client.save_lds_reg(lds_filename, json_obj)

def listLDSUs(port):
    if port>0 and port<=3:
        for ldsu in g_ldsu_descriptors:
            if port == int(ldsu["PORT"]):
                printf("{} Port {} [{}-{}]".format(ldsu["UID"], ldsu["PORT"], ldsu["OBJ"], ldsu["NAME"]))
                numdevices = g_device_client.get_obj_numdevices(ldsu["OBJ"])
                for number in range(numdevices):
                    descriptor = g_device_client.get_objidx(ldsu["OBJ"], number)
                    classname = g_device_client.get_objidx_class(descriptor)
                    printf("  {} {}".format(number, classname))
    else:
        for ldsu in g_ldsu_descriptors:
            printf("{} Port {} [{}-{}]".format(ldsu["UID"], ldsu["PORT"], ldsu["OBJ"], ldsu["NAME"]))
            numdevices = g_device_client.get_obj_numdevices(ldsu["OBJ"])
            for number in range(numdevices):
                descriptor = g_device_client.get_objidx(ldsu["OBJ"], number)
                classname = g_device_client.get_objidx_class(descriptor)
                printf("  {} {}".format(number, classname))
    printf("")

def moveLDSU(uid, port):
    found = False
    for ldsu in g_ldsu_descriptors:
        if uid == ldsu["UID"]:
            ldsu["PORT"] = str(port)
            reg_ldsu_descriptors()
            found = True
            break
    if not found:
        printf("{} not found.".format(uid))
    else:
        # save to file to make changes persistent on reboot
        saveToLDSFile()
    printf("")

def generateUID():
    uid = ""
    while True:
        found = False
        uid = "{}{:02d}".format(CONFIG_DEVICE_ID, random.randint(0, 99))
        for ldsu in g_ldsu_descriptors:
            if ldsu["UID"] == uid:
                found = True
                break

        if not found:
            break
    return uid

def plugLDSU(obj, port, uid):
    ldsu_descriptor = g_device_client.get_ldsu_reg_from_lds_reg_template(obj)
    if ldsu_descriptor is None:
        printf("{} is not found!".format(obj))
        return
    if port<=0 and port>3:
        printf("{} is not valid!".format(port))
        return

    if uid is None:
        # generate a uid
        uid = generateUID()
    else:
        # check if uid is not present
        for ldsu in g_ldsu_descriptors:
            if ldsu["UID"] == uid:
                printf("{} is not valid".format(uid))
                return

    # update LDSU descriptor and register it
    ldsu_descriptor["UID"] = uid
    ldsu_descriptor["PORT"] = str(port)
    g_ldsu_descriptors.append(ldsu_descriptor)
    reg_ldsu_descriptors()

    # update LDSU properties to add for the new LDSU
    if g_ldsu_properties.get(uid) is None:
        obj = ldsu_descriptor["OBJ"]
        numdevices = g_device_client.get_obj_numdevices(obj)
        g_ldsu_properties[uid] = []
        for device in range(numdevices):
            g_ldsu_properties[uid].append({ 'enabled': 0, 'mode': 0 })


    # save to file to make changes persistent on reboot
    saveToLDSFile()
    printf("")

def unplugLDSU(uid):
    found = False
    for ldsu in g_ldsu_descriptors:
        if uid == ldsu["UID"]:
            g_ldsu_descriptors.remove(ldsu)
            reg_ldsu_descriptors()
            found = True
            break
    if not found:
        printf("{} not found.".format(uid))
    else:
        # save to file to make changes persistent on reboot
        saveToLDSFile()
    printf("")



###################################################################################
# MQTT/AMQP callback functions
###################################################################################

def on_message(subtopic, subpayload):

    expected_topic = "{}{}".format(CONFIG_DEVICE_ID, CONFIG_SEPARATOR)
    expected_topic_len = len(expected_topic)

    if subtopic[:expected_topic_len] != expected_topic:
        printf("unexpected packet")
        return

    api = subtopic[expected_topic_len:]
    #printf(api)
    handle_api(api, subtopic, subpayload)


def on_mqtt_message(client, userdata, msg):

    printf("RCV: {}".format(msg.topic))
    printf_json(json.loads(msg.payload))
    on_message(msg.topic, msg.payload)

  
def on_amqp_message(ch, method, properties, body):

    printf("RCV: AMQP {} {}".format(method.routing_key, body))
    on_message(method.routing_key, body)



###################################################################################
# Restart/stop/start application
###################################################################################

def restart():
    try:
        p = psutil.Process(os.getpid())
        for handler in p.get_open_files() + p.connections():
            os.close(handler.fd)
    except Exception as e:
        pass

    python = sys.executable
    command = ""
    for arg in sys.argv:
        command += "{} ".format(arg)
    os.execl(python, python, command)

def process_restart():
    global g_device_status
    if g_device_status == DEVICE_STATUS_RESTARTING:
        printf("")
        printf("Device will be restarting in 3 seconds")
        for x in range(3):
            time.sleep(1)
            printf(".")
        time.sleep(1)
        restart()

def process_stop():
    global g_device_status, g_timer_thread, g_heartbeat_thread
    if g_device_status == DEVICE_STATUS_STOPPING:
        printf("")
        printf("Device will be stopped...")
        g_timer_thread.set_pause(True)
        g_heartbeat_thread.set_pause(True)
        g_device_status = DEVICE_STATUS_STOPPED
        printf("Device stopped successfully!\n")

def process_start():
    global g_device_status, g_timer_thread, g_heartbeat_thread
    if g_device_status == DEVICE_STATUS_STARTING:
        printf("")
        printf("Device will be started...")
        g_timer_thread.set_pause(False)
        g_heartbeat_thread.set_pause(False)
        g_device_status = DEVICE_STATUS_RUNNING
        printf("Device started successfully!\n")


def req_configuration(peripherals = None):
    printf("")
    printf("")
    printf("Request device configuration")
    topic = "{}{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_DEVICE_ID, CONFIG_SEPARATOR, API_REQUEST_CONFIGURATION)
    if peripherals is None:
        payload = {}
    else:
        payload = { "peripherals": peripherals }
    publish(topic, payload)

def del_configuration():
    printf("")
    printf("")
    printf("\Delete device configuration")
    topic = "{}{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_DEVICE_ID, CONFIG_SEPARATOR, API_DELETE_CONFIGURATION)
    payload = {}
    publish(topic, payload)

def set_configuration(filename = None):
    topic = "{}{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_DEVICE_ID, CONFIG_SEPARATOR, API_SET_CONFIGURATION)
    payload = {}

    if filename is None:
        filename = "{}.cfg".format(CONFIG_DEVICE_ID)
    printf("")
    printf("")
    printf("Load device configuration from file {}".format(filename))

    try:
        f = open(filename, "r")
    except:
        printf("{} does not exist".format(filename))
        return
    #json_formatted_str = json.dumps(json_config, indent=2)
    config = f.read()
    payload = json.loads(config)
    #printf_json(payload)
    f.close()

    publish(topic, payload)

def save_configuration(json_config):
    try:
        now = datetime.datetime.now()
        filename = "{}_{}.cfg".format(CONFIG_DEVICE_ID, now.strftime("%Y%m%d_%H%M%S"))
        f = open(filename, "w")
        json_formatted_str = json.dumps(json_config, indent=2)
        if (json_formatted_str != "{}"):
            f.write(json_formatted_str)
        f.close()

        printf("")
        if (json_formatted_str != "{}"):
            printf("Device configuration saved to {}".format(filename))
        else:
            printf("Device configuration is empty; not saving to file")
        printf("")
    except:
        printf("exception")
        pass

def req_otastatus(ver):
    printf("")
    printf("")
    printf("Request OTA status")
    topic = "{}{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_DEVICE_ID, CONFIG_SEPARATOR, API_REQUEST_OTASTATUS)
    payload = {"version": ver}
    publish(topic, payload)

def req_epochtime():
    printf("")
    printf("")
    printf("Request EPOCH time")
    topic = "{}{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_DEVICE_ID, CONFIG_SEPARATOR, API_REQUEST_TIME)
    payload = {}
    payload = json.dumps(payload)
    publish(topic, payload)


def get_random_data(peripheral_class):
    if peripheral_class == "potentiometer":
        return random.randint(0, 255)
    elif peripheral_class == "temperature":
        return float("{0:.1f}".format(random.uniform(0, 40)))
    elif peripheral_class == "anemometer":
        return float("{0:.1f}".format(random.uniform(0, 100)))
    elif peripheral_class == "humidity":
        return float("{0:.1f}".format(random.uniform(0, 100)))
    elif peripheral_class == "battery":
        return float("{0:.1f}".format(random.uniform(0, 100)))
    elif peripheral_class == "fluid":
        return float("{0:.1f}".format(random.uniform(0, 100)))
    else:
        return float("{0:.1f}".format(random.uniform(0, 100)))

def get_random_data_ex(format, accuracy, min, max):
    if format == "integer":
        return random.randint(min, max)
    elif format == "float":
        if accuracy == 1:
            return float("{0:.1f}".format(random.uniform(min, max)))
        elif accuracy == 2:
            return float("{0:.2f}".format(random.uniform(min, max)))
        return random.randint(min, max)
    elif format == "boolean":
        return True if random.randint(0, 1) else False

class TimerThread(threading.Thread):

    def __init__(self, event, timeout):
        threading.Thread.__init__(self)
        self.stopped = event
        self.timeout = timeout
        self.pause = False
        self.exit = False
        if CONFIG_SEND_NOTIFICATION_PERIODICALLY:
            self.notification_counter = 0
            self.notification_max = int(CONFIG_SEND_NOTIFICATION_PERIOD/timeout)

    def set_timeout(self, timeout):
        self.timeout = timeout
        if CONFIG_SEND_NOTIFICATION_PERIODICALLY:
            self.notification_max = int(CONFIG_SEND_NOTIFICATION_PERIOD/timeout)

    def set_pause(self, pause=True):
        self.pause = pause

    def set_exit(self):
        self.exit = True

    def process_ldsu_input_devices(self):
        topic = "{}{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_DEVICE_ID, CONFIG_SEPARATOR, API_PUBLISH_SENSOR_READING)

#        sensors = { 
#            "UID": string,          # LDSU UUID
#            "TS": string,           # TIMESTAMP
#            "SNS": ["", "", "", ""] # VALUES
#        }

        ldsu_keys = list(g_ldsu_properties.keys())
        for ldsu_key in ldsu_keys:
            has_enabled = False
            values = []
            # generate random value for enabled sensors of the LDSU
            for ldsu_device in g_ldsu_properties[ldsu_key]:
                if ldsu_device.get("attributes"):
                    attributes = ldsu_device["attributes"]
                    # generate random value if sensor is enabled
                    if ldsu_device["enabled"] and attributes["type"] == "input":
                        #print(ldsu_device)
                        #print(attributes)
                        #printf("{} {}".format(attributes["class"], attributes["format"] ))
                        #printf("{}".format(int(attributes["accuracy"]) ))
                        #printf("{} {}".format(int(attributes["minmax"][0]), int(attributes["minmax"][1]) ))
                        value = get_random_data_ex(attributes["format"], int(attributes["accuracy"]), int(attributes["minmax"][0]), int(attributes["minmax"][1]))
                        value = str(value)
                        printf("{} {} {} {} {} {}".format(value, attributes["class"], attributes["format"], int(attributes["accuracy"]), int(attributes["minmax"][0]), int(attributes["minmax"][1]) ))
                        has_enabled = True
                    else:
                        value = "NaN"
                else:
                    value = "NaN"
                values.append(value)

            # if one of the LDSU device is enabled, then publish
            if has_enabled:
                payload = {}
                payload["UID"] = ldsu_key
                payload["TS"] = str(int(time.time()))
                payload["SNS"] = values
                printf_json(payload)
                publish(topic, payload)

    def process_input_devices(self):
        topic = "{}{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_DEVICE_ID, CONFIG_SEPARATOR, API_PUBLISH_SENSOR_READING)

        # sample MQTT packet for sensor data publishing
        # 1. only ENABLED properties shall be included
        # 2. I2CX can have multiple entries (as multiple I2C devices on slot X can be enabled at the same time)
        # 3. the backend performs the mapping to the corresponding sensorname given the address/class
        # 4. the backed will compute the lowest and highest values as displayed in the UI. 
        #    it will update the lowest and highest as needed based on the provided "value" 
        # 5. the frontend will use the "unit" from the JSON file.
        sensors = { 
#                "i2c1":    [{"class": 0, "value": 1, "address": 1}, ...],
#                "i2c2":    [{"class": 1, "value": 2, "address": 2}, ...],
#                "i2c3":    [{"class": 2, "value": 3, "address": 3}, ...],
#                "i2c4":    [{"class": 3, "value": 4, "address": 4}, ...],
#                "adc1":    [{"class": 0, "value": 1}],
#                "adc2":    [{"class": 1, "value": 2}],
#                "1wire1":  [{"class": 2, "value": 3}],
#                "tprobe1": [{"class": 3, "value": 4, subclass: {"class": 4, "value": 5}}],
        }

        num_entries = 0

        # process ENABLED i2c INPUT devices
        for x in range(len(g_i2c_properties)):
            i2c = "i2c{}".format(x+1)
            entries = []
            for y in g_i2c_properties[x]:
                entry = {}
                # i2c device address should be > 0
                # i2c device should be enabled
                # i2c device class should be of type INPUT
                if (int(y) > 0 and g_i2c_properties[x][y]["enabled"]):
                    i2c_class = g_device_classes[g_i2c_properties[x][y]["class"]]
                    if i2c_class == "potentiometer" or i2c_class == "temperature":
                        entry["address"] = int(y)
                        entry["value"] = get_random_data(i2c_class)
                        entry["class"] = g_i2c_properties[x][y]["class"]
                        entries.append(entry)
            if len(entries):
                sensors[i2c] = entries 
                num_entries += 1

        # process ENABLED adc devices
        for x in range(len(g_adc_properties)):
            adc = "adc{}".format(x+1)
            # adc device address should be > 0
            # adc device should be enabled
            if (g_adc_properties[x]["enabled"]):
                adc_class = g_device_classes[g_adc_properties[x]["class"]]
                if adc_class == "anemometer" or adc_class == "potentiometer" or adc_class == "battery" or adc_class == "fluid":
                    entry = {}
                    entry["value"] = get_random_data(adc_class)
                    entry["class"] = g_adc_properties[x]["class"]
                    if not sensors.get(adc):
                        sensors[adc] = []
                    sensors[adc].append(entry)
                    num_entries += 1

        # process ENABLED 1wire devices
        for x in range(len(g_1wire_properties)):
            onewire = "1wire{}".format(x+1)
            # 1wire device address should be > 0
            # 1wire device should be enabled
            if (g_1wire_properties[x]["enabled"]):
                onewire_class = g_device_classes[g_1wire_properties[x]["class"]]
                if onewire_class == "temperature":
                    entry = {}
                    entry["value"] = get_random_data(onewire_class)
                    entry["class"] = g_1wire_properties[x]["class"]
                    if not sensors.get(onewire):
                        sensors[onewire] = []
                    sensors[onewire].append(entry)
                    num_entries += 1

        # process ENABLED tprobe devices
        for x in range(len(g_tprobe_properties)):
            tprobe = "tprobe{}".format(x+1)
            # tprobe device address should be > 0
            # tprobe device should be enabled
            if (g_tprobe_properties[x]["enabled"]):
                tprobe_class = g_device_classes[g_tprobe_properties[x]["class"]]

                # handle subclass
                tprobe_subclass = g_device_classes[g_tprobe_properties[x]["subclass"]]

                if tprobe_class == "temperature" and tprobe_subclass == "humidity":
                    entry = {}
                    entry["value"] = get_random_data(tprobe_class)
                    entry["class"] = g_tprobe_properties[x]["class"]

                    # handle subclass
                    entry["subclass"] = {}
                    entry["subclass"]["value"] = get_random_data(tprobe_subclass)
                    entry["subclass"]["class"] = g_tprobe_properties[x]["subclass"]

                    g_tprobe_properties[x]["class"]
                    if not sensors.get(tprobe):
                        sensors[tprobe] = []
                    sensors[tprobe].append(entry)
                    num_entries += 1

        # if any of the I2C INPUT/ADC/1WIRE/TPROBE devices are enabled, then send a packet
        if num_entries > 0:
            payload = {}
            if CONFIG_ADD_SENSOR_DATA_TIMESTAMP:
                payload["timestamp"] = int(time.time())
            payload["sensors"] = sensors
            printf("")
            global start_timeX
            start_timeX = time.time()
            #printf(start_timeX)
            publish(topic, payload)
        else:
            #printf("no enabled sensor")
            pass

    def process_output_devices(self):
        # process ENABLED i2c OUTPUT devices
        for x in range(len(g_i2c_properties)):
            for y in g_i2c_properties[x]:
                # i2c device address should be > 0
                # i2c device should be enabled
                if (int(y) > 0 and g_i2c_properties[x][y]["enabled"]):
                    topic = "{}{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_DEVICE_ID, CONFIG_SEPARATOR, API_REQUEST_SENSOR_READING)
                    payload = {}
                    payload["sensors"] = []

                    i2c_class = g_device_classes[g_i2c_properties[x][y]["class"]]
                    if i2c_class == "light":
                        # if LIGHT class
                        #printf("xxx {}".format(g_i2c_properties[x][y]))
                        if g_i2c_properties[x][y]["attributes"]["color"]["usage"] == 0:
                            # if RGB as color
                            hw_color = g_i2c_properties[x][y]["attributes"]["color"]["single"]["endpoint"]
                            if hw_color == 1:
                                entry = g_i2c_properties[x][y]["attributes"]["color"]["single"]["hardware"]
                                payload["sensors"].append(entry)
                        else: #if g_i2c_properties[x][y]["attributes"]["color"]["usage"] == 1:
                            # if RGB as component
                            hw_red   = g_i2c_properties[x][y]["attributes"]["color"]["individual"]["red"]["endpoint"]
                            hw_green = g_i2c_properties[x][y]["attributes"]["color"]["individual"]["green"]["endpoint"]
                            hw_blue  = g_i2c_properties[x][y]["attributes"]["color"]["individual"]["blue"]["endpoint"]
                            if hw_red == 1 or hw_green == 1 or hw_blue == 1:
                                if hw_red:
                                    entry = g_i2c_properties[x][y]["attributes"]["color"]["individual"]["red"]["hardware"]
                                    payload["sensors"].append(entry)
                                if hw_green:
                                    entry = g_i2c_properties[x][y]["attributes"]["color"]["individual"]["green"]["hardware"]
                                    payload["sensors"].append(entry)
                                if hw_blue:
                                    entry = g_i2c_properties[x][y]["attributes"]["color"]["individual"]["blue"]["hardware"]
                                    payload["sensors"].append(entry)
                        payload["source"] = {"peripheral": "I2C", "number": x+1, "address": int(y), "class": g_i2c_properties[x][y]["class"]}
                        printf("")
                        publish(topic, payload)
                        printf("")
                    elif i2c_class == "display":
                        # if DISPLAY class
                        #printf("xxx {}".format(g_i2c_properties[x][y]))
                        if g_i2c_properties[x][y]["attributes"]["endpoint"] == 1:
                            entry = g_i2c_properties[x][y]["attributes"]["hardware"]
                            payload["sensors"].append(entry)
                            payload["source"] = {"peripheral": "I2C", "number": x+1, "address": int(y), "class": g_i2c_properties[x][y]["class"]}
                            printf("")
                            publish(topic, payload)
                            printf("")

    def process_trigger_notification(self):
        self.notification_counter += 1
        if self.notification_counter >= self.notification_max:
            self.notification_counter = 0
            menos_publish(MENOS_EMAIL)
            #menos_publish(MENOS_MOBILE)

    def run(self):
        #printf("")
        #printf("TimerThread {}".format(g_messaging_client.is_connected()))
        while not self.stopped.wait(self.timeout) and g_messaging_client.is_connected():
            if self.pause == False:

                # For LDSU sensor
                if True:
                    self.process_ldsu_input_devices()

                # For I2C, ADC, TPROBE, 1WIRE
                if False:
                    self.process_input_devices()

                #self.process_output_devices()
                if False:
                    if CONFIG_SEND_NOTIFICATION_PERIODICALLY:
                        self.process_trigger_notification()
            else:
                #printf("Device is currently stopped! Not sending any sensor data.")
                pass

            # receovery when backend is down but comes back
            if g_device_status == DEVICE_STATUS_CONFIGURING:
                req_configuration()
        #printf("")
        printf("TimerThread exit! {}".format(g_messaging_client.is_connected()))


class HeartbeatThread(threading.Thread):

    def __init__(self, event, timeout):
        threading.Thread.__init__(self)
        self.stopped = event
        self.timeout = timeout
        self.pause = False
        self.exit = False

    def set_timeout(self, timeout):
        self.timeout = timeout

    def set_pause(self, pause=True):
        self.pause = pause

    def set_exit(self):
        self.exit = True

    def run(self):
        #printf("")
        #printf("HeartbeatThread {}".format(g_messaging_client.is_connected()))
        pub_heartbeat()
        while not self.stopped.wait(self.timeout) and g_messaging_client.is_connected():
            if self.pause == False:
                pub_heartbeat()

        #printf("")
        printf("HeartbeatThread exit! {}".format(g_messaging_client.is_connected()))


class DownloadThread(threading.Thread):

    def __init__(self, event=None, timeout=None):
        threading.Thread.__init__(self)
        self.stopped = event
        self.timeout = timeout
        self.filename = None
        self.filesize = 0
        self.fileversion = None
        self.filechecksum = None
        self.use_filename = None
        self.start_time = 0

        # for download via MQTT
        self.downloadedsize = 0

    def set_parameters(self, filename, filesize, fileversion, filechecksum):
        self.filename = filename
        self.filesize = filesize
        self.fileversion = fileversion
        self.filechecksum = filechecksum
        index = filename.rindex("/")
        if index == -1:
            index = 0
        else:
            index += 1
        self.use_filename = filename[index:]

    # for download via MQTT
    def get_filename(self):
        return self.use_filename

    # for download via MQTT
    def set_downloaded(self, downloadedsize):
        self.downloadedsize += downloadedsize

    # compute check using crc32
    def compute_checksum(self):
        f = open(self.use_filename, "rb")
        bin = f.read()
        f.close()
        checksum = binascii.crc32(bin)
        return checksum

    def send_completion_status(self, status):
        time.sleep(1)
        result = "completed" if status == True else "failed" 

        # send completion status
        topic = "{}{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_DEVICE_ID, CONFIG_SEPARATOR, API_UPGRADE_FIRMWARE_COMPLETION)
        payload = {"value": {"result": result}}
        printf("")
        printf("Sending OTA completion status: {}\r\n".format(result))
        printf("")
        publish(topic, payload)

        # display status
        if status == True:
            printf("Downloaded firmware to {} {} bytes in {} secs !!!".format(self.use_filename, self.filesize, round(time.time()-self.start_time) ))
            printf("")
        else:
            printf("The firmware failed to download !!!")
            printf("")
        printf("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        printf("")
        printf("")
        printf("")

    def process_result(self):
        result = True

        # compute checksum
        checksum = self.compute_checksum()

        # check file size
        if self.filesize == self.downloadedsize:
            printf("")
            printf("File size correct: {} [0x{:02X}]".format(self.downloadedsize, self.downloadedsize))
        else:
            result = False
            printf("")
            printf("File size incorrect: {} [0x{:02X}] != {} [0x{:02X}]".format(self.downloadedsize, self.downloadedsize, self.filesize, self.filesize))

        # check checksum
        if self.filechecksum == checksum:
            printf("")
            printf("CRC32 checksum correct: {} [0x{:02X}]".format(checksum, checksum))
        else:
            result = False
            printf("")
            printf("CRC32 checksum incorrect: {} [0x{:02X}] != {} [0x{:02X}]".format(checksum, checksum, self.filechecksum, self.filechecksum))
        return result

    def send_request_firmware(self):
        topic = "{}{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_DEVICE_ID, CONFIG_SEPARATOR, API_REQUEST_FIRMWARE)
        payload = {
            "location": self.filename,
            "offset": self.downloadedsize,
            "size": CONFIG_OTA_DOWNLOAD_FIRMWARE_MQTTS_CHUNK_SIZE
        }
        publish(topic, payload, debug=False)

    def run(self):
        self.start_time = time.time()

        result = False
        if not CONFIG_OTA_DOWNLOAD_FIRMWARE_VIA_MQTTS:
            printf("Downloading firmware via HTTPS ...")
            printf("")
            result, self.downloadedsize = http_get_firmware_binary(self.filename, self.filesize)
            if result:
                result = self.process_result()
            self.send_completion_status(result)
        else:
            printf("Downloading firmware via MQTTS ...")
            printf("")
            self.downloadedsize = 0
            while g_messaging_client.is_connected() and self.downloadedsize < self.filesize:
                while self.stopped.wait(self.timeout):
                    if self.downloadedsize < self.filesize:
                        self.stopped.clear()
                        self.send_request_firmware()
                    else:
                        result = self.process_result()
                        self.send_completion_status(result)
                        break

        # set the version number
        if result:
            global g_firmware_version_STR
            g_firmware_version_STR = self.fileversion
            write_file_version(g_firmware_version_STR)

        # start the timer thread and heartbeat thread
        time.sleep(g_timer_thread_timeout)
        g_timer_thread.set_pause(False)
        g_heartbeat_thread.set_pause(False)


###################################################################################
# UART Command handling
###################################################################################

UART_ATCOMMAND_MOBILE              = "AT+M"
UART_ATCOMMAND_EMAIL               = "AT+E"
UART_ATCOMMAND_NOTIFY              = "AT+N"
UART_ATCOMMAND_MODEM               = "AT+O"
UART_ATCOMMAND_STORAGE             = "AT+S"
UART_ATCOMMAND_DEFAULT             = "AT+D"
UART_ATCOMMAND_CONTINUE            = "ATC"
UART_ATCOMMAND_ECHO                = "ATE"
UART_ATCOMMAND_HELP                = "ATH"
UART_ATCOMMAND_INFO                = "ATI"
UART_ATCOMMAND_MORE                = "ATM"
UART_ATCOMMAND_PAUSE               = "ATP"
UART_ATCOMMAND_RESET               = "ATR"
UART_ATCOMMAND_UPDATE              = "ATU"
UART_ATCOMMAND_STATUS              = "AT"

UART_ATCOMMAND_LDSTEST             = "ATT"


UART_ATCOMMAND_DESC_MOBILE         = "Send message as SMS to verified mobile number"
UART_ATCOMMAND_DESC_EMAIL          = "Send message as email to verified email address"
UART_ATCOMMAND_DESC_NOTIFY         = "Send message as mobile app notification to verified user"
UART_ATCOMMAND_DESC_MODEM          = "Send message to other IoT modem devices"
UART_ATCOMMAND_DESC_STORAGE        = "Send message to storage"
UART_ATCOMMAND_DESC_DEFAULT        = "Send default message to configured endpoints"
UART_ATCOMMAND_DESC_CONTINUE       = "Continue device functions"
UART_ATCOMMAND_DESC_ECHO           = "Echo on/off (toggle)"
UART_ATCOMMAND_DESC_HELP           = "Display help information on commands"
UART_ATCOMMAND_DESC_INFO           = "Display device information"
UART_ATCOMMAND_DESC_MORE           = "Display more information on error"
UART_ATCOMMAND_DESC_PAUSE          = "Pause/Resume (toggle)"
UART_ATCOMMAND_DESC_RESET          = "Reset device"
UART_ATCOMMAND_DESC_UPDATE         = "Enter firmware update (UART entry point inside bootloader)"
UART_ATCOMMAND_DESC_STATUS         = "Display device status"

UART_ATCOMMAND_DESC_LDSTEST        = "Simulate tests for moving/adding/removing LDSU in LDS BUS"


MENOS_MOBILE                       = "mobile"
MENOS_EMAIL                        = "email"
MENOS_NOTIFICATION                 = "notification"
MENOS_MODEM                        = "modem"
MENOS_STORAGE                      = "storage"
MENOS_DEFAULT                      = "default"


##############################################################################################################
# Notification triggering
##############################################################################################################
# UART
# server/<deviceid>/trigger_notification/<peripheral>/<menos>
# {
#   "recipient": string (optional),
#   "message": string (optional)
# }
#
# GPIO/ADC/1WIRE/TPROBE
# server/<deviceid>/trigger_notification/<peripheral><number>/<menos>
# {
#   "recipient": string (optional),
#   "message": string (optional),
#   "activate": int
# }
#
# I2C
# server/<deviceid>/trigger_notification/<peripheral><number>/<menos>/<address>
# {
#   "recipient": string (optional),
#   "message": string (optional),
#   "activate": int
# }
#
##############################################################################################################

def menos_publish(menos, recipient=None, message=None, peripheral="uart", number="", address=None, activate=None):
    if address is None:
        topic = "{}/{}/trigger_notification/{}{}/{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_DEVICE_ID, peripheral, number, menos)
    else:
        topic = "{}/{}/trigger_notification/{}{}/{}/{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_DEVICE_ID, peripheral, number, menos, address)
    payload = {}
    if recipient is not None:
        payload["recipient"] = recipient
    if message is not None:
        payload["message"] = message
    if activate is not None:
        payload["activate"] = activate
    publish(topic, payload)

def uart_parse_command(cmd):
    recipient = None
    message = None
    result = 1

    if cmd[0] != "+":
        printf("Wrong syntax")
        printf("")
        return 0, None, None

    cmd_list = cmd[1:].split("+", 2)
    if len(cmd_list) == 0:
        printf("Wrong syntax")
        printf("")
        return 0, None, None
    elif len(cmd_list) == 1:
        recipient = cmd_list[0]
    else:
        recipient = cmd_list[0]
        if len(recipient) == 0:
            recipient = None
        else:
            if recipient[0] == "'":
                recipient_len = len(recipient)
                if recipient[recipient_len-1] != "'":
                    printf("Wrong syntax")
                    printf("")
                    return 0, None, None
                recipient = recipient[1: recipient_len-1]
            elif recipient[0] == '"':
                recipient_len = len(recipient)
                if recipient[recipient_len-1] != '"':
                    printf("Wrong syntax")
                    printf("")
                    return 0, None, None
                recipient = recipient[1: recipient_len-1]

        message = cmd_list[1]
        if len(message) == 0:
            message = None
        else:
            if message[0] == "'":
                message_len = len(message)
                if message[message_len-1] != "'":
                    printf("Wrong syntax")
                    printf("")
                    return 0, None, None
                message = message[1: message_len-1]
            elif message[0] == '"':
                message_len = len(message)
                if message[message_len-1] != '"':
                    printf("Wrong syntax")
                    printf("")
                    return 0, None, None
                message = message[1: message_len-1]

        if recipient is None and message is None:
            printf("Wrong syntax")
            printf("")
            return 0, None, None

    return result, recipient, message

def uart_cmdhdl_common(idx, cmd, menos):
    if len(cmd) == len(UART_ATCOMMANDS[idx]["command"]):
        menos_publish(menos)
        return
    result, recipient, message = uart_parse_command(cmd[len(UART_ATCOMMANDS[idx]["command"]):])
    if result:
        menos_publish(menos, recipient, message)

def uart_cmdhdl_mobile(idx, cmd):
    uart_cmdhdl_common(idx, cmd, MENOS_MOBILE)

def uart_cmdhdl_email(idx, cmd):
    uart_cmdhdl_common(idx, cmd, MENOS_EMAIL)

def uart_cmdhdl_notification(idx, cmd):
    uart_cmdhdl_common(idx, cmd, MENOS_NOTIFICATION)

def uart_cmdhdl_mOdem(idx, cmd):
    uart_cmdhdl_common(idx, cmd, MENOS_MODEM)

def uart_cmdhdl_storage(idx, cmd):
    uart_cmdhdl_common(idx, cmd, MENOS_STORAGE)

def uart_cmdhdl_default(idx, cmd):
    if len(cmd) == len(UART_ATCOMMANDS[idx]["command"]):
        # below are sample test cases for I2C notification triggering
        #menos_publish(MENOS_EMAIL, None, None, "i2c", 1, 40, 1)
        #menos_publish(MENOS_EMAIL, None, None, "i2c", 1, 40, 0)
        menos_publish(MENOS_DEFAULT)
        return

def uart_cmdhdl_help(idx, cmd):
    printf("")
    printf('UART Commands:')
    for command in UART_ATCOMMANDS:
        printf("{}\t{}".format(command["command"], command["help"]))
    printf('')

def uart_cmdhdl_unsupported(idx, cmd):
    printf("uart_cmdhdl_unsupported")

def uart_cmdhdl_ldstest_help():
    printf("")
    printf("LDS Test Commands:")
    printf("ATT+LS+<PORT>                List LDSUs in LDS BUS port (1, 2, 3)")
    printf("                             If no port, will list LDSUs in all ports")
    printf("ATT+MOV+<UID>+<PORT>         Move an LDSU from one port to another port")
    printf("ATT+ADD+<OBJ>+<PORT>+<UID>   Plug an LDSU of type OBJ to specified port")
    printf("                             Available OBJ = [32768, 32770]")
    printf("                             UID is optional (to re-add what you removed)")
    printf("ATT+REM+<UID>                Unplug an LDSU")
    printf("")

def uart_cmdhdl_ldstest(idx, cmd):
    if len(cmd) == len(UART_ATCOMMANDS[idx]["command"]):
        uart_cmdhdl_ldstest_help()
        return

    cmd_list = cmd.split("+")[1:]
    if cmd_list[0] == "LS":
        params = cmd_list[1:]
        if len(params) != 1:
            listLDSUs(0)
            return
        port = int(params[0])
        listLDSUs(port)

    elif cmd_list[0] == "MOV":
        params = cmd_list[1:]
        if len(params) != 2:
            printf("invalid {} parameters".format(cmd_list[0]))
            return
        uid = params[0]
        port = int(params[1])
        moveLDSU(uid, port)

    elif cmd_list[0] == "ADD":
        params = cmd_list[1:]
        if len(params) < 2:
            printf("invalid {} parameters".format(cmd_list[0]))
            return
        obj = params[0]
        port = int(params[1])
        if len(params) == 2:
            uid = None
        elif len(params) == 3:
            uid = params[2]
        plugLDSU(obj, port, uid)

    elif cmd_list[0] == "REM":
        params = cmd_list[1:]
        if len(params) != 1:
            printf("invalid {} parameters".format(cmd_list[0]))
            return
        uid = params[0]
        unplugLDSU(uid)

    else:
        printf("invalid command")
        return


UART_ATCOMMANDS = [
    { "command": UART_ATCOMMAND_MOBILE,   "fxn": uart_cmdhdl_mobile,       "help": UART_ATCOMMAND_DESC_MOBILE  },
    { "command": UART_ATCOMMAND_EMAIL,    "fxn": uart_cmdhdl_email,        "help": UART_ATCOMMAND_DESC_EMAIL   },
    { "command": UART_ATCOMMAND_NOTIFY,   "fxn": uart_cmdhdl_notification, "help": UART_ATCOMMAND_DESC_NOTIFY  },
    { "command": UART_ATCOMMAND_MODEM,    "fxn": uart_cmdhdl_mOdem,        "help": UART_ATCOMMAND_DESC_MODEM   },
    { "command": UART_ATCOMMAND_STORAGE,  "fxn": uart_cmdhdl_storage,      "help": UART_ATCOMMAND_DESC_STORAGE },
    { "command": UART_ATCOMMAND_DEFAULT,  "fxn": uart_cmdhdl_default,      "help": UART_ATCOMMAND_DESC_DEFAULT },

    { "command": UART_ATCOMMAND_HELP,     "fxn": uart_cmdhdl_help,         "help": UART_ATCOMMAND_DESC_HELP     },
    { "command": UART_ATCOMMAND_LDSTEST,  "fxn": uart_cmdhdl_ldstest,      "help": UART_ATCOMMAND_DESC_LDSTEST  },
    #{ "command": UART_ATCOMMAND_CONTINUE, "fxn": uart_cmdhdl_unsupported,  "help": UART_ATCOMMAND_DESC_CONTINUE },
    #{ "command": UART_ATCOMMAND_ECHO,     "fxn": uart_cmdhdl_unsupported,  "help": UART_ATCOMMAND_DESC_ECHO     },
    #{ "command": UART_ATCOMMAND_INFO,     "fxn": uart_cmdhdl_unsupported,  "help": UART_ATCOMMAND_DESC_INFO     }, # = {software version, present configuration, present status, list of I2C devices and addresses, IP address, connection status to service, etc}" },
    #{ "command": UART_ATCOMMAND_MORE,     "fxn": uart_cmdhdl_unsupported,  "help": UART_ATCOMMAND_DESC_MORE     },
    #{ "command": UART_ATCOMMAND_PAUSE,    "fxn": uart_cmdhdl_unsupported,  "help": UART_ATCOMMAND_DESC_PAUSE    },
    #{ "command": UART_ATCOMMAND_RESET,    "fxn": uart_cmdhdl_unsupported,  "help": UART_ATCOMMAND_DESC_RESET    },
    #{ "command": UART_ATCOMMAND_UPDATE,   "fxn": uart_cmdhdl_unsupported,  "help": UART_ATCOMMAND_DESC_UPDATE   },

    #{ "command": UART_ATCOMMAND_STATUS,   "fxn": uart_cmdhdl_mobile,       "help": UART_ATCOMMAND_DESC_STATUS   }, # OK if all is good, ERROR if device is in error state" },
]

def read_kbd_input(inputQueue):

    #printf("")
    #printf("read_kbd_input")

    while g_messaging_client.is_connected():
        if g_device_status == DEVICE_STATUS_RUNNING:
            break
        time.sleep(1)

    if g_messaging_client.is_connected():
        uart_cmdhdl_help(0, None)

        while g_messaging_client.is_connected():
            input_str = input()
            inputQueue.put(input_str)

    g_input_thread = None

    #printf("")
    #printf("read_kbd_input exit!")


###################################################################################
# HTTPS client
###################################################################################

def http_write_to_file(filename, contents):
    index = filename.rindex("/")
    if index == -1:
        index = 0
    else:
        index += 1
    new_filename = filename[index:]
    f = open(new_filename, "wb")
    f.write(contents)
    f.close()

def http_initialize_connection(host=CONFIG_HTTP_HOST):
    if True:
        context = ssl._create_unverified_context()
    else:
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_REQUIRED
        #context.load_cert_chain(config.CONFIG_TLS_CERT, config.CONFIG_TLS_PKEY)
        #context.load_verify_locations(
        #    config.CONFIG_TLS_CERT, config.CONFIG_TLS_CERT, config.CONFIG_TLS_PKEY)
        #context.check_hostname = False
    conn = http.client.HTTPSConnection(host, CONFIG_HTTP_TLS_PORT, context=context, timeout=CONFIG_HTTP_TIMEOUT)
    return conn

def http_send_request(conn, req_type, req_api, params, headers, debug=True):
    try:
        if headers:
            if debug:
                printf("http_send_request")
                printf("  {}:{}".format(CONFIG_HTTP_HOST, CONFIG_HTTP_TLS_PORT))
                printf("  {} {}".format(req_type, req_api))
                printf("  {}".format(headers))
                if params:
                    printf("  {}".format(params))
            conn.request(req_type, req_api, params, headers)
            if debug:
                printf("http_send_request")
                printf("")
        else:
            conn.request(req_type, req_api, params)
        return True
    except:
        printf("REQ: Could not communicate with WEBSERVER! {}".format(""))
    return False

def http_recv_response(conn, debug=True):
    try:
        if debug:
            printf("http_recv_response")
        r1 = conn.getresponse()
        if debug:
            printf("http_recv_response")
            printf("  {} {} {}".format(r1.status, r1.reason, r1.length))
            printf("")
        if r1.status == 200:
            file_size = r1.length
            #printf("response = {} {} [{}]".format(r1.status, r1.reason, r1.length))
            if file_size:
                data = r1.read(file_size)
            return file_size, data
        else:
            printf("RES: Could not communicate with DEVICE! {}".format(r1.status))
            return 0, None
    except Exception as e:
        printf("RES: Could not communicate with DEVICE! {}".format(e))
    return 0, None

def http_get_firmware_binary(filename, filesize):
    global CONFIG_DEVICE_ID
    global CONFIG_USERNAME
    global CONFIG_PASSWORD

    # in order for the device secret key to not be compromise easily,
    # we now retrieve the authcode via an HTTPS API
    # this prevents from compromising the device secret_key
    # later we disable the API in nginx.conf so that the API cannot be used in production
    authcode = http_compute_ota_authcode(CONFIG_DEVICE_ID, CONFIG_USERNAME, CONFIG_PASSWORD)
    if authcode is None:
        printf("ERROR: Failed retrieving ota authcode!")
        return False


    conn = http_initialize_connection()
    #headers = { "Content-type": "application/octet-stream", "Accept-Ranges": "bytes", "Content-Length": filesize }
    #headers = { "User-Agent": "PostmanRuntime/7.22.0", "Accept": "*/*", "Host": "ec2-54-166-169-66.compute-1.amazonaws.com", "Accept-Encoding": "gzip, deflate, br", "Connection": "keep-alive" }
    headers = { "Connection": "keep-alive", "Authorization": "Bearer " + authcode }
    length = 0
    api = "/firmware"
    result = http_send_request(conn, "GET", api + "/" + filename, None, headers)
    if result:
        length, response = http_recv_response(conn)
        if length == 0:
            printf("http_recv_response error")
            conn.close()
            return False, length
        if length != filesize:
            printf("error length {} != filesize {}".format(length, filesize))
            conn.close()
            return False, length
        try:
            http_write_to_file(filename, response)
        except Exception as e:
            printf("exception {}".format(e))
            conn.close()
            return False, length
    conn.close()
    return result, length

def http_compute_ota_authcode(uuid, username, password):

    otaauthcode = None

    # initialize HTTPS connection with a specific server for the ota authcode
    if "brtchip-iotportal.com" in CONFIG_HTTP_HOST:
        # for local setup, use the DEV cloud
        conn = http_initialize_connection(host=CONFIG_HTTP_HOST)
    else:
        # for local setup, use the DEV cloud
        conn = http_initialize_connection(host="dev.brtchip-iotportal.com")

    headers = { "Connection": "keep-alive", "Content-Type": "application/json" }
    params = json.dumps({ "uuid": uuid, "username": username, "password": password })
    api = "/devicesimulator/otaauthcode"

    result = http_send_request(conn, "GET", api, params, headers, debug=False)
    if result:
        length, response = http_recv_response(conn, debug=False)
        if length == 0:
            printf("http_recv_response error")
            conn.close()
            return None
        try:
            response = json.loads(response)
            otaauthcode = response["otaauthcode"]
        except Exception as e:
            printf("exception {}".format(e))
            conn.close()
            return None
    conn.close()
    return otaauthcode

def http_compute_device_password(uuid, serial_number, mac_address):

    password = None

    # initialize HTTPS connection with a specific server for the device password API
    if "brtchip-iotportal.com" in CONFIG_HTTP_HOST:
        # for local setup, use the DEV cloud
        conn = http_initialize_connection(host=CONFIG_HTTP_HOST)
    else:
        # for local setup, use the DEV cloud
        conn = http_initialize_connection(host="dev.brtchip-iotportal.com")

    headers = { "Connection": "keep-alive", "Content-Type": "application/json" }
    params = json.dumps({ "uuid": uuid, "serialnumber": serial_number, "poemacaddress": mac_address })
    api = "/devicesimulator/devicepassword"

    result = http_send_request(conn, "GET", api, params, headers, debug=False)
    if result:
        length, response = http_recv_response(conn, debug=False)
        if length == 0:
            printf("http_recv_response error")
            conn.close()
            return None
        try:
            response = json.loads(response)
            password = response["password"]
        except Exception as e:
            printf("exception {}".format(e))
            conn.close()
            return None
    conn.close()
    return password


###################################################################################
# File version
###################################################################################

# Write version to file (for OTA feature)
def write_file_version(ver):

    filename = CONFIG_DEVICE_ID + ".ver"

    try:
        json_obj = { "version": ver }
        f = open(filename, "w")
        f.write(json.dumps(json_obj))
        f.close()
    except:
        pass

# Read version from file (for OTA feature)
def read_file_version(ver):

    version = ver
    filename = CONFIG_DEVICE_ID + ".ver"

    try:
        f = open(filename, "r")
        json_obj = f.read()
        f.close()
        json_obj = json.loads(json_obj)
        version = json_obj["version"]
    except:
        write_file_version(ver)

    return version


###################################################################################
# Registration of sensors
###################################################################################

# Read registered sensors from .sns file
def read_registered_sensors_eeprom():

    filename = CONFIG_DEVICE_ID + ".sns"

    try:
        f = open(filename, "r")
        json_obj = f.read()
        f.close()
        json_obj = json.loads(json_obj)
        sensors = json_obj["sensors"]
    except Exception as e:
        sensors = []

    printf("Read registered sensors {}".format(len(sensors)))
    return sensors

# OLD
# Send registered sensors from .sns file
def set_registration(sensors):
    topic = "{}{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_DEVICE_ID, CONFIG_SEPARATOR, API_SET_REGISTRATION)
    payload = {"value": sensors}
    #payload = json.dumps(payload)
    publish(topic, payload)

# Register gateway descriptor
def reg_gateway_descriptor():
    printf("")
    printf("Register gateway descriptor")
    topic = "{}{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_DEVICE_ID, CONFIG_SEPARATOR, API_SET_DESCRIPTOR)
    if g_gateway_descriptor["UUID"] == "":
        g_gateway_descriptor["UUID"] = CONFIG_DEVICE_ID
        g_gateway_descriptor["SNO"]  = CONFIG_DEVICE_SERIAL
        g_gateway_descriptor["PMAC"] = CONFIG_DEVICE_MACADD
    payload = {"value": g_gateway_descriptor}
    publish(topic, payload)

# Register LDSU descriptors
def reg_ldsu_descriptors(port=None, as_response=False):
    printf("")
    printf("Register LDSU descriptors")

    if True: #port is None:
        # send all LDSUs in chunks
        if True:
            # send LDSU descriptors in multiple MQTT packets of 1kb chunks (about 5 LDSUs possible, 172 each = 860)
            topic = "{}{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_DEVICE_ID, CONFIG_SEPARATOR, API_SET_LDSU_DESCS)
            chunks = 0
            maxchunksize = 1024
            size = 0
            ldsu_descriptors = []
            total_chunks = math.ceil(len(g_ldsu_descriptors)/5)

            for x in range(len(g_ldsu_descriptors)):
                estimated_len = len(json.dumps(ldsu_descriptors)) + len(json.dumps(g_ldsu_descriptors[x])) + len("{value:[]}")
                if estimated_len < maxchunksize:
                    # adding the descriptor will still fit the maxchunksize
                    ldsu_descriptors.append(g_ldsu_descriptors[x])
                    size = len(json.dumps(ldsu_descriptors))
                else:
                    # adding the descriptor will no longer fit the maxchunksize
                    # so send the descriptors in the list
                    payload = {
                        "value": ldsu_descriptors, 
                        "chunk": { "SEQN": str(chunks), "TSEQ": str(total_chunks), "TOT": str(len(g_ldsu_descriptors)) } 
                    }
                    printf(estimated_len)
                    printf(len(json.dumps(payload)))
                    publish(topic, payload)
                    # reset size counter
                    size = 0
                    ldsu_descriptors = []
                    chunks += 1

                    # add current descriptor
                    ldsu_descriptors.append(g_ldsu_descriptors[x])
                    size = len(json.dumps(ldsu_descriptors))
            if size:
                # send the last chunk
                payload = {
                    "value": ldsu_descriptors, 
                    "chunk": { "SEQN": str(chunks), "TSEQ": str(total_chunks), "TOT": str(len(g_ldsu_descriptors)) } 
                }
                printf(len(json.dumps(payload)))
                publish(topic, payload)
                # reset size counter
                size = 0
                ldsu_descriptors = []
                chunks += 1

            # respond to API_GET_LDSU_DESCS (note that above was all to API_SET_LDSU_DESCS)
            if as_response:
                topic = "{}{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_DEVICE_ID, CONFIG_SEPARATOR, API_GET_LDSU_DESCS)
                payload = {}
                publish(topic, payload)

            printf("{} LDSUs registered in {} chunks of max size {}".format(len(g_ldsu_descriptors), chunks, maxchunksize))

        elif False:
            # send LDSU descriptors in 1 MQTT packet
            api = API_SET_LDSU_DESCS
            if as_response:
                api = API_GET_LDSU_DESCS

            topic = "{}{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_DEVICE_ID, CONFIG_SEPARATOR, api)
            payload = {"value": g_ldsu_descriptors}
            for ldsu_descriptor in g_ldsu_descriptors:
                printf(len(json.dumps(ldsu_descriptor)))
            printf(len(json.dumps(payload)))
            publish(topic, payload)

        elif False:
            # send LDSU descriptors in 3 multiple chunks per port
            # (ex. if 80 LDSUs, then can send by port or by any number of LDSUs)
            api = API_SET_LDSU_DESCS
            if as_response:
                api = API_GET_LDSU_DESCS

            topic = "{}{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_DEVICE_ID, CONFIG_SEPARATOR, api)
            for port in range(3):
                ldsu_descriptors = []
                for ldsu_descriptor in g_ldsu_descriptors:
                    if ldsu_descriptor["PORT"] == str(port+1):
                        ldsu_descriptors.append(ldsu_descriptor)
                payload = {"value": ldsu_descriptors}
                publish(topic, payload)
    else:
        api = API_SET_LDSU_DESCS
        if as_response:
            api = API_GET_LDSU_DESCS

        # send all LDSUs for specified port
        topic = "{}{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_DEVICE_ID, CONFIG_SEPARATOR, api)
        ldsu_descriptors = []
        for ldsu_descriptor in g_ldsu_descriptors:
            if ldsu_descriptor["PORT"] == port:
                ldsu_descriptors.append(ldsu_descriptor)
        payload = {"value": ldsu_descriptors}
        publish(topic, payload)


# Initialize Gateway descriptor
def init_gw_descriptor():
    global g_gateway_descriptor
    global g_device_client
    g_gateway_descriptor = g_device_client.get_gw_desc()
    if g_gateway_descriptor is None:
        g_gateway_descriptor = {}
        return False
    g_gateway_descriptor["UUID"] = CONFIG_DEVICE_ID
    g_gateway_descriptor["SNO"]  = CONFIG_DEVICE_SERIAL
    g_gateway_descriptor["PMAC"] = CONFIG_DEVICE_MACADD
    return True

# Initialize LDSU descriptors to ensure unique UID
def init_ldsu_descriptors():
    global g_ldsu_descriptors
    global g_device_client
    g_ldsu_descriptors = g_device_client.get_lds_reg()
    if g_ldsu_descriptors is None:
        g_ldsu_descriptors = []
        return False
    for x in range(len(g_ldsu_descriptors)):
        if g_ldsu_descriptors[x]["UID"] == "BRTXXXXXXXXXXXXX" or g_ldsu_descriptors[x]["UID"] == "":
            g_ldsu_descriptors[x]["UID"] = "{}{:02d}".format(CONFIG_DEVICE_ID, x)
    return True

# Initialize LDSU properties
def init_ldsu_properties():
    global g_ldsu_properties
    global g_device_client
    for ldsu_descriptor in g_ldsu_descriptors:
        source = ldsu_descriptor["UID"]
        obj = ldsu_descriptor["OBJ"]
        numdevices = g_device_client.get_obj_numdevices(obj)
        g_ldsu_properties[source] = []
        for device in range(numdevices):
            g_ldsu_properties[source].append({ 'enabled': 0, 'mode': 0 })


###################################################################################
# Heartbeat
###################################################################################

# Publish heartbeat
def pub_heartbeat():
    topic = "{}{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_DEVICE_ID, CONFIG_SEPARATOR, API_PUBLISH_HEARTBEAT)
    payload = { "TS": str(int(time.time())) }
    publish(topic, payload)


###################################################################################
# Password generation
###################################################################################

def decode_password(secret_key, password):

    return jwt.decode(password, secret_key, algorithms=['HS256'])

def compute_password(secret_key, uuid, serial_number, mac_address, debug=False):

    if not CONFIG_QUERY_BACKEND_TO_COMPUTE_DEVICE_PASSWORD:
        # code removed
        pass
    else:
        printf("CONFIG_QUERY_BACKEND_TO_COMPUTE_DEVICE_PASSWORD")
        # in order for the device secret key to not be compromise easily,
        # we now retrieve the password via an HTTPS API
        # this prevents from compromising the device secret_key
        # later we disable the API in nginx.conf so that the API cannot be used in production
        password = http_compute_device_password(uuid, serial_number, mac_address)
        if password is None:
            printf("ERROR: Failed retrieving password!")

    return password


###################################################################################
# Main entry point
###################################################################################

def parse_arguments(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--USE_ECC',              required=False, default=1 if CONFIG_USE_ECC else 0, help='Use ECC instead of RSA')
    parser.add_argument('--USE_AMQP',             required=False, default=1 if CONFIG_USE_AMQP else 0, help='Use AMQP instead of MQTT')

    parser.add_argument('--USE_DEVICE_SECRETKEY', required=False, default='',                   help='Device Secret Key to use', nargs='?', const='') # added nargs and const for device restart
    parser.add_argument('--USE_DEVICE_ID',        required=False, default='',                   help='Device ID to use')
    parser.add_argument('--USE_DEVICE_SERIAL',    required=False, default='',                   help='Device Serial Number to use')
    parser.add_argument('--USE_DEVICE_MACADD',    required=False, default='',                   help='Device POE MAC Address to use')

    parser.add_argument('--USE_DEVICE_CA',        required=False, default=CONFIG_TLS_CA,        help='Device CA certificate to use')
    parser.add_argument('--USE_DEVICE_CERT',      required=False, default=CONFIG_TLS_CERT,      help='Device certificate to use')
    parser.add_argument('--USE_DEVICE_PKEY',      required=False, default=CONFIG_TLS_PKEY,      help='Device private key to use')

    parser.add_argument('--USE_HOST',             required=False, default=CONFIG_HOST,          help='Host server to connect to')
    parser.add_argument('--USE_PORT',             required=False, default=CONFIG_MQTT_TLS_PORT, help='Host port to connect to')

    # for backward compatibility and troubleshooting purposes
    parser.add_argument('--USE_USERNAME',         required=False, default='',                   help='Username to use in connection', nargs='?', const='') # added nargs and const for device restart
    parser.add_argument('--USE_PASSWORD',         required=False, default='',                   help='Password to use in connection', nargs='?', const='') # added nargs and const for device restart

    return parser.parse_args(argv)

def main(args):

    global g_firmware_version_STR
    global g_messaging_client
    global g_device_client
    global g_device_status
    global g_timer_thread_stop
    global g_timer_thread_timeout
    global g_timer_thread
    global g_heartbeat_thread_stop
    global g_heartbeat_thread_timeout
    global g_heartbeat_thread
    global g_input_thread

    global CONFIG_USE_AMQP
    global CONFIG_USE_ECC
    global CONFIG_SEPARATOR
    global CONFIG_TLS_CA
    global CONFIG_TLS_CERT
    global CONFIG_TLS_PKEY
    global CONFIG_HOST
    global CONFIG_HTTP_HOST
    global CONFIG_MQTT_TLS_PORT
    global CONFIG_AMQP_TLS_PORT

    global CONFIG_DEVICE_SECRETKEY
    global CONFIG_DEVICE_ID
    global CONFIG_DEVICE_SERIAL
    global CONFIG_DEVICE_MACADD
    global CONFIG_USERNAME
    global CONFIG_PASSWORD

    CONFIG_USE_AMQP      = True if int((args.USE_AMQP))==1 else False
    CONFIG_USE_ECC       = True if int((args.USE_ECC))==1 else False
    CONFIG_SEPARATOR     = "." if int((args.USE_AMQP))==1 else "/"
    CONFIG_TLS_CA        = args.USE_DEVICE_CA
    CONFIG_TLS_CERT      = args.USE_DEVICE_CERT
    CONFIG_TLS_PKEY      = args.USE_DEVICE_PKEY
    CONFIG_HOST          = args.USE_HOST
    CONFIG_HTTP_HOST     = args.USE_HOST
    CONFIG_MQTT_TLS_PORT = int(args.USE_PORT)
    CONFIG_AMQP_TLS_PORT = int(args.USE_PORT)

    CONFIG_DEVICE_SECRETKEY = args.USE_DEVICE_SECRETKEY
    CONFIG_DEVICE_ID        = args.USE_DEVICE_ID
    CONFIG_DEVICE_SERIAL    = args.USE_DEVICE_SERIAL
    CONFIG_DEVICE_MACADD    = args.USE_DEVICE_MACADD
    setup_logging(CONFIG_DEVICE_ID + "_logs.txt")

    # Password is now a combination of UUID, Serial Number and POE Mac Address
    # Previously, PASSWORD is just the DEVICE_SERIAL
    #CONFIG_PASSWORD = CONFIG_DEVICE_SERIAL
    if args.USE_USERNAME != '' and args.USE_PASSWORD != '':
        # backward compatibility
        CONFIG_USERNAME = args.USE_USERNAME
        CONFIG_PASSWORD = args.USE_PASSWORD
        CONFIG_DEVICE_SERIAL = args.USE_PASSWORD
        CONFIG_DEVICE_MACADD = "Unknown"
    else:
        CONFIG_USERNAME = CONFIG_DEVICE_ID
        CONFIG_PASSWORD = compute_password(CONFIG_DEVICE_SECRETKEY, CONFIG_DEVICE_ID, CONFIG_DEVICE_SERIAL, CONFIG_DEVICE_MACADD, debug=False)
        if CONFIG_PASSWORD is None:
            return


    printf("-------------------------------------------------------")
    printf("Copyright (C) Bridgetek Pte Ltd")
    printf("-------------------------------------------------------")
    printf("Welcome to IoT Device Simulator...")
    printf("")
    printf("This application simulates FT900 IoT device")
    printf("-------------------------------------------------------")


    # Read file version from file (for OTA feature)
    g_firmware_version_STR = read_file_version(g_firmware_version_STR)

    printf("")
    printf("FIRMWARE VERSION = {}".format(g_firmware_version_STR))

    printf("")
    printf("DEVICE INFO")
    printf("uuid: {}".format(CONFIG_DEVICE_ID))
    printf("ser:  {}".format(CONFIG_DEVICE_SERIAL))
    printf("mac:  {}".format(CONFIG_DEVICE_MACADD))

    printf("")
    printf("TLS CERTIFICATES")
    printf("ca:   {}".format(CONFIG_TLS_CA))
    printf("cert: {}".format(CONFIG_TLS_CERT))
    printf("pkey: {}".format(CONFIG_TLS_PKEY))

    printf("")
    printf("MQTT CREDENTIALS")
    printf("host: {}:{}".format(CONFIG_HOST, CONFIG_MQTT_TLS_PORT))
    printf("id:   {}".format(CONFIG_DEVICE_ID))
    printf("user: {}".format(CONFIG_USERNAME))
    printf("pass: {}".format(CONFIG_PASSWORD))


    # Initialize MQTT/AMQP client
    if CONFIG_USE_AMQP:
        g_messaging_client = messaging_client(CONFIG_USE_AMQP, on_amqp_message, device_id=CONFIG_DEVICE_ID, use_printf=printf)
        g_messaging_client.set_server(CONFIG_HOST, CONFIG_AMQP_TLS_PORT)
    else:
        g_messaging_client = messaging_client(CONFIG_USE_AMQP, on_mqtt_message, device_id=CONFIG_DEVICE_ID, use_ecc=CONFIG_USE_ECC, use_printf=printf)
        g_messaging_client.set_server(CONFIG_HOST, CONFIG_MQTT_TLS_PORT)
    if CONFIG_USERNAME or CONFIG_PASSWORD:
        g_messaging_client.set_user_pass(CONFIG_USERNAME, CONFIG_PASSWORD)
    g_messaging_client.set_tls(CONFIG_TLS_CA, CONFIG_TLS_CERT, CONFIG_TLS_PKEY)


    # Initialize LDSU device (sensor/actuator) client
    lds_filename = CONFIG_DEVICE_ID + ".json"
    g_device_client = device_client.device_client()
    g_device_client.initialize(lds_filename=lds_filename)


    inputThread = None
    while True:

        # Connect to MQTT/AMQP broker
        ignore_hostname = False
        while True:
            try:
                (result, code) = g_messaging_client.initialize(timeout=5, ignore_hostname=ignore_hostname)
                if not result:
                    printf("Could not connect to message broker! {}".format(code))
                    if code == 1:
                        ignore_hostname = True
                else:
                    break
            except:
                printf("Could not connect to message broker! exception!")
                time.sleep(1)

        # Subscribe to messages sent for this device
        time.sleep(1)
        subtopic = "{}{}#".format(CONFIG_DEVICE_ID, CONFIG_SEPARATOR)
        g_messaging_client.subscribe(subtopic, subscribe=True, declare=True, consume_continuously=True)
        # test security, subscribe to other topics
        #subtopic2 = "{}{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_DEVICE_ID, CONFIG_SEPARATOR, API_PUBLISH_SENSOR_READING)
        #g_messaging_client.subscribe(subtopic2, subscribe=True, declare=True, consume_continuously=True)


        # Get epoch time
        # Not needed for the device simulator
        # This is just for demonstration to device firmware (to be used as last resort in case SNTP fails for some reason)
        #req_epochtime()


        # Initialize Gateway and LDSU descriptors and properties to ensure uniqueness per device simulator
        if init_gw_descriptor() == False:
            printf("ERROR: Could not locate GW descriptor template file!")
            return
        if init_ldsu_descriptors() == False:
            printf("ERROR: Could not locate Sample LDS Reg template file!")
            return
        init_ldsu_properties()

        # Register gateway descriptor and ldsu descriptors
        # TODO: send LDSU descriptors in multiple chunks (ex. 80 LDSUs)
        reg_gateway_descriptor()
        reg_ldsu_descriptors()
        time.sleep(1)


        # Scan sensor for configuration
        #if CONFIG_SCAN_SENSORS_AT_BOOTUP:
        #    sensors = read_registered_sensors_eeprom()
        #    if len(sensors):
        #        set_registration(sensors)

        # Delete device configuration
        # OPTIONAL This is not really needed.
        # This just simplifies deleting configuration of the sensors, which can be very useful when debugging configuration issues
        if CONFIG_DELETE_CONFIGURATION:
            del_configuration()

        # Load device configuration from file
        # OPTIONAL This is not really needed.
        # This just simplifies configuration of the sensors, which can be very useful when configuring several sensors
        #if CONFIG_LOAD_CONFIGURATION_FROM_FILE:
        #    time.sleep(1)
        #    set_configuration()


        # Query device configuration
        if CONFIG_REQUEST_CONFIGURATION:
            g_device_status = DEVICE_STATUS_CONFIGURING
            req_configuration()
            time.sleep(1)

        # Check OTA status at bootup
        if CONFIG_OTA_AT_BOOTUP:
            req_otastatus(g_firmware_version_STR)
            time.sleep(1)


        # Start the heartbeat thread
        g_heartbeat_thread_stop = threading.Event()
        g_heartbeat_thread = HeartbeatThread(g_heartbeat_thread_stop, g_heartbeat_thread_timeout)
        g_heartbeat_thread.start()

        # Start the timer thread for sensor processing
        g_timer_thread_stop = threading.Event()
        g_timer_thread = TimerThread(g_timer_thread_stop, g_timer_thread_timeout)
        g_timer_thread.start()

        # Start keyboard input thread for AT commands processing
        if g_input_thread == None:
            inputQueue = queue.Queue()
            g_input_thread = threading.Thread(target=read_kbd_input, args=(inputQueue,), daemon=True)
            g_input_thread.start()


        # Loop processing
        # Exit when disconnection happens
        while g_messaging_client.is_connected():
            time.sleep(1)

            # process restart
            if g_device_status == DEVICE_STATUS_RESTARTING:
                process_restart()
            elif g_device_status == DEVICE_STATUS_STOPPING:
                process_stop()
            elif g_device_status == DEVICE_STATUS_STARTING:
                process_start()
            elif g_device_status == DEVICE_STATUS_RUNNING:
                # process keyboard input
                if inputQueue.qsize() > 0:
                    cmd = inputQueue.get()
                    for idx in range(len(UART_ATCOMMANDS)):
                        if cmd.startswith(UART_ATCOMMANDS[idx]["command"]):
                            UART_ATCOMMANDS[idx]["fxn"](idx, cmd)
                            break


        # Handle graceful disconnection
        g_messaging_client.subscribe(subtopic, subscribe=False)
        time.sleep(2)
        g_messaging_client.release()
        if g_timer_thread:
            g_timer_thread.set_exit()
            g_timer_thread_stop.set()
            g_timer_thread.join()
        if g_heartbeat_thread:
            g_heartbeat_thread.set_exit()
            g_heartbeat_thread_stop.set()
            g_heartbeat_thread.join()
        # When disconnected, reset the configurations
        # and pull the configurations during reconnection
        # This is to prevent synchronization issues with local configuration with backend configuration
        # When deleting device, configurations will be deleted in the backend, so device shall also clear its local configuration
        reset_local_configurations()

    printf("application exits!")

if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))

