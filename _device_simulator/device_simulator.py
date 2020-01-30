import json
import time
import netifaces
import argparse
import sys
import os
import psutil
import threading
import random
from messaging_client import messaging_client # common module from parent directory



###################################################################################
CONFIG_USE_ECC = True
# Enable to use AMQP for webserver-to-messagebroker communication
# Disable to use MQTT for webserver-to-messagebroker communication
CONFIG_USE_AMQP = False
###################################################################################

###################################################################################
# global variables
###################################################################################

# device configuration on bootup
CONFIG_REQUEST_CONFIGURATION = True
CONFIG_REQUEST_CONFIGURATION_DEBUG = False
CONFIG_DELETE_CONFIGURATION = False

g_timer_thread = None
g_timer_thread_use = True
g_timer_thread_stop = threading.Event()
g_timer_thread_timeout = 5

g_messaging_client = None

g_gpio_values = {}

# FIRMWARE VERSION
g_firmware_version_MAJOR = 0
g_firmware_version_MINOR = 1
g_firmware_version = (g_firmware_version_MAJOR*100 + g_firmware_version_MINOR)
g_firmware_version_STR = "{}.{}".format(g_firmware_version_MAJOR, g_firmware_version_MINOR)

# STATUS
DEVICE_STATUS_STARTING   = 0
DEVICE_STATUS_RUNNING    = 1
DEVICE_STATUS_RESTART    = 2
DEVICE_STATUS_RESTARTING = 3
DEVICE_STATUS_STOP       = 4
DEVICE_STATUS_STOPPING   = 5
DEVICE_STATUS_STOPPED    = 6
DEVICE_STATUS_START      = 7
g_device_status = DEVICE_STATUS_RUNNING
g_device_statuses = ["starting", "running", "restart", "restarting", "stop", "stopping", "stopped", "start"]

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
g_gpio_enabled = [1, 1, 1, 1]
g_gpio_status = [0, 1, 0, 1]


g_device_classes = ["speaker", "display", "light", "potentiometer", "temperature", "humidity", "anemometer"]

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
g_i2c_enabled = [1, 1, 1, 1]

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

# sensor reading
API_RECEIVE_SENSOR_READING       = "rcv_sensor_reading"
API_REQUEST_SENSOR_READING       = "req_sensor_reading"
API_PUBLISH_SENSOR_READING       = "sensor_reading"

# configuration
API_RECEIVE_CONFIGURATION        = "rcv_configuration"
API_REQUEST_CONFIGURATION        = "req_configuration"
API_DELETE_CONFIGURATION         = "del_configuration"



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



###################################################################################
# API handling
###################################################################################

def print_json(json_object, label=None):
    json_formatted_str = json.dumps(json_object, indent=2)
    if label is None:
        print(json_formatted_str)
    else:
        print("{}\r\n{}".format(label, json_formatted_str))

def publish(topic, payload):
    payload = json.dumps(payload)
    g_messaging_client.publish(topic, payload)

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
    attributes = class_attributes
    return attributes

def handle_api(api, subtopic, subpayload):
    global g_device_status
    global g_uart_properties, g_uart_enabled
    global g_gpio_properties, g_gpio_enabled, g_gpio_voltage, g_gpio_status, g_gpio_values
    global g_i2c_properties, g_i2c_enabled
    global g_adc_voltage
    global g_device_settings



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
                print(g_device_statuses[g_device_status])
        elif status == DEVICE_STATUS_STOP:
            if g_device_status != DEVICE_STATUS_STOPPING and g_device_status != DEVICE_STATUS_STOPPED:
                g_device_status = DEVICE_STATUS_STOPPING
                print(g_device_statuses[g_device_status])
        elif status == DEVICE_STATUS_START:
            if g_device_status != DEVICE_STATUS_STARTING and g_device_status != DEVICE_STATUS_RUNNING:
                g_device_status = DEVICE_STATUS_STARTING
                print(g_device_statuses[g_device_status])

        payload = {}
        payload["value"] = {"status": g_device_status}
        publish(topic, payload)


    ####################################################
    # SENSOR READING
    ####################################################
    elif api == API_RECEIVE_SENSOR_READING:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        # if requested with API_REQUEST_SENSOR_READING which is already obsoleted
        if subpayload.get("source"):
            source = subpayload["source"]
            print("{}{}:{} {}".format(source["peripheral"], source["number"], source["address"], g_device_classes[source["class"]]))
            #print(subpayload["sensors"])

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
                                    print("COLOR = {} scaled {} ({})".format(value, scaled_value, hex(scaled_value).upper()))
                            elif g_i2c_properties[x][y]["attributes"]["color"]["usage"] == 1:
                                # RGB as component
                                prop = g_i2c_properties[x][y]["attributes"]["color"]["individual"]
                                index = 0
                                if prop["red"]["endpoint"] == 1:
                                    value = int(subpayload["sensors"][index]["value"])
                                    print("RED   : {} ({})".format(value, hex(value).upper()))
                                    index += 1
                                if prop["green"]["endpoint"] == 1:
                                    value = int(subpayload["sensors"][index]["value"])
                                    print("GREEN : {} ({})".format(value, hex(value).upper()))
                                    index += 1
                                if prop["blue"]["endpoint"] == 1:
                                    value = int(subpayload["sensors"][index]["value"])
                                    print("BLUE  : {} ({})".format(value, hex(value).upper()))
                                    index += 1
                            print("")
                            break
                elif device_class == "display":
                    for y in g_i2c_properties[x]:
                        if int(y) == source["address"]:
                            index = 0
                            value = int(subpayload["sensors"][index]["value"])
                            if g_i2c_properties[x][y]["attributes"]["format"] == 0:
                                print("HEX = {} ({})".format(hex(value).upper(), value))
                            elif g_i2c_properties[x][y]["attributes"]["format"] == 1:
                                print("INT = {} ({})".format(value, hex(value).upper()))
                            print("")
                            break

    ####################################################
    # SETTINGS
    ####################################################
    elif api == API_GET_SETTINGS:
        topic = generate_pubtopic(subtopic)

        #print("g_device_settings {}".format(g_device_settings))

        payload = {}
        payload["value"] = g_device_settings
        publish(topic, payload)

    elif api == API_SET_SETTINGS:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        g_device_settings = subpayload
        #print("g_device_settings {}".format(g_device_settings))
        g_timer_thread_timeout = g_device_settings["sensorrate"]
        g_timer_thread.set_timeout(g_timer_thread_timeout)

        payload = {}
        publish(topic, payload)


    ####################################################
    # UART
    ####################################################
    elif api == API_GET_UARTS:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        value = {
            'uarts': [
                {'enabled': g_uart_enabled },
            ]
        }
        #print(g_uart_enabled)

        payload = {}
        payload["value"] = value
        publish(topic, payload)

    elif api == API_GET_UART_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        value = g_uart_properties
        #print(g_uart_properties)
        #print(g_uart_baudrate[g_uart_properties['baudrate']])
        #print(g_uart_parity[g_uart_properties['parity']])
        #print(g_uart_flowcontrol[g_uart_properties['flowcontrol']])
        #print(g_uart_stopbits[g_uart_properties['stopbits']])
        #print(g_uart_databits[g_uart_properties['databits']])

        payload = {}
        payload["value"] = value
        publish(topic, payload)

    elif api == API_SET_UART_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        #print(subpayload)

        g_uart_properties = { 
            'baudrate': subpayload["baudrate"], 
            'parity': subpayload["parity"],
            'flowcontrol': subpayload["flowcontrol"],
            'stopbits': subpayload["stopbits"],
            'databits': subpayload["databits"],
        }
        #print(g_uart_properties)
        #print(g_uart_baudrate[g_uart_properties['baudrate']])
        #print(g_uart_parity[g_uart_properties['parity']])
        #print(g_uart_flowcontrol[g_uart_properties['flowcontrol']])
        #print(g_uart_stopbits[g_uart_properties['stopbits']])
        #print(g_uart_databits[g_uart_properties['databits']])

        payload = {}
        publish(topic, payload)

    elif api == API_ENABLE_UART:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        #print(subpayload)

        g_uart_enabled = int(subpayload["enable"])
        #print(g_uart_enabled)

        payload = {}
        publish(topic, payload)


    ####################################################
    # GPIO
    ####################################################
    elif api == API_GET_GPIOS:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        value = {
            'voltage': g_gpio_voltage,
            'gpios': [
                {'direction': g_gpio_properties[0]['direction'], 'status': g_gpio_status[0], 'enabled': g_gpio_enabled[0] },
                {'direction': g_gpio_properties[1]['direction'], 'status': g_gpio_status[1], 'enabled': g_gpio_enabled[1] },
                {'direction': g_gpio_properties[2]['direction'], 'status': g_gpio_status[2], 'enabled': g_gpio_enabled[2] },
                {'direction': g_gpio_properties[3]['direction'], 'status': g_gpio_status[3], 'enabled': g_gpio_enabled[3] }
            ]
        }
        #print(g_gpio_enabled)

        payload = {}
        payload["value"] = value
        publish(topic, payload)

    elif api == API_GET_GPIO_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        number = int(subpayload["number"])-1
        value = g_gpio_properties[number]

        payload = {}
        payload["value"] = value
        publish(topic, payload)

    elif api == API_SET_GPIO_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        #print(subpayload)

        number = int(subpayload["number"])-1
        g_gpio_properties[number] = { 
            'direction' : subpayload["direction"], 
            'mode' : subpayload["mode"],
            'alert': subpayload["alert"],
            'alertperiod': subpayload["alertperiod"],
            'polarity': subpayload["polarity"],
            'width': subpayload["width"],
            'mark': subpayload["mark"],
            'space': subpayload["space"],
            'count': subpayload["count"] }
        value = g_gpio_properties[number]

        payload = {}
        publish(topic, payload)

    elif api == API_ENABLE_GPIO:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        #print(subpayload)

        g_gpio_enabled[int(subpayload["number"])-1] = subpayload["enable"]
        #print(g_gpio_enabled)

        payload = {}
        publish(topic, payload)

    elif api == API_GET_GPIO_VOLTAGE:
        topic = generate_pubtopic(subtopic)

        payload = {}
        payload["value"] = {"voltage": g_gpio_voltage}
        publish(topic, payload)
        #print(g_gpio_voltages[g_gpio_voltage])

    elif api == API_SET_GPIO_VOLTAGE:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        #print(subpayload)

        g_gpio_voltage = subpayload["voltage"]
        #print(g_gpio_voltages[g_gpio_voltage])

        payload = {}
        publish(topic, payload)


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
        #print(value)

        payload = {}
        payload["value"] = value
        publish(topic, payload)

    elif api == API_ENABLE_I2C_DEVICE:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        #print(subpayload)

        number = int(subpayload["number"])-1
        address = str(subpayload["address"])
        enable = int(subpayload["enable"])
        try:
            g_i2c_properties[number][address]["enabled"] = enable
        except:
            pass
        #print()
        #print(g_i2c_properties[number])
        #print()

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
                #print()
                #print(value)
                #print()
        except:
            pass

        payload = {}
        if value is not None:
            payload["value"] = value
        publish(topic, payload)

    elif api == API_SET_I2C_DEVICE_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        print(len(subpayload))
        subpayload = json.loads(subpayload)
        #print(subpayload)

        number = int(subpayload["number"])-1
        address = str(subpayload["address"])
        device_class = subpayload["class"]
        g_i2c_properties[number][address] = {
            'class': device_class,
            'attributes' : setClassAttributes(device_class, subpayload),
            'enabled': 0
        }
        #print()
        #print(g_i2c_properties[number])
        #print()

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
        #print(value)

        payload = {}
        payload["value"] = value
        publish(topic, payload)    

    elif api == API_ENABLE_ADC_DEVICE:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        #print(subpayload)

        number = int(subpayload["number"])-1
        enable = int(subpayload["enable"])
        try:
            g_adc_properties[number]["enabled"] = enable
        except:
            pass
        #print()
        #print(g_adc_properties[number])
        #print()

        payload = {}
        publish(topic, payload)

    elif api == API_GET_ADC_DEVICE_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        number = int(subpayload["number"])-1
        value = None 
        try:
            value = g_adc_properties[number]["attributes"]
            #print()
            #print(value)
            #print()
        except:
            pass

        payload = {}
        if value is not None:
            payload["value"] = value
        publish(topic, payload)

    elif api == API_SET_ADC_DEVICE_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        #print(subpayload)

        number = int(subpayload["number"])-1
        device_class = subpayload["class"]
        g_adc_properties[number] = {
            'class': device_class,
            'attributes' : setClassAttributes(device_class, subpayload),
            'enabled': 0
        }
        #print()
        #print(g_adc_properties[number])
        #print()

        payload = {}
        publish(topic, payload)

    elif api == API_GET_ADC_VOLTAGE:
        topic = generate_pubtopic(subtopic)

        payload = {}
        payload["value"] = {"voltage": g_adc_voltage}
        publish(topic, payload)
        print(g_adc_voltages[g_adc_voltage])

    elif api == API_SET_ADC_VOLTAGE:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        print(subpayload)

        g_adc_voltage = subpayload["voltage"]
        print(g_adc_voltages[g_adc_voltage])

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
        #print(value)

        payload = {}
        payload["value"] = value
        publish(topic, payload)    

    elif api == API_ENABLE_1WIRE_DEVICE:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        #print(subpayload)

        number = int(subpayload["number"])-1
        enable = int(subpayload["enable"])
        try:
            g_1wire_properties[number]["enabled"] = enable
        except:
            pass
        #print()
        #print(g_1wire_properties[number])
        #print()

        payload = {}
        publish(topic, payload)

    elif api == API_GET_1WIRE_DEVICE_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        number = int(subpayload["number"])-1
        value = None 
        try:
            value = g_1wire_properties[number]["attributes"]
            #print()
            #print(value)
            #print()
        except:
            pass

        payload = {}
        if value is not None:
            payload["value"] = value
        publish(topic, payload)

    elif api == API_SET_1WIRE_DEVICE_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        #print(subpayload)

        number = int(subpayload["number"])-1
        device_class = subpayload["class"]
        g_1wire_properties[number] = {
            'class': device_class,
            'attributes' : setClassAttributes(device_class, subpayload),
            'enabled': 0
        }
        #print()
        #print(g_1wire_properties[number])
        #print()

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
        #print(value)

        payload = {}
        payload["value"] = value
        publish(topic, payload)    

    elif api == API_ENABLE_TPROBE_DEVICE:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        #print(subpayload)

        number = int(subpayload["number"])-1
        enable = int(subpayload["enable"])
        try:
            g_tprobe_properties[number]["enabled"] = enable
        except:
            pass
        #print()
        #print(g_tprobe_properties[number])
        #print()

        payload = {}
        publish(topic, payload)

    elif api == API_GET_TPROBE_DEVICE_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        number = int(subpayload["number"])-1
        value = None 
        try:
            value = g_tprobe_properties[number]["attributes"]
            #print()
            #print("GET: {}".format(value))
            #print()
        except:
            pass

        payload = {}
        if value is not None:
            payload["value"] = value
        publish(topic, payload)

    elif api == API_SET_TPROBE_DEVICE_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        #print("SET: {}".format(subpayload))

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

        #print()
        #print(g_tprobe_properties[number])
        #print()

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
            print("{}: {}".format(label, i2c_value))

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
            print("{}: {}".format(label, adc_value))

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
            print("{}: {}".format(label, onewire_value))

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
            print("{}: {}".format(label, tprobe_value))

            if len(tprobe_value) > 0:
                value[label] = {}
                value[label] = tprobe_value

        print("")
        payload = {}
        payload["value"] = value
        #print(payload["value"])
        publish(topic, payload)    


    ####################################################
    # NOTIFICATION
    ####################################################

    elif api == API_TRIGGER_NOTIFICATION:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        # Notification from cloud
        publish(topic, subpayload)
        print("Notification triggered to email/SMS recipient!")

    elif api == API_RECEIVE_NOTIFICATION:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        # Notification from another device
        print("Notification received from device {}:".format(subpayload["sender"]))
        print(subpayload["message"])
        print()


    ####################################################
    # CONFIGURATION
    ####################################################

    elif api == API_RECEIVE_CONFIGURATION:
        topic = generate_pubtopic(subtopic)
        if len(subpayload) > 2:
            print(len(subpayload))
        subpayload = json.loads(subpayload)

        if CONFIG_REQUEST_CONFIGURATION_DEBUG:
            print("")
            print("uart   {} - {}\r\n".format(subpayload["uart"],   len(subpayload["uart"])   ))
            print("gpio   {} - {}\r\n".format(subpayload["gpio"],   len(subpayload["gpio"])   ))
            print("i2c    {} - {}\r\n".format(subpayload["i2c"],    len(subpayload["i2c"])    ))
            print("  i2c0 {} - {}\r\n".format(subpayload["i2c"][0], len(subpayload["i2c"][0]) ))
            print("  i2c1 {} - {}\r\n".format(subpayload["i2c"][1], len(subpayload["i2c"][1]) ))
            print("  i2c2 {} - {}\r\n".format(subpayload["i2c"][2], len(subpayload["i2c"][2]) ))
            print("  i2c3 {} - {}\r\n".format(subpayload["i2c"][3], len(subpayload["i2c"][3]) ))
            print("adc    {} - {}\r\n".format(subpayload["adc"],    len(subpayload["adc"])    ))
            print("1wire  {} - {}\r\n".format(subpayload["1wire"],  len(subpayload["1wire"])  ))
            print("tprobe {} - {}\r\n".format(subpayload["tprobe"], len(subpayload["tprobe"]) ))
            print("")

        if subpayload.get("uart"):
            if subpayload["uart"][0].get("attributes"):
                g_uart_properties = subpayload["uart"][0]["attributes"]

        if subpayload.get("gpio"):
            for x in range(len(g_gpio_properties)):
                if subpayload["gpio"][x].get("attributes"):
                    g_gpio_properties[x] = subpayload["gpio"][x]["attributes"]

        if subpayload.get("adc"):
            for x in range(len(g_adc_properties)):
                if subpayload["adc"][x].get("attributes"):
                    g_adc_properties[x]["enabled"] = 0
                    g_adc_properties[x]["class"] = subpayload["adc"][x]["class"]
                    g_adc_properties[x]["attributes"] = subpayload["adc"][x]["attributes"]
                    if subpayload["adc"][x].get("subclass"):
                        g_adc_properties[x]["subclass"] = subpayload["adc"][x]["subclass"]

        if subpayload.get("1wire"):
            for x in range(len(g_1wire_properties)):
                if subpayload["1wire"][x].get("attributes"):
                    g_1wire_properties[x]["enabled"] = 0
                    g_1wire_properties[x]["class"] = subpayload["1wire"][x]["class"]
                    g_1wire_properties[x]["attributes"] = subpayload["1wire"][x]["attributes"]
                    if subpayload["1wire"][x].get("subclass"):
                        g_1wire_properties[x]["subclass"] = subpayload["1wire"][x]["subclass"]

        if subpayload.get("tprobe"):
            for x in range(len(g_tprobe_properties)):
                if subpayload["tprobe"][x].get("attributes"):
                    g_tprobe_properties[x]["enabled"] = 0
                    g_tprobe_properties[x]["class"] = subpayload["tprobe"][x]["class"]
                    g_tprobe_properties[x]["attributes"] = subpayload["tprobe"][x]["attributes"]
                    if subpayload["tprobe"][x].get("subclass"):
                        g_tprobe_properties[x]["subclass"] = subpayload["tprobe"][x]["subclass"]

        if subpayload.get("i2c"):
            for x in range(len(g_i2c_properties)):
                for y in range(len(subpayload["i2c"][x])):
                    if subpayload["i2c"][x][y].get("attributes"):
                        address = str(subpayload["i2c"][x][y]["address"])
                        g_i2c_properties[x][address] = {}
                        g_i2c_properties[x][address]["enabled"] = 0
                        g_i2c_properties[x][address]["class"] = subpayload["i2c"][x][y]["class"]
                        g_i2c_properties[x][address]["attributes"] = subpayload["i2c"][x][y]["attributes"]
                        if subpayload["i2c"][x][y].get("subclass"):
                            g_i2c_properties[x][address]["subclass"] = subpayload["i2c"][x][y]["subclass"]

        if CONFIG_REQUEST_CONFIGURATION_DEBUG:
            print_json(g_uart_properties, "uart")
            print_json(g_gpio_properties, "gpio")
            print_json(g_adc_properties, "adc")
            print_json(g_1wire_properties, "1wire")
            print_json(g_tprobe_properties, "tprobe")
            print_json(g_i2c_properties, "i2c")

        print("\r\nDEVICE CONFIGURATION")
        print("Device is now configured with cached values from cloud.\r\n\r\n")


    ####################################################
    # UNSUPPORTED
    ####################################################

    else:
        print("UNSUPPORTED")



###################################################################################
# MQTT/AMQP callback functions
###################################################################################

def on_message(subtopic, subpayload):

    expected_topic = "{}{}".format(CONFIG_DEVICE_ID, CONFIG_SEPARATOR)
    expected_topic_len = len(expected_topic)

    if subtopic[:expected_topic_len] != expected_topic:
        print("unexpected packet")
        return

    api = subtopic[expected_topic_len:]
    #print(api)
    handle_api(api, subtopic, subpayload)


def on_mqtt_message(client, userdata, msg):

    print("RCV: {}".format(msg.topic))
    print_json(json.loads(msg.payload))
    on_message(msg.topic, msg.payload)

  
def on_amqp_message(ch, method, properties, body):

    print("RCV: AMQP {} {}".format(method.routing_key, body))
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
        print("\nDevice will be restarting in 3 seconds")
        for x in range(3):
            time.sleep(1)
            print(".")
        time.sleep(1)
        restart()

def process_stop():
    global g_device_status
    if g_device_status == DEVICE_STATUS_STOPPING:
        print("\nDevice will be stopped in 3 seconds")
        for x in range(3):
            time.sleep(1)
            print(".")
        time.sleep(1)
        g_device_status = DEVICE_STATUS_STOPPED
        print("Device stopped successfully!\n")

