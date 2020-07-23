import os
import sys
import ssl
import jwt
import json
import time
from datetime import datetime
import argparse
import http.client
import logging
import random
from logging.handlers import RotatingFileHandler
from logging import handlers



# add timestamp to logs in console and file
CONFIG_ADD_LOG_FILE_TIMESTAMP = True
CONFIG_ADD_LOG_CONSOLE_TIMESTAMP = False
CONFIG_LOG_FILE_MAX_SIZE = 1048576*10 # 10MB
CONFIG_LOG_FILE_MAX_BACKUP = 10



###################################################################################
# Logging
###################################################################################

printf = None

def setup_logging(filename):

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
    return logging.debug

###################################################################################
# JSON Logging
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

###################################################################################
# HTTP Utilities
###################################################################################

def http_initialize_connection(host, port):
    if True:
        context = ssl._create_unverified_context()
    else:
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_REQUIRED
        #context.load_cert_chain(config.CONFIG_TLS_CERT, config.CONFIG_TLS_PKEY)
        #context.load_verify_locations(
        #    config.CONFIG_TLS_CERT, config.CONFIG_TLS_CERT, config.CONFIG_TLS_PKEY)
        #context.check_hostname = False
    conn = http.client.HTTPSConnection(host, port, context=context, timeout=10)
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
            printf("\tRES: Could not communicate with DEVICE! {}".format(r1.status))
            return 0, None
    except Exception as e:
        printf("\tRES: Could not communicate with DEVICE! {}".format(e))
    return 0, None



###################################################################################
# HTTP APIs
###################################################################################


def encode_jwt(username, password, secret_key):
    iat = int(time.time())
    params = {
        "username": username,
        "password": password,
        "iat": iat,
        "exp": iat + 10
    }
    password = jwt.encode(params, secret_key, algorithm='HS256')
    if type(password) == bytes:
        password = password.decode("utf-8")

    return password

def http_send_receive(host, port, method, api, params, headers, key):
    try:
        conn = http_initialize_connection(host, port)
        result = http_send_request(conn, method, api, params, headers, debug=False)
        if result:
            length, response = http_recv_response(conn, debug=False)
            if length == 0:
                conn.close()
                return False, None
            try:
                response = json.loads(response)
                if response["status"] == "OK":
                    conn.close()
                    if key:
                        return True, response[key]
                    else:
                        return True, None
            except Exception as e:
                printf("exception {}".format(e))
                conn.close()
                return False, None
        conn.close()
        return False, None
    except:
        conn.close()
        return False, None

def http_get_header(authorization):
    return { 
        "Connection": "keep-alive",
        "Content-Type" : "application/json",
        "Authorization": "Bearer " + authorization,
    }

def login(host, port, username, password, secret_key):
    tokens = None

    method = "POST"
    api = "/user/login"
    headers = http_get_header(encode_jwt(username, password, secret_key))
    params = None

    result, value = http_send_receive(host, port, method, api, params, headers, "token")
    return value

def add_device(host, port, tokens, devicename, deviceid, serialnumber, poemacaddress):
    method = "POST"
    api = "/devices/device/" + devicename
    api = api.replace(" ", "%20")
    headers = http_get_header(tokens["access"])
    params = json.dumps({
        "deviceid"     : deviceid,
        "serialnumber" : serialnumber,
        "poemacaddress": poemacaddress
    })

    result, value = http_send_receive(host, port, method, api, params, headers, None)
    return result

def get_device(host, port, tokens, devicename):
    method = "GET"
    api = "/devices/device/" + devicename
    api = api.replace(" ", "%20")
    headers = http_get_header(tokens["access"])
    params = None

    result, value = http_send_receive(host, port, method, api, params, headers, "device")
    return value

def get_sensors_by_port(host, port, tokens, devicename, busport):
    method = "GET"
    api = "/devices/device/" + devicename + "/ldsbus/" + busport + "/sensors"
    api = api.replace(" ", "%20")
    headers = http_get_header(tokens["access"])
    params = None

    result, value = http_send_receive(host, port, method, api, params, headers, "sensors")
    return value

def get_sensor_configuration(host, port, tokens, devicename, sensor):
    method = "GET"
    api = "/devices/device/" + devicename + "/" + sensor["source"] + "/" + sensor["number"] + "/sensors/sensor/" + sensor["sensorname"] + "/properties"
    api = api.replace(" ", "%20")
    headers = http_get_header(tokens["access"])
    params = None

    result, value = http_send_receive(host, port, method, api, params, headers, "value")
    return value

