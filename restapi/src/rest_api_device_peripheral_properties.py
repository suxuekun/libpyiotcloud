#import os
#import ssl
import json
#import time
#import hmac
#import hashlib
import flask
#import base64
#import datetime
#import calendar
#from flask_json import FlaskJSON, JsonError, json_response, as_json
#from certificate_generator import certificate_generator
#from messaging_client import messaging_client
#from rest_api_config import config
#from database import database_client
#from flask_cors import CORS
from flask_api import status
from jose import jwk, jwt
#import http.client
#from s3_client import s3_client
#import threading
#import copy
#from redis_client import redis_client
#import statistics
import rest_api_utils
from database import database_categorylabel, database_crudindex



#CONFIG_SEPARATOR            = '/'
#CONFIG_PREPEND_REPLY_TOPIC  = "server"



class device_peripheral_properties:

    def __init__(self, database_client, messaging_requests):
        self.database_client = database_client
        self.messaging_requests = messaging_requests


    #
    # GET UART PROPERTIES
    #
    # - Request:
    #   GET /devices/device/<devicename>/uart/properties
    #   headers: { 'Authorization': 'Bearer ' + token.access }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string, 'value': { 'baudrate': int, 'parity': int, 'flowcontrol': int, 'stopbits': int, 'databits': int } }
    #   { 'status': 'NG', 'message': string }
    #
    def get_uart_prop(self, devicename):
        api = 'get_uart_prop'

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        #data = {}
        #data['token'] = token
        #data['devicename'] = devicename
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        #data['username'] = username
        #print('get_uart_prop {} devicename={}'.format(data['username'], data['devicename']))


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Set Uart: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        configuration = self.database_client.get_device_peripheral_configuration(entityname, devicename, "uart", 1, None)
        if configuration:
            response = {'value': configuration["attributes"]}
            print(configuration["attributes"])
        else:
            response = {'value': {}}

        #response, status_return = self.messaging_requests.process(api, data)
        #if status_return != 200:
        #    return response, status_return

        source = "uart"
        notification = self.database_client.get_device_notification(entityname, devicename, source)
        if notification is not None:
            if notification["endpoints"]["modem"].get("recipients_id"):
                notification["endpoints"]["modem"].pop("recipients_id")
            #print(notification)
            # notification recipients should be empty
            if notification["endpoints"]["notification"].get("recipients"):
                notification["endpoints"]["notification"]["recipients"] = ""
            response['value']['notification'] = notification
            response = json.dumps(response)
        else:
            response['value']['notification'] = rest_api_utils.utils().build_default_notifications("uart", token, self.database_client)
            response = json.dumps(response)

        return response


    #
    # SET UART PROPERTIES
    #
    # - Request:
    #   POST /devices/device/<devicename>/uart/properties
    #   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
    #   data: { 'baudrate': int, 'parity': int, 'flowcontrol': int, 'stopbits': int, 'databits': int }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string }
    #   { 'status': 'NG', 'message': string }
    #
    def set_uart_prop(self, devicename):
        api = 'set_uart_prop'

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED

        # get username from token
        data = flask.request.get_json()
        #print(data)
        if data['baudrate'] is None or data['parity'] is None or data['databits'] is None or data['stopbits'] is None or data['flowcontrol'] is None or data['notification'] is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
            print('\r\nERROR Invalid parameters\r\n')
            return response, status.HTTP_400_BAD_REQUEST
        #print(data['baudrate'])
        #print(data['parity'])
        #print(data['notification'])

        # get notifications and remove from list
        notification = data['notification']
        #print(notification)
        data.pop('notification')
        #print(notification)
        #print(data)

        username = self.database_client.get_username_from_token({'access': auth_header_token})
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('set_uart_prop {} devicename={}'.format(username, devicename))


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Set Uart: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        source = "uart"
        item = self.database_client.update_device_notification(entityname, devicename, source, notification)

        # update device configuration database for device bootup
        #print("data={}".format(data))
        item = self.database_client.update_device_peripheral_configuration(entityname, devicename, "uart", 1, None, None, None, data)


        data['token'] = {'access': auth_header_token}
        data['devicename'] = devicename
        data['username'] = username
        response, status_return = self.messaging_requests.process(api, data)
        if status_return != 200:
            return response, status_return

        return response


    #
    # ENABLE/DISABLE UART
    #
    # - Request:
    #   POST /devices/device/DEVICENAME/uart/enable
    #   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
    #   data: { 'enable': int }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string }
    #   { 'status': 'NG', 'message': string }
    #
    #@app.route('/devices/device/<devicename>/uart/enable', methods=['POST'])
    #def enable_uart(self, devicename):
    #    api = 'enable_uart'

    #    # get token from Authorization header
    #    auth_header_token = self.utils.get_auth_header_token()
    #    if auth_header_token is None:
    #        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
    #        print('\r\nERROR Invalid authorization header\r\n')
    #        return response, status.HTTP_401_UNAUTHORIZED

    #    # get username from token
    #    data = flask.request.get_json()

    #    # check parameter input
    #    if data['enable'] is None:
    #        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
    #        print('\r\nERROR Invalid parameters\r\n')
    #        return response, status.HTTP_400_BAD_REQUEST

    #    data['token'] = {'access': auth_header_token}
    #    data['devicename'] = devicename
    #    username = self.database_client.get_username_from_token(data['token'])
    #    if username is None:
    #        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
    #        print('\r\nERROR Token expired\r\n')
    #        return response, status.HTTP_401_UNAUTHORIZED
    #    data['username'] = username
    #    print('enable_uart {} devicename={}'.format(data['username'], data['devicename']))

    #    return self.messaging_requests.process(api, data)

    
    #
    # GET UARTS
    #
    # - Request:
    #   GET /devices/device/<devicename>/uarts
    #   headers: { 'Authorization': 'Bearer ' + token.access }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string, 
    #     'value': { 
    #       'uarts': [
    #         {'enabled': int}, 
    #       ]
    #     }
    #   }
    #   { 'status': 'NG', 'message': string }
    #
    #@app.route('/devices/device/<devicename>/uarts', methods=['GET'])
    #def get_uarts(self, devicename):
    #    api = 'get_uarts'

    #    # get token from Authorization header
    #    auth_header_token = self.utils.get_auth_header_token()
    #    if auth_header_token is None:
    #        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
    #        print('\r\nERROR Invalid authorization header\r\n')
    #        return response, status.HTTP_401_UNAUTHORIZED
    #    token = {'access': auth_header_token}

    #    # get username from token
    #    data = {}
    #    data['token'] = token
    #    data['devicename'] = devicename
    #    username = self.database_client.get_username_from_token(data['token'])
    #    if username is None:
    #        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
    #        print('\r\nERROR Token expired\r\n')
    #        return response, status.HTTP_401_UNAUTHORIZED
    #    data['username'] = username
    #    print('get_uarts {} devicename={}'.format(data['username'], data['devicename']))

    #    return self.messaging_requests.process(api, data)
    
    

    ########################################################################################################
    #
    # SET I2C DEVICE PROPERTIES
    #
    # - Request:
    #   POST /devices/device/<devicename>/i2c/number/sensors/sensor/<sensorname>/properties
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   data: adsasdasdasdasdasdasdasd
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    #
    # SET ADC DEVICE PROPERTIES
    # SET 1WIRE DEVICE PROPERTIES
    # SET TPROBE DEVICE PROPERTIES
    #
    # - Request:
    #   POST /devices/device/<devicename>/adc/number/sensors/sensor/<sensorname>/properties
    #   POST /devices/device/<devicename>/1wire/number/sensors/sensor/<sensorname>/properties
    #   POST /devices/device/<devicename>/tprobe/number/sensors/sensor/<sensorname>/properties
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   data: adsasdasdasdasdasdasdasd
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def set_xxx_dev_prop(self, devicename, xxx, number, sensorname):
        print('set_{}_dev_prop'.format(xxx))

        # check number parameter
        #if int(number) > 4 or int(number) < 1:
        #    response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        #    print('\r\nERROR Invalid parameters\r\n')
        #    return response, status.HTTP_400_BAD_REQUEST

        if xxx == "i2c" or xxx == "adc" or xxx == "1wire" or xxx == "tprobe":
            api = 'set_{}_dev_prop'.format(xxx)
        else:
            api = 'set_ldsu_dev_prop'

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Set {} Sensor: Invalid authorization header\r\n'.format(xxx))
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token} 
        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Set {} Sensor: Token expired\r\n'.format(xxx))
            return response, status.HTTP_401_UNAUTHORIZED
        print('{} {} devicename={} number={} sensorname={}'.format(api, username, devicename, number, sensorname))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0 or len(devicename) == 0 or len(sensorname) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Set {} Sensor: Empty parameter found\r\n'.format(xxx))
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Set {} Sensor: Token expired [{}]\r\n'.format(xxx, username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Set {} Sensor: Token is invalid [{}]\r\n'.format(xxx, username))
            return response, status.HTTP_401_UNAUTHORIZED

        # get username from token
        data = flask.request.get_json()
        if data is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
            print('\r\nERROR Invalid parameters\r\n')
            return response, status.HTTP_400_BAD_REQUEST


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Set Peripheral Sensor: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED

            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # check if sensor is registered
        sensor = self.database_client.get_sensor(entityname, devicename, xxx, number, sensorname)
        if not sensor:
            response = json.dumps({'status': 'NG', 'message': 'Sensor is not registered'})
            print('\r\nERROR Get {} Sensor: Sensor is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        # removed for caching
        #data['token'] = token
        #data['devicename'] = devicename
        #data['username'] = username

        if sensor.get('address'):
            data['address'] = sensor['address']
        data['class'] = int(rest_api_utils.utils().get_i2c_device_class(sensor['class']))
        if sensor.get('subclass'):
            # handle subclasses
            data['subclass'] = int(rest_api_utils.utils().get_i2c_device_class(sensor['subclass']))
        data['number'] = int(number)
        print('{} {} devicename={} number={}'.format(api, entityname, devicename, number))


        # no notification data
        if not data.get("notification"):
            #print("no notification data")

            # removed for caching
            #response, status_return = self.messaging_requests.process(api, data)
            #if status_return != 200:
            #    # set enabled to FALSE and configured to FALSE
            #    self.database_client.set_enable_configure_sensor(entityname, devicename, xxx, number, sensorname, 0, 0)
            #    return response, status_return

            # if ADC/1WIRE/TPROBE, set all other ADC/1WIRE/TPROBE to unconfigured and disabled
            if xxx == "adc" or xxx == "1wire" or xxx == "tprobe":
                self.database_client.disable_unconfigure_sensors_source(entityname, devicename, xxx, number)
            # set to disabled and configured
            self.database_client.set_enable_configure_sensor(entityname, devicename, xxx, number, sensorname, 0, 1)

            # update device configuration database for device bootup
            #print("data={}".format(data))
            data.pop('number')
            if data.get('address'):
                data.pop('address')
            if data.get('class'):
                data.pop('class')
            if data.get('subclass'):
                data.pop('subclass')

            address = None
            if sensor.get('address'):
                address = sensor['address']
            classid = None
            if sensor.get('class'):
                classid = int(rest_api_utils.utils().get_i2c_device_class(sensor['class']))
            subclassid = None
            if sensor.get('subclass'):
                subclassid = int(rest_api_utils.utils().get_i2c_device_class(sensor['subclass']))
            item = self.database_client.update_device_peripheral_configuration(entityname, devicename, xxx, int(number), address, classid, subclassid, data)

            return response


        # has notification parameter (for class and subclass)
        notification = data['notification']
        data.pop('notification')
        # handle subclasses
        if data.get("subattributes"):
            subattributes_notification = data['subattributes']['notification']
            data['subattributes'].pop('notification')
        else:
            subattributes_notification = None

        # removed for caching
        # query device
        #response, status_return = self.messaging_requests.process(api, data)
        #if status_return != 200:
        #    # set enabled to FALSE and configured to FALSE
        #    self.database_client.set_enable_configure_sensor(entityname, devicename, xxx, number, sensorname, 0, 0)
        #    return response, status_return

        # if ADC/1WIRE/TPROBE, set all other ADC/1WIRE/TPROBE to unconfigured and disabled
        if xxx == "adc" or xxx == "1wire" or xxx == "tprobe":
            self.database_client.disable_unconfigure_sensors_source(entityname, devicename, xxx, number)

        # set to disabled and configured
        self.database_client.set_enable_configure_sensor(entityname, devicename, xxx, number, sensorname, 0, 1)

        if api != 'set_ldsu_dev_prop':
            source = "{}{}{}".format(xxx, number, sensorname)
        #self.database_client.update_device_notification(entityname, devicename, source, notification)
        self.database_client.update_device_notification_with_notification_subclass(entityname, devicename, xxx, notification, subattributes_notification, int(number))

        # update device configuration database for device bootup
        #print("data={}".format(data))
        data.pop('number')
        if data.get('address'):
            data.pop('address')
        if data.get('class'):
            data.pop('class')
        if data.get('subclass'):
            data.pop('subclass')

        address = None
        if sensor.get('address'):
            address = sensor['address']
        classid = None
        if sensor.get('class'):
            classid = int(rest_api_utils.utils().get_i2c_device_class(sensor['class']))
        subclassid = None
        if sensor.get('subclass'):
            subclassid = int(rest_api_utils.utils().get_i2c_device_class(sensor['subclass']))

        if api == 'set_ldsu_dev_prop':
            address = int(number)
        item = self.database_client.update_device_peripheral_configuration(entityname, devicename, xxx, int(number), address, classid, subclassid, data)

        response = json.dumps({'status': 'OK', 'message': 'Sensor set successfully'})
        return response



    ########################################################################################################
    #
    # GET I2C DEVICE PROPERTIES
    #
    # - Request:
    #   POST /devices/device/<devicename>/i2c/number/sensors/sensor/<sensorname>/properties
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'value': {}}
    #   {'status': 'NG', 'message': string}
    #
    #
    # GET ADC DEVICE PROPERTIES
    # GET 1WIRE DEVICE PROPERTIES
    # GET TPROBE DEVICE PROPERTIES
    #
    # - Request:
    #   POST /devices/device/<devicename>/adc/number/sensors/sensor/<sensorname>/properties
    #   POST /devices/device/<devicename>/1wire/number/sensors/sensor/<sensorname>/properties
    #   POST /devices/device/<devicename>/tprobe/number/sensors/sensor/<sensorname>/properties
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'value': {}}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_xxx_dev_prop(self, devicename, xxx, number, sensorname):
        print('get_{}_dev_prop'.format(xxx))

        # check number parameter
        #if int(number) > 4 or int(number) < 1:
        #    response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        #    print('\r\nERROR Invalid parameters\r\n')
        #    return response, status.HTTP_400_BAD_REQUEST

        if xxx == "i2c" or xxx == "adc" or xxx == "1wire" or xxx == "tprobe":
            api = 'get_{}_dev_prop'.format(xxx)
        else:
            api = 'get_ldsu_dev_prop'

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get {} Sensor: Invalid authorization header\r\n'.format(xxx))
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token} 
        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get {} Sensor: Token expired\r\n'.format(xxx))
            return response, status.HTTP_401_UNAUTHORIZED
        print('{} {} devicename={} number={} sensorname={}'.format(api, username, devicename, number, sensorname))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0 or len(devicename) == 0 or len(sensorname) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get {} Sensor: Empty parameter found\r\n'.format(xxx))
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get {} Sensor: Token expired [{}]\r\n'.format(xxx, username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get {} Sensor: Token is invalid [{}]\r\n'.format(xxx, username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get Peripheral Sensor: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED

            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # check if sensor is registered
        sensor = self.database_client.get_sensor(entityname, devicename, xxx, number, sensorname)
        if not sensor:
            response = json.dumps({'status': 'NG', 'message': 'Sensor is not registered'})
            print('\r\nERROR Get {} Sensor: Sensor is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND


        if False:
            # removed for caching
            data = {}
            data['token'] = token
            data['devicename'] = devicename
            data['username'] = username
            if sensor.get('address'):
                data['address'] = sensor['address']
            data['class'] = int(rest_api_utils.utils().get_i2c_device_class(sensor['class']))
            data['number'] = int(number)
            print('{} {} devicename={} number={}'.format(api, entityname, devicename, number))

            # no notification object required
            if data["class"] < rest_api_utils.classes().I2C_DEVICE_CLASS_POTENTIOMETER:
                return self.messaging_requests.process(api, data)

            # has notification object required
            print("query device")
            response, status_return = self.messaging_requests.process(api, data)
            if status_return != 200:
                return response, status_return
            response = json.loads(response)
            print(response)

        else:
            print("get_device_peripheral_configuration")
            configuration = self.database_client.get_device_peripheral_configuration(entityname, devicename, xxx, int(number), None)
            if configuration:
                response = {'value': configuration["attributes"]}
                print(configuration["attributes"])
            else:
                response = {'value': {}}


        if api != 'get_ldsu_dev_prop':
            source = "{}{}{}".format(xxx, number, sensorname)
        #notification = self.database_client.get_device_notification(entityname, devicename, source)
        (notification, subattributes_notification) = self.database_client.get_device_notification_with_notification_subclass(entityname, devicename, xxx, int(number))
        if notification is not None:
            #response = json.loads(response)
            if response.get('value'):
                response['value']['notification'] = notification
            else:
                response['value'] = {}
                response['value']['notification'] = notification
            response = json.dumps(response)
        else:
            #response = json.loads(response)
            if response.get('value'):
                response['value']['notification'] = rest_api_utils.utils().build_default_notifications(xxx, token, self.database_client)
            else:
                response['value'] = {}
                response['value']['notification'] = rest_api_utils.utils().build_default_notifications(xxx, token, self.database_client)
            response = json.dumps(response)

        # handle subclasses
        if subattributes_notification is not None:
            response = json.loads(response)
            if response.get('value'):
                if response['value'].get('subattributes'):
                    response['value']['subattributes']['notification'] = subattributes_notification
            else:
                response['value'] = {}
                response['value']['subattributes']['notification'] = subattributes_notification
            response = json.dumps(response)
        else:
            response = json.loads(response)
            if response.get('value'):
                if response['value'].get('subattributes'):
                    response['value']['subattributes']['notification'] = rest_api_utils.utils().build_default_notifications(xxx, token, self.database_client)
            else:
                response['value'] = {}
                response['value']['subattributes']['notification'] = rest_api_utils.utils().build_default_notifications(xxx, token, self.database_client)
            response = json.dumps(response)

        return response


    ########################################################################################################
    #
    # ENABLE/DISABLE I2C DEVICE
    #
    # - Request:
    #   POST /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/SENSORNAME/enable
    #   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
    #   data: { 'enable': int }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string }
    #   { 'status': 'NG', 'message': string }
    #
    #
    # ENABLE/DISABLE ADC DEVICE
    # ENABLE/DISABLE 1WIRE DEVICE
    # ENABLE/DISABLE TPROBE DEVICE
    #
    # - Request:
    #   POST /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/SENSORNAME/enable
    #   POST /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/SENSORNAME/enable
    #   POST /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/SENSORNAME/enable
    #   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
    #   data: { 'enable': int }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string }
    #   { 'status': 'NG', 'message': string }
    #
    ########################################################################################################
    def enable_xxx_dev(self, devicename, xxx, number, sensorname):
        print('enable_{}_dev'.format(xxx))

        if xxx == "i2c" or xxx == "adc" or xxx == "1wire" or xxx == "tprobe":
            api = 'enable_{}_dev'.format(xxx)
        else:
            api = 'enable_ldsu_dev'

        # check number parameter
        #if int(number) > 4 or int(number) < 1:
        #    response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        #    print('\r\nERROR Invalid parameters\r\n')
        #    return response, status.HTTP_400_BAD_REQUEST

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED

        # get username from token
        data = flask.request.get_json()

        # check parameter input
        if data['enable'] is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
            print('\r\nERROR Invalid parameters\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        data['token'] = {'access': auth_header_token}
        data['devicename'] = devicename
        username = self.database_client.get_username_from_token(data['token'])
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        data['username'] = username


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Enable Peripheral Sensor: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED

            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # check if sensor is registered
        sensor = self.database_client.get_sensor(entityname, devicename, xxx, number, sensorname)
        if not sensor:
            response = json.dumps({'status': 'NG', 'message': 'Sensor is not registered'})
            print('\r\nERROR Get {} Sensor: Sensor is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        #print(sensor)
        if sensor["configured"] == 0:
            response = json.dumps({'status': 'NG', 'message': 'Sensor is not yet configured'})
            print('\r\nERROR Get {} Sensor: Sensor is yet configured [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_400_BAD_REQUEST

        print('enable_{}_dev {} devicename={} number={}'.format(xxx, entityname, devicename, number))

        do_enable = data['enable']


        # added for caching
        #if do_enable:
        #    configuration = self.database_client.get_device_peripheral_configuration(entityname, devicename, xxx, int(number), None)
        #    if configuration:
        #        configuration["attributes"]["class"] = configuration["class"]
        #        data = {**data, **configuration["attributes"]}

        # added for LDSU
        if api != 'enable_ldsu_dev':
            if sensor.get('address'):
                data['address'] = sensor['address']
            # note: python dict maintains insertion order so number will always be the last key
            data['number'] = int(number)
        else:
            data["UID"] = xxx
            data['SAID'] = number
            data['MODE'] = 0


        # communicate with device
        response, status_return = self.messaging_requests.process(api, data)
        if status_return != 200:
            print('enable_xxx_dev 6')
            return response, status_return

        # set enabled to do_enable and configured to 1
        self.database_client.set_enable_configure_sensor(entityname, devicename, xxx, number, sensorname, do_enable, 1)

        # set enabled
        address = None
        if sensor.get('address'):
            address = sensor["address"]
        self.database_client.set_enable_device_peripheral_configuration(entityname, devicename, xxx, int(number), address, do_enable)

        return response


    ########################################################################################################
    #
    # CHANGE LDSU DEVICE NAME
    #
    # - Request:
    #   POST /devices/device/DEVICENAME/UUID/NUMBER/sensors/sensor/SENSORNAME/enable
    #   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
    #   data: { 'enable': int }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string }
    #   { 'status': 'NG', 'message': string }
    #
    ########################################################################################################
    def change_xxx_dev_name(self, devicename, xxx, number, sensorname):
        print('change_{}_dev_name'.format(xxx))

        # check number parameter
        #if int(number) > 4 or int(number) < 1:
        #    response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        #    print('\r\nERROR Invalid parameters\r\n')
        #    return response, status.HTTP_400_BAD_REQUEST

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED

        # get username from token
        data = flask.request.get_json()

        # check parameter input
        if data['name'] is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
            print('\r\nERROR Invalid parameters\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        username = self.database_client.get_username_from_token({'access': auth_header_token})
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Change Peripheral Sensor Name: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED

            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # change name
        result = self.database_client.change_sensor_name(entityname, devicename, xxx, number, data["name"])


        msg = {'status': 'OK', 'message': 'Peripheral Sensor changed successfully.'}
        response = json.dumps(msg)
        print('\r\nDelete All Device Sensors Properties successful: {} {}\r\n'.format(username, devicename))
        return response


    ########################################################################################################
    #
    # DELETE PERIPHERAL SENSOR PROPERTIES
    #
    # - Request:
    #   DELETE /devices/device/DEVICENAME/sensors/properties
    #   headers: { 'Authorization': 'Bearer ' + token.access }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string }
    #   { 'status': 'NG', 'message': string }
    #
    ########################################################################################################
    def delete_all_device_sensors_properties(self, devicename):

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Delete All Device Sensors Properties: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Delete All Device Sensors Properties: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('delete_all_device_sensors_properties {} devicename={}'.format(username, devicename))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Delete All Device Sensors Properties: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Delete All Device Sensors Properties: Token expired [{} {}]\r\n'.format(username, devicename))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Delete All Device Sensors Properties: Token is invalid [{} {}]\r\n'.format(username, devicename))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.DELETE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Delete All Device Sensors Properties: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED

            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username

        self.database_client.delete_all_device_peripheral_configuration(entityname, devicename)


        msg = {'status': 'OK', 'message': 'Delete All Device Sensors Properties deleted successfully.',}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nDelete All Device Sensors Properties successful: {} {}\r\n'.format(username, devicename))
        return response