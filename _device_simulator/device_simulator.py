import json
import time
import netifaces
import argparse
import sys
import os
import psutil
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

g_messaging_client = None

g_gpio_values = {}

# FIRMWARE VERSION (for GET STATUS)
g_firmware_version_MAJOR = 0
g_firmware_version_MINOR = 1
g_firmware_version = (g_firmware_version_MAJOR*100 + g_firmware_version_MINOR)
g_firmware_version_STR = "{}.{}".format(g_firmware_version_MAJOR, g_firmware_version_MINOR)

# DEVICE STATUS (for GET STATUS)
DEVICE_STATUS_STARTING   = 0
DEVICE_STATUS_RUNNING    = 1
DEVICE_STATUS_RESTART    = 2
DEVICE_STATUS_RESTARTING = 3
DEVICE_STATUS_STOP       = 4
DEVICE_STATUS_STOPPING   = 5
DEVICE_STATUS_STOPPED    = 6
DEVICE_STATUS_START      = 7
g_device_status = DEVICE_STATUS_RUNNING

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

# I2C
g_i2c_properties = [
    {
        '0': { 'enabled': 0, 'class': 0, 'attributes': {} },
    },
    {
        '0': { 'enabled': 0, 'class': 0, 'attributes': {} },
    },
    {
        '0': { 'enabled': 0, 'class': 0, 'attributes': {} },
    },
    {
        '0': { 'enabled': 0, 'class': 0, 'attributes': {} },
    }
]
g_i2c_enabled = [1, 1, 1, 1]

###################################################################################
# APIs
###################################################################################

# device status
API_GET_STATUS                = "get_status"
API_SET_STATUS                = "set_status"

# uart
API_GET_UARTS                 = "get_uarts"
API_GET_UART_PROPERTIES       = "get_uart_prop"
API_SET_UART_PROPERTIES       = "set_uart_prop"
API_ENABLE_UART               = "enable_uart"

# gpio
API_GET_GPIOS                 = "get_gpios"
API_GET_GPIO_PROPERTIES       = "get_gpio_prop"
API_SET_GPIO_PROPERTIES       = "set_gpio_prop"
API_ENABLE_GPIO               = "enable_gpio"
API_GET_GPIO_VOLTAGE          = "get_gpio_voltage"
API_SET_GPIO_VOLTAGE          = "set_gpio_voltage"

# i2c
API_GET_I2CS                  = "get_i2cs"
API_GET_I2C_DEVICES           = "get_i2c_devs"
API_ADD_I2C_DEVICE            = "add_i2c_dev"
API_REMOVE_I2C_DEVICE         = "remove_i2c_dev"
API_ENABLE_I2C_DEVICE         = "enable_i2c_dev"
API_GET_I2C_DEVICE_PROPERTIES = "get_i2c_dev_prop"
API_SET_I2C_DEVICE_PROPERTIES = "set_i2c_dev_prop"
API_ENABLE_I2C                = "enable_i2c"



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
    attributes = class_attributes
    return attributes