def set_sensor_configuration(host, port, tokens, devicename, sensor, notification):
    method = "POST"
    api = "/devices/device/" + devicename + "/" + sensor["source"] + "/" + sensor["number"] + "/sensors/sensor/" + sensor["sensorname"] + "/properties"
    api = api.replace(" ", "%20")
    headers = http_get_header(tokens["access"])
    params = json.dumps({
        "opmode": 0,
        "mode": 2, #continuous mode
        "alert": {
           "type": 0, 
           "period": 60000,
        }, 
        "hardware": {
           "enable": False,
           "recipients": "",
           "isgroup": False,
        },
        "notification": notification
    })
    result, value = http_send_receive(host, port, method, api, params, headers, None)
    return result

def enable_sensor(host, port, tokens, devicename, sensor, enable=True):
    method = "POST"
    api = "/devices/device/" + devicename + "/" + sensor["source"] + "/" + sensor["number"] + "/sensors/sensor/" + sensor["sensorname"] + "/enable"
    api = api.replace(" ", "%20")
    headers = http_get_header(tokens["access"])
    params = json.dumps({
        "enable"     : 1 if enable else 0,
    })

    result, value = http_send_receive(host, port, method, api, params, headers, None)
    return result

def get_device_status(host, port, tokens, devicename):
    method = "GET"
    api = "/devices/device/" + devicename + "/status"
    api = api.replace(" ", "%20")
    headers = http_get_header(tokens["access"])
    params = None

    result, value = http_send_receive(host, port, method, api, params, headers, "value")
    return result

def generate_deviceid(index):
    year = datetime.now().year - 2000
    month = datetime.now().month
    day = datetime.now().day
    deviceid = "PH80XX00{:02}{:02}{:02}{:02X}".format(month, day, year, index)
    return deviceid

def generate_serialnumber():
    serialnumber = random.randint(10000, 99999)
    return str(serialnumber)

def generate_macaddress():
    macaddress = ""
    for x in range(6):
        macaddress += "{:02X}:".format(random.randint(0, 255))
    return macaddress[:-1]

def generate_device(devicename_prefix, index):
    devicename = "{}_{:03}".format(devicename_prefix, index)
    deviceid = generate_deviceid(index)
    serialnumber = generate_serialnumber()
    macaddress = generate_macaddress()
    return devicename, deviceid, serialnumber, macaddress

def read_file(filename):
    try:
        f = open(filename, "r")
        contents = f.read()
        f.close()
    except Exception as e:
        return None

    return contents

def write_file(filename, contents):
    try:
        f = open(filename, "w")
        f.write(contents)
        f.close()
    except Exception as e:
        return None

    return contents

def read_script_templates():
    bat = read_file("templates/device_simulator.py.bat")
    sh = read_file("templates/device_simulator.py.sh")
    return bat, sh

def generate_script_file(host, template, ext, devicename, deviceid, serialnumber, poemacaddress):
    filename = "device_simulator.py.{}.{}".format(devicename, ext)

    contents = ""
    lines = template.split("\n")
    for line in lines:
        if "DEVICE_ID=\"\"" in line:
            contents += line.replace("DEVICE_ID=\"\"", "DEVICE_ID=\"" + deviceid + "\"")
        elif "DEVICE_SERIAL=\"\"" in line:
            contents += line.replace("DEVICE_SERIAL=\"\"", "DEVICE_SERIAL=\"" + serialnumber + "\"")
        elif "DEVICE_MACADD=\"\"" in line:
            contents += line.replace("DEVICE_MACADD=\"\"", "DEVICE_MACADD=\"" + poemacaddress + "\"")
        elif "HOST=\"\"" in line:
            contents += line.replace("HOST=\"\"", "HOST=\"" + host + "\"")
        else:
            contents += line
        contents += "\n"
    write_file(filename, contents)
    return filename

def generate_script_files(host, bat_template, sh_template, devicename, deviceid, serialnumber, poemacaddress):
    if os.name == "nt":
        filename = generate_script_file(host, bat_template, "bat", devicename, deviceid, serialnumber, poemacaddress)
    else:
        filename = generate_script_file(host, sh_template, "sh", devicename, deviceid, serialnumber, poemacaddress)
    return filename

def generate_script_master(host, devicename_prefix, numdevices):
    if os.name == "nt":
        ext = "bat"
        filename = "device_simulator.py.{}_ALL.{}".format(devicename_prefix, ext)
        contents = ""
        for index in range(numdevices):
            contents += "START device_simulator.py.{}_{:03}.{}\n".format(devicename_prefix, index, ext)
        write_file(filename, contents)
    else:
        # TODO
        pass

def run_script_file(filename):
    if os.name == "nt":
        os.system("START {}".format(filename));
    else:
        # TODO
        os.system("START {}".format(filename));

def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--USE_HOST',             required=True, default='', help='Host server to connect to')
    parser.add_argument('--USE_PORT',             required=True, default='', help='Host port to connect to')
    parser.add_argument('--USE_USERNAME',         required=True, default='', help='Account username to use')
    parser.add_argument('--USE_PASSWORD',         required=True, default='', help='Account password to use')
    parser.add_argument('--USE_DEVICE_SECRETKEY', required=True, default='', help='HTTP secret key')
    parser.add_argument('--USE_DEVICE_COUNT',     required=True, default='', help='Number of devices to create run')
    parser.add_argument('--USE_DEVICE_NAMEPREFIX',required=True, default='', help='Name prefix to be used')
    return parser.parse_args(argv)

def main(args):
    global printf

    printf = setup_logging("device_simulator_fleet_automation_logs.txt")
    host = args.USE_HOST
    port = int(args.USE_PORT)
    numdevices = int(args.USE_DEVICE_COUNT)
    devicename_prefix = args.USE_DEVICE_NAMEPREFIX

    printf("-------------------------------------------------------")
    printf("Copyright (C) Bridgetek Pte Ltd")
    printf("-------------------------------------------------------")
    printf("")
    printf("Welcome to IoT Device Simulator Fleet Automation...")
    printf("")
    printf("This enables system test automation for fleet of devices.")
    printf("to test backend reliability and scalability.")
    printf("")
    printf("It automates")
    printf("1. registration multiple devices")
    printf("2. configuration of sensors of multiple devices")
    printf("3. enabling of sensors of multiple devices")
    printf("4. generating the batch script for multiple devices")
    printf("5. running the batch script to run multiple devices")
    printf("")
    printf("-------------------------------------------------------")


    tokens = login(host, port, args.USE_USERNAME, args.USE_PASSWORD, args.USE_DEVICE_SECRETKEY)
    if tokens is None:
        return
    bat_template, sh_template = read_script_templates()
    printf("")

    printf("Strating registration and running of {} devices...".format(numdevices))
    printf("")
    for index in range(numdevices):
        # generate device information
        devicename, deviceid, serialnumber, poemacaddress = generate_device(devicename_prefix, index)
        #devicename = "Dev1"

        # add device
        result = add_device(host, port, tokens, devicename, deviceid, serialnumber, poemacaddress)
        if not result:
            # if device already exists, get device information
            device = get_device(host, port, tokens, devicename)
            if device is None:
                printf("Error: device does not exist!")
                return
            deviceid = device["deviceid"]
            serialnumber = device["serialnumber"]
            poemacaddress = device["poemacaddress"]
            printf("{:03} {} {} {}".format(index, devicename, deviceid, serialnumber, poemacaddress))
            printf("\talready registered...")
        else:
            printf("{:03} {} {} {}".format(index, devicename, deviceid, serialnumber, poemacaddress))
            printf("\tregistered...")


        # run device simulators
        filename = generate_script_files(host, bat_template, sh_template, devicename, deviceid, serialnumber, poemacaddress)
        run_script_file(filename)

        time.sleep(1)
        while True:
            time.sleep(1)
            result = get_device_status(host, port, tokens, devicename)
            if result:
                break
            printf("\tdevice is offline...")
        printf("\tdevice is online!")

        # get sensors
        busport = "1"
        sensors = get_sensors_by_port(host, port, tokens, devicename, busport)

        for sensor in sensors:
            result = True
            # set configuration if not configured
            config = get_sensor_configuration(host, port, tokens, devicename, sensor)
            if config.get("mode") is None:
                result = set_sensor_configuration(host, port, tokens, devicename, sensor, config["notification"])
                if not result:
                    printf("ERROR: Sensor configure failed!")

            # enable sensors if not enabled
            if result:
                printf("\t{} {} sensor configured - {}".format(sensor["source"], sensor["number"], sensor["class"]))
                if not sensor["enabled"]:
                    result = enable_sensor(host, port, tokens, devicename, sensor)
                    if not result:
                        printf("ERROR: Sensor enable failed!")
                        continue
                printf("\t{} {} sensor enabled - {}".format(sensor["source"], sensor["number"], sensor["class"]))

    generate_script_master(host, devicename_prefix, numdevices)
    printf("Completed registration and running of {} devices.".format(numdevices))


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))