def process_start():
    global g_device_status
    if g_device_status == DEVICE_STATUS_STARTING:
        print("\nDevice will be started in 3 seconds")
        for x in range(3):
            time.sleep(1)
            print(".")
        time.sleep(1)
        g_device_status = DEVICE_STATUS_RUNNING
        print("Device started successfully!\n")


def req_configuration(peripherals = None):
    print("\r\n\r\nRequest device configuration")
    topic = "{}{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_DEVICE_ID, CONFIG_SEPARATOR, API_REQUEST_CONFIGURATION)
    if peripherals is None:
        payload = {}
    else:
        payload = { "peripherals": peripherals }
    publish(topic, payload)

def del_configuration(peripherals = None):
    print("\r\n\r\nDelete device configuration")
    topic = "{}{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_DEVICE_ID, CONFIG_SEPARATOR, API_DELETE_CONFIGURATION)
    if peripherals is None:
        payload = {}
    else:
        payload = { "peripherals": peripherals }
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

class TimerThread(threading.Thread):

    def __init__(self, event, timeout):
        threading.Thread.__init__(self)
        self.stopped = event
        self.timeout = timeout

    def set_timeout(self, timeout):
        self.timeout = timeout

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
                if adc_class == "anemometer" or adc_class == "potentiometer":
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
            payload["sensors"] = sensors
            print("")
            publish(topic, payload)
            print("")
        else:
            #print("no enabled sensor")
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
                        #print("xxx {}".format(g_i2c_properties[x][y]))
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
                        print("")
                        publish(topic, payload)
                        print("")
                    elif i2c_class == "display":
                        # if DISPLAY class
                        #print("xxx {}".format(g_i2c_properties[x][y]))
                        if g_i2c_properties[x][y]["attributes"]["endpoint"] == 1:
                            entry = g_i2c_properties[x][y]["attributes"]["hardware"]
                            payload["sensors"].append(entry)
                            payload["source"] = {"peripheral": "I2C", "number": x+1, "address": int(y), "class": g_i2c_properties[x][y]["class"]}
                            print("")
                            publish(topic, payload)
                            print("")


    def run(self):
        print("")
        while not self.stopped.wait(self.timeout):
            self.process_input_devices()
            #self.process_output_devices()