def handle_api(api, subtopic, subpayload):
    global g_device_status
    global g_uart_properties, g_uart_enabled
    global g_gpio_properties, g_gpio_enabled, g_gpio_voltage, g_gpio_status, g_gpio_values
    global g_i2c_properties, g_i2c_enabled


    ####################################################
    # GET/SET STATUS
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
                print("DEVICE_STATUS_RESTART")
        elif status == DEVICE_STATUS_STOP:
            if g_device_status != DEVICE_STATUS_STOPPING and g_device_status != DEVICE_STATUS_STOPPED:
                g_device_status = DEVICE_STATUS_STOPPING
                print("DEVICE_STATUS_STOP")
        elif status == DEVICE_STATUS_START:
            if g_device_status != DEVICE_STATUS_STARTING and g_device_status != DEVICE_STATUS_RUNNING:
                g_device_status = DEVICE_STATUS_STARTING
                print("DEVICE_STATUS_START")

        payload = {}
        payload["value"] = {"status": g_device_status}
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
        print(g_uart_enabled)

        payload = {}
        payload["value"] = value
        publish(topic, payload)

    elif api == API_GET_UART_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        value = g_uart_properties
        print(g_uart_properties)
        print(g_uart_baudrate[g_uart_properties['baudrate']])
        print(g_uart_parity[g_uart_properties['parity']])
        print(g_uart_flowcontrol[g_uart_properties['flowcontrol']])
        print(g_uart_stopbits[g_uart_properties['stopbits']])
        print(g_uart_databits[g_uart_properties['databits']])

        payload = {}
        payload["value"] = value
        publish(topic, payload)

    elif api == API_SET_UART_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        print(subpayload)

        g_uart_properties = { 
            'baudrate': subpayload["baudrate"], 
            'parity': subpayload["parity"],
            'flowcontrol': subpayload["flowcontrol"],
            'stopbits': subpayload["stopbits"],
            'databits': subpayload["databits"],
        }
        print(g_uart_properties)
        print(g_uart_baudrate[g_uart_properties['baudrate']])
        print(g_uart_parity[g_uart_properties['parity']])
        print(g_uart_flowcontrol[g_uart_properties['flowcontrol']])
        print(g_uart_stopbits[g_uart_properties['stopbits']])
        print(g_uart_databits[g_uart_properties['databits']])

        payload = {}
        publish(topic, payload)

    elif api == API_ENABLE_UART:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        print(subpayload)

        g_uart_enabled = int(subpayload["enable"])
        print(g_uart_enabled)

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
        print(g_gpio_enabled)

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
        print(subpayload)

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
        print(subpayload)

        g_gpio_enabled[int(subpayload["number"])-1] = subpayload["enable"]
        print(g_gpio_enabled)

        payload = {}
        publish(topic, payload)

    elif api == API_GET_GPIO_VOLTAGE:
        topic = generate_pubtopic(subtopic)

        payload = {}
        payload["value"] = {"voltage": g_gpio_voltage}
        publish(topic, payload)
        print(g_gpio_voltages[g_gpio_voltage])

    elif api == API_SET_GPIO_VOLTAGE:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        print(subpayload)

        g_gpio_voltage = subpayload["voltage"]
        print(g_gpio_voltages[g_gpio_voltage])

        payload = {}
        publish(topic, payload)


    ####################################################
    # I2C
    ####################################################

    elif api == API_GET_I2CS:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        value = {
            'i2cs': [
                {'enabled': g_i2c_enabled[0] },
                {'enabled': g_i2c_enabled[1] },
                {'enabled': g_i2c_enabled[2] },
                {'enabled': g_i2c_enabled[3] }
            ]
        }
        print(g_i2c_enabled)

        payload = {}
        payload["value"] = value
        publish(topic, payload)

    elif api == API_GET_I2C_DEVICES:
        print("API_GET_I2C_DEVICES")
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)

        value = {
            'i2cs': g_i2c_properties
        }

        payload = {}
        payload["value"] = value
        publish(topic, payload)

    elif api == API_ADD_I2C_DEVICE:
        print("API_ADD_I2C_DEVICE")

    elif api == API_REMOVE_I2C_DEVICE:
        print("API_REMOVE_I2C_DEVICE")

    elif api == API_ENABLE_I2C_DEVICE:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        print(subpayload)

        number = int(subpayload["number"])-1
        address = str(subpayload["address"])
        enable = int(subpayload["enable"])
        try:
            g_i2c_properties[number][address]["enabled"] = enable
        except:
            pass
        print()
        print(g_i2c_properties[number])
        print()

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
                print()
                print(value)
                print()
        except:
            pass

        payload = {}
        if value is not None:
            payload["value"] = value
        publish(topic, payload)

    elif api == API_SET_I2C_DEVICE_PROPERTIES:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        print(subpayload)

        number = int(subpayload["number"])-1
        address = str(subpayload["address"])
        device_class = subpayload["class"]
        g_i2c_properties[number][address] = {
            'class': device_class,
            'attributes' : setClassAttributes(device_class, subpayload),
            'enabled': 0
        }
        print()
        print(g_i2c_properties[number])
        print()

        payload = {}
        publish(topic, payload)

    elif api == API_ENABLE_I2C:
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        print(subpayload)

        g_i2c_enabled[int(subpayload["number"])-1] = subpayload["enable"]
        print(g_i2c_enabled)

        payload = {}
        publish(topic, payload)



    ####################################################
    # NOTIFICATION
    ####################################################

    elif api == "trigger_notification":
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        # Notification from cloud
        publish(topic, subpayload)
        print("Notification triggered to email/SMS recipient!")

    elif api == "recv_notification":
        topic = generate_pubtopic(subtopic)
        subpayload = json.loads(subpayload)
        # Notification from another device
        print("Notification received from device {}:".format(subpayload["sender"]))
        print(subpayload["message"])
        print()



    else:
        print("UNSUPPORTED")



###################################################################################
# MQTT/AMQP callback functions
###################################################################################

def on_message(subtopic, subpayload):

    expected_topic = "{}{}".format(CONFIG_DEVICE_ID, CONFIG_SEPARATOR)
    expected_topic_len = len(expected_topic)

    if subtopic[:expected_topic_len] != expected_topic:
        return

    api = subtopic[expected_topic_len:]
    #print(api)
    handle_api(api, subtopic, subpayload)


def on_mqtt_message(client, userdata, msg):

    print("RCV: MQTT {} {}".format(msg.topic, msg.payload))
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

    print("application exits!")