###################################################################################
# Main entry point
###################################################################################

def parse_arguments(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--USE_ECC',         required=False, default=1 if CONFIG_USE_ECC else 0, help='Use ECC instead of RSA')
    parser.add_argument('--USE_AMQP',        required=False, default=1 if CONFIG_USE_AMQP else 0, help='Use AMQP instead of MQTT')
    parser.add_argument('--USE_DEVICE_ID',   required=False, default=CONFIG_DEVICE_ID,     help='Device ID to use')
    parser.add_argument('--USE_DEVICE_CA',   required=False, default=CONFIG_TLS_CA,        help='Device CA certificate to use')
    parser.add_argument('--USE_DEVICE_CERT', required=False, default=CONFIG_TLS_CERT,      help='Device certificate to use')
    parser.add_argument('--USE_DEVICE_PKEY', required=False, default=CONFIG_TLS_PKEY,      help='Device private key to use')
    parser.add_argument('--USE_HOST',        required=False, default=CONFIG_HOST,          help='Host server to connect to')
    parser.add_argument('--USE_PORT',        required=False, default=CONFIG_MQTT_TLS_PORT, help='Host port to connect to')
    parser.add_argument('--USE_USERNAME',    required=False, default=CONFIG_USERNAME,      help='Username to use in connection')
    parser.add_argument('--USE_PASSWORD',    required=False, default=CONFIG_PASSWORD,      help='Password to use in connection')
    return parser.parse_args(argv)


if __name__ == '__main__':

    args = parse_arguments(sys.argv[1:])
    CONFIG_USE_AMQP    = True if int((args.USE_AMQP))==1 else False
    CONFIG_USE_ECC    = True if int((args.USE_ECC))==1 else False
    CONFIG_SEPARATOR   = "." if int((args.USE_AMQP))==1 else "/"
    CONFIG_DEVICE_ID   = args.USE_DEVICE_ID
    CONFIG_TLS_CA      = args.USE_DEVICE_CA
    CONFIG_TLS_CERT    = args.USE_DEVICE_CERT
    CONFIG_TLS_PKEY    = args.USE_DEVICE_PKEY
    CONFIG_HOST        = args.USE_HOST
    CONFIG_MQTT_TLS_PORT = int(args.USE_PORT)
    CONFIG_AMQP_TLS_PORT = int(args.USE_PORT)
    CONFIG_USERNAME    = args.USE_USERNAME
    CONFIG_PASSWORD    = args.USE_PASSWORD

    print("\n\n")
    print("Copyright (C) Bridgetek Pte Ltd")
    print("-------------------------------------------------------")
    print("Welcome to IoT Device Controller example...\n")
    print("Demonstrate remote access of FT900 via Bridgetek IoT Cloud")
    print("-------------------------------------------------------")

    print("\nFIRMWARE VERSION = {} ({})".format(g_firmware_version_STR, g_firmware_version))

    print("\nTLS CERTIFICATES")
    print("ca:   {}".format(args.USE_DEVICE_CA))
    print("cert: {}".format(args.USE_DEVICE_CERT))
    print("pkey: {}".format(args.USE_DEVICE_PKEY))

    print("\nMQTT CREDENTIALS")
    print("host: {}:{}".format(args.USE_HOST, args.USE_PORT))
    print("id:   {}".format(args.USE_DEVICE_ID))
    print("user: {}".format(args.USE_USERNAME))
    print("pass: {}".format(args.USE_PASSWORD))


    # Initialize MQTT/AMQP client
    if CONFIG_USE_AMQP:
        g_messaging_client = messaging_client(CONFIG_USE_AMQP, on_amqp_message, device_id=CONFIG_DEVICE_ID)
        g_messaging_client.set_server(CONFIG_HOST, CONFIG_AMQP_TLS_PORT)
    else:
        g_messaging_client = messaging_client(CONFIG_USE_AMQP, on_mqtt_message, device_id=CONFIG_DEVICE_ID, use_ecc=CONFIG_USE_ECC)
        g_messaging_client.set_server(CONFIG_HOST, CONFIG_MQTT_TLS_PORT)
    if CONFIG_USERNAME or CONFIG_PASSWORD:
        g_messaging_client.set_user_pass(CONFIG_USERNAME, CONFIG_PASSWORD)
    g_messaging_client.set_tls(CONFIG_TLS_CA, CONFIG_TLS_CERT, CONFIG_TLS_PKEY)


    while True:
        # Connect to MQTT/AMQP broker
        ignore_hostname = False
        while True:
            try:
                (result, code) = g_messaging_client.initialize(timeout=5, ignore_hostname=ignore_hostname)
                if not result:
                    print("Could not connect to message broker! {}".format(code))
                    if code == 1:
                        ignore_hostname = True
                else:
                    break
            except:
                print("Could not connect to message broker! exception!")
                time.sleep(1)

        # Subscribe to messages sent for this device
        time.sleep(1)
        subtopic = "{}{}#".format(CONFIG_DEVICE_ID, CONFIG_SEPARATOR)
        g_messaging_client.subscribe(subtopic, subscribe=True, declare=True, consume_continuously=True)
        # test security, subscribe to other topics
        #subtopic2 = "{}{}{}{}{}".format(CONFIG_PREPEND_REPLY_TOPIC, CONFIG_SEPARATOR, CONFIG_DEVICE_ID, CONFIG_SEPARATOR, API_PUBLISH_SENSOR_READING)
        #g_messaging_client.subscribe(subtopic2, subscribe=True, declare=True, consume_continuously=True)


        # Delete device configuration
        if CONFIG_DELETE_CONFIGURATION:
            del_configuration()
            # can specify specific peripherals like below
            # peripherals can be uart, gpio, i2c, adc, 1wire, tprobe
            #del_configuration(["i2c"])

        # Query device configuration
        if CONFIG_REQUEST_CONFIGURATION:
            req_configuration()
            # can specify specific peripherals like below
            # peripherals can be uart, gpio, i2c, adc, 1wire, tprobe
            #req_configuration(["i2c"])

        # Start the timer thread
        if g_timer_thread_use:
            g_timer_thread = TimerThread(g_timer_thread_stop, g_timer_thread_timeout)
            g_timer_thread.start()

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

        g_messaging_client.release()

        if g_timer_thread_use:
            g_timer_thread_stop.set()

    print("application exits!")
