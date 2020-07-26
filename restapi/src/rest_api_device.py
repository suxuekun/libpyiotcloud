#import os
#import ssl
import json
import time
#import hmac
#import hashlib
import flask
#import base64
#import datetime
#import calendar
#from flask_json import FlaskJSON, JsonError, json_response, as_json
#from certificate_generator import certificate_generator
#from messaging_client import messaging_client
from rest_api_config import config
#from database import database_client
#from flask_cors import CORS
from flask_api import status
import jwt
#from jose import jwk, jwt
#import http.client
#from s3_client import s3_client
import threading
#import copy
#from redis_client import redis_client
#import statistics
import rest_api_utils
from database import database_categorylabel, database_crudindex
from message_broker_api import message_broker_api
from dashboards.ioc import init_chart_gateway_service, init_chart_sensor_service
from payment.services import subscription_service
import re
from device_serial_number import device_serial_number



CONFIG_SEPARATOR            = '/'
CONFIG_PREPEND_REPLY_TOPIC  = "server"



class device:

    def __init__(self, database_client, messaging_requests, messaging_client, device_client):
        self.database_client = database_client
        self.messaging_requests = messaging_requests
        self.messaging_client = messaging_client
        self.device_client = device_client


    def _check_deviceid(self, deviceid):
        # UUID: PH80XXRRMMDDYYZZZZZ (14 characters plus 2bytes (5 characters) - digits and uppercase letters)

        #if re.match("[A-Z]{2}[0-9A-Z]{4}[0-9A-Z]{2}[0-9]{6}[0-9]{5}$", deviceid) is None:
        if re.match("[0-9A-Z]{16}$", deviceid) is None:
            return False

        prodfamily  = deviceid[0:2]
        prodid      = deviceid[2:6]
        reserved    = deviceid[6:8]
        month       = deviceid[8:10]
        day         = deviceid[10:12]
        year        = deviceid[12:14]
        running_num = deviceid[14:]

        #print(prodfamily)
        #print(prodid)
        #print(reserved)
        #print(month)
        #print(day)
        #print(year)
        #print(running_num)

        # check prodfamily
        #if prodfamily != "PH":
        #    print("Invalid prodfamily {}".format(prodfamily))
        #    return False

        # check prodid
        #if prodid != "80XX":
        #    print("Invalid prodid {}".format(prodid))
        #    return False

        # check reserved

        # check month, day, year
        #if int(month) < 1 or int(month) > 12:
        #    print("Invalid month {}".format(month))
        #    return False
        #if int(day) < 1 or int(day) > 31:
        #    print("Invalid day {}".format(day))
        #    return False
        #if int(year) < 0 or int(year) > 99:
        #    print("Invalid year {}".format(year))
        #    return False

        # check running number
        #if int(runningnum, 16) > 255:
        #    print("Invalid running number {}".format(runningnum))
        #    return False

        return True

    def _check_serialnumber(self, deviceid, serialnumber):
        # SerialNumber: SSSSS (5 characters - digits and uppercase letters)

        if re.match("[0-9A-Z]{5}$", serialnumber) is None:
            return False

        if False:
            if not config.debugging:
                siphash, half_siphash = device_serial_number().compute_by_uuid(deviceid)
                print("siphash=0x{:X}".format( siphash ))
                print("half siphash=0x{:X}".format( half_siphash ))
                siphash = "{:X}".format(siphash) 
                half_siphash = "{:X}".format(half_siphash) 
                #print(siphash)
                #print(half_siphash)

                if serialnumber != half_siphash:
                    print("serialnumber does not match {} {}".format(serialnumber, half_siphash))

        return True

    def _check_macaddress(self, macaddress):
        # POE MAC Address: 00:00:00:00:00:00 (17 characters - digits and A-F uppercase letters)

        if re.match("[0-9A-F]{2}([-:]?)[0-9A-F]{2}(\\1[0-9A-F]{2}){4}$", macaddress) is None:
            return False

        return True


    def decode_password(self, secret_key, password):

        return jwt.decode(password, secret_key, algorithms=['HS256'])

    def compute_password(self, secret_key, uuid, serial_number, mac_address, debug=False):

        if secret_key=='' or uuid=='' or serial_number=='' or mac_address=='':
            printf("secret key, uuid, serial number and mac address should not be empty!")
            return None

        current_time = int(time.time())
        params = {
            "uuid": uuid,                  # device uuid
            "serialnumber": serial_number, # device serial number
            "poemacaddress": mac_address,  # device mac address in uppercase string ex. AA:BB:CC:DD:EE:FF
        }
        password = jwt.encode(params, secret_key, algorithm='HS256')

        # pyjwt returns bytes while jose returns string
        # if bytes is returned, then convert to string
        if type(password) == bytes:
            password = password.decode("utf-8")

        if debug:
            print("")
            print("compute_password")
            rest_api_utils.utils().print_json(params)
            print(password)
            print("")

            payload = self.decode_password(secret_key, password)
            print("")
            print("decode_password")
            rest_api_utils.utils().print_json(payload)
            print("")

        return password


    def device_cleanup(self, entityname, deviceid, devicename):

        try:
            # delete device sensor-related information
            sensors = self.database_client.get_all_device_sensors_by_deviceid(deviceid)
            if sensors is not None:
                for sensor in sensors:
                    if sensor.get("source") and sensor.get("number") and sensor.get("sensorname"):
                        self.sensor_cleanup(None, None, deviceid, sensor["source"], sensor["number"], sensor["sensorname"], sensor)
        except Exception as e:
            print("Exception sensor_cleanup")
            print(e)

        try:
            # delete device-related information
            self.database_client.delete_device_history_by_deviceid(deviceid)
            self.database_client.delete_ota_status_by_deviceid(deviceid)
            self.database_client.delete_device_notification_by_deviceid(deviceid)
            self.database_client.delete_device_location_by_deviceid(deviceid)
            self.database_client.remove_device_from_devicegroups(entityname, deviceid)
            self.database_client.delete_device_heartbeats_by_deviceid(deviceid)
            self.database_client.delete_ldsus_by_deviceid(deviceid)
            self.database_client.delete_ota_status_by_deviceid(deviceid)
            #self.database_client.delete_menos_transaction_by_deviceid(deviceid)
        except Exception as e:
            print("Exception asdasd")
            print(e)

        # delete dashboard related items
        try:
            init_chart_gateway_service().delete_by_deviceId(deviceid)
            init_chart_sensor_service().delete_by_deviceId(deviceid)
        except Exception as e:
            print("Exception init_chart_gateway_service().delete_by_deviceId")
            print(e)

        # delete device subscription
        try:
            subscription_service.cleanup(deviceid)
        except Exception as e:
            print("Exception subscription_service.delete")
            print(e)

        # delete device notifications and configurations
        devices = self.database_client.get_devices(entityname)
        try:
            for devicex in devices:
                self.database_client.update_device_notification_devicedelete_by_deviceid(devicex["deviceid"], devicename)
        except Exception as e:
            print("Exception update_device_notification_devicedelete_by_deviceid")
            print(e)
        try:
            for devicex in devices:
                self.database_client.update_device_peripheral_configuration_devicedelete_by_deviceid(devicex["deviceid"], devicename)
        except Exception as e:
            print("Exception update_device_peripheral_configuration_devicedelete_by_deviceid")
            print(e)

        # delete device from database
        try:
            self.database_client.delete_device_by_deviceid(deviceid)
        except Exception as e:
            print("Exception delete_device_by_deviceid")
            print(e)

        # delete device from message broker
        try:
            message_broker_api().unregister(deviceid)
        except Exception as e:
            print("Exception message_broker_api().unregister")
            print(e)


    #
    # when deleting a sensor,
    # make sure the sensor configurations, sensor readings and sensor registration are also deleted
    #
    def sensor_cleanup(self, entityname, devicename, deviceid, xxx, number, sensorname, sensor):

        print("\r\ndelete_sensor {}".format(sensorname))
        address = None
        if sensor.get("address") is not None:
            address = sensor["address"]

        print("")

        # delete sensor notifications
        print("Deleting sensor notifications...")
        #source = "{}{}{}".format(xxx, number, sensorname)
        #notification = self.database_client.get_device_notification(entityname, devicename, source)
        #print(notification)
        if deviceid:
            self.database_client.delete_device_notification_sensor_by_deviceid(deviceid, xxx, int(number))
        else:
            self.database_client.delete_device_notification_sensor(entityname, devicename, xxx, int(number))
        #notification = self.database_client.get_device_notification(entityname, devicename, source)
        #print(notification)
        #print("")

        # delete sensor configurations
        print("Deleting sensor configurations...")
        #config = self.database_client.get_device_peripheral_configuration(entityname, devicename, xxx, int(number), address)
        #print(config)
        if deviceid:
            self.database_client.delete_device_peripheral_configuration_by_deviceid(deviceid, xxx, int(number), None)
        else:
            self.database_client.delete_device_peripheral_configuration(entityname, devicename, xxx, int(number), None)
        #config = self.database_client.get_device_peripheral_configuration(entityname, devicename, xxx, int(number), address)
        #print(config)
        #print("")

        # delete sensor readings
        print("Deleting sensor readings...")
        #readings = self.database_client.get_sensor_reading(entityname, devicename, source, address)
        #print(readings)
        #readings_dataset = self.database_client.get_sensor_reading_dataset(entityname, devicename, source, address)
        #print(readings_dataset)
        if deviceid:
            self.database_client.delete_sensor_reading_by_deviceid(deviceid, xxx, int(number))
        else:
            self.database_client.delete_sensor_reading(entityname, devicename, xxx, int(number))
        #readings = self.database_client.get_sensor_reading(entityname, devicename, source, address)
        #print(readings)
        #readings_dataset = self.database_client.get_sensor_reading_dataset(entityname, devicename, source, address)
        #print(readings_dataset)
        #print("")

        # delete sensor from database
        print("Deleting sensor registration...")
        if deviceid:
            self.database_client.delete_device_sensors_by_source_number_by_deviceid(deviceid, xxx, number)
            #self.database_client.delete_sensor_by_deviceid(deviceid, xxx, number, sensorname)
        else:
            self.database_client.delete_device_sensors_by_source_number_by(entityname, devicename, xxx, number)
        #result = self.database_client.get_sensor(entityname, devicename, xxx, number, sensorname)
        #print(result)
        #print("")


    def get_status_threaded(self, entityname, api, data, device):
        response, status_return = self.messaging_requests.process(api, data)
        if status_return == 503: # HTTP_503_SERVICE_UNAVAILABLE
            # if device is unreachable, get the cached heartbeat and version
            cached_value = self.database_client.get_device_cached_values(entityname, device["devicename"])
            if cached_value:
                if cached_value.get("heartbeat"):
                    device["heartbeat"] = cached_value["heartbeat"]
                if cached_value.get("version"):
                    device["version"] = cached_value["version"]

        if status_return == 200:
            response = json.loads(response)
            version = response["value"]["version"]
            status = response["value"]["status"]
            response = json.dumps(response)
            self.database_client.save_device_version(entityname, device["devicename"], version)
            device["version"] = version
            device["status"] = status


    ########################################################################################################
    # 
    # GET DEVICES
    #
    # - Request:
    #   GET /devices
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'devices': array[{'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': string, 'heartbeat': string, 'version': string, location: {'latitude': float, 'longitude': float}}, ...]}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_device_list(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get Devices: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Devices: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        #print('get_device_list {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get Devices: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Devices: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get Devices: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get Devices: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        devices = self.database_client.get_devices(entityname)


        msg = {'status': 'OK', 'message': 'Devices queried successfully.', 'devices': devices}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        #print('get_device_list {} {} devices'.format(username, len(devices)))
        return response

    ########################################################################################################
    # 
    # GET DEVICES FILTERED
    #
    # - Request:
    #   GET /devices/filter/FILTERSTRING
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'devices': array[{'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': string, 'heartbeat': string, 'version': string, location: {'latitude': float, 'longitude': float}}, ...]}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_device_list_filtered(self, filter):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get Devices: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Devices: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        #print('get_device_list_filtered {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0 or len(filter) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get Devices: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Devices: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get Devices: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get Devices: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        devices = self.database_client.get_devices_with_filter(entityname, filter)

        # get the location from database
        #for device in devices:
        #    location  = self.database_client.get_device_location(username, device["devicename"])
        #    if location:
        #        device["location"] = location


        msg = {'status': 'OK', 'message': 'Devices queried successfully.', 'devices': devices}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        #print('\r\nGet Devices successful: {}\r\n{} devices\r\n'.format(username, len(devices)))
        return response


    ########################################################################################################
    #
    # ADD DEVICE
    #
    # - Request:
    #   POST /devices/device/<devicename>
    #   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
    #   data: {'deviceid': string, 'serialnumber': string, 'poemacaddress': string}
    #   // poemacaddress is a mac address in uppercase string ex. AA:BB:CC:DD:EE:FF
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    #
    # DELETE DEVICE
    #
    # - Request:
    #   DELETE /devices/device/<devicename>
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def register_device(self, devicename):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Add/Delete Device: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Add/Delete Device: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('register_device {} devicename={}'.format(username, devicename))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0 or len(devicename) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Add/Delete Device: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Add/Delete Device: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Add/Delete Device: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        if flask.request.method == 'POST':
            if orgname is not None:
                # check authorization
                if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.CREATE) == False:
                    response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                    print('\r\nERROR Add Device: Authorization not allowed [{}]\r\n'.format(username))
                    return response, status.HTTP_401_UNAUTHORIZED

            # check parameters exist
            data = flask.request.get_json()
            if data is None:
                response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
                print('\r\nERROR Add Device: Parameters not included [{},{}]\r\n'.format(entityname, devicename))
                return response, status.HTTP_400_BAD_REQUEST
            if data.get("deviceid") is None or data.get("serialnumber") is None or data.get("poemacaddress") is None:
                response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
                print('\r\nERROR Add Device: Parameters not included [{},{}]\r\n'.format(entityname, devicename))
                return response, status.HTTP_400_BAD_REQUEST
            #print(data["deviceid"])
            #print(data["serialnumber"])

            # check devicename
            if len(devicename) > 32 or len(devicename) == 0:
                response = json.dumps({'status': 'NG', 'message': 'Devicename length is invalid'})
                print('\r\nERROR Add Device: Devicename length is invalid [{},{}]\r\n'.format(entityname, devicename))
                return response, status.HTTP_400_BAD_REQUEST

            # check parameters are valid format and length
            result1 = self._check_deviceid(data["deviceid"])
            result2 = self._check_serialnumber(data["deviceid"], data["serialnumber"])
            result3 = self._check_macaddress(data["poemacaddress"])
            if not result1:
                response = json.dumps({'status': 'NG', 'message': 'UUID is invalid'})
                print('\r\nERROR Add Device: Device UUID is invalid [{},{}]\r\n'.format(entityname, devicename))
                return response, status.HTTP_400_BAD_REQUEST
            if not result2:
                response = json.dumps({'status': 'NG', 'message': 'Serial Number is invalid'})
                print('\r\nERROR Add Device: Serial Number is invalid [{},{}]\r\n'.format(entityname, devicename))
                return response, status.HTTP_400_BAD_REQUEST
            if not result3:
                response = json.dumps({'status': 'NG', 'message': 'POE MAC Address is invalid'})
                print('\r\nERROR Add Device: POE MAC Address is invalid [{},{}]\r\n'.format(entityname, devicename))
                return response, status.HTTP_400_BAD_REQUEST


            # check if device is registered
            # a user cannot register the same device name
            if self.database_client.find_device(entityname, devicename):
                response = json.dumps({'status': 'NG', 'message': 'Device name is already taken'})
                print('\r\nERROR Add Device: Device name is already taken [{},{}]\r\n'.format(entityname, devicename))
                return response, status.HTTP_409_CONFLICT

            # check if UUID is unique
            # a user cannot register a device if it is already registered by another user
            if self.database_client.find_device_by_id(data["deviceid"]):
                response = json.dumps({'status': 'NG', 'message': 'Device UUID is already registered'})
                print('\r\nERROR Add Device: Device uuid is already registered[{}]\r\n'.format(data["deviceid"]))
                return response, status.HTTP_409_CONFLICT

            # TODO: check if serial number matches UUID

            # check if poe mac address is unique
            if self.database_client.find_device_by_poemacaddress(data["poemacaddress"]):
                response = json.dumps({'status': 'NG', 'message': 'Device POE MAC Address is already registered'})
                print('\r\nERROR Add Device: Device POE MAC Address is already registered[{}]\r\n'.format(data["deviceid"]))
                return response, status.HTTP_409_CONFLICT


            # add device to database
            result = self.database_client.add_device(entityname, devicename, data["deviceid"], data["serialnumber"], data['poemacaddress'])
            #print(result)
            if not result:
                response = json.dumps({'status': 'NG', 'message': 'Device could not be registered'})
                print('\r\nERROR Add Device: Device could not be registered [{},{}]\r\n'.format(entityname, devicename))
                return response, status.HTTP_400_BAD_REQUEST

            # add and configure message broker user
            try:
                # Password is now a combination of UUID, Serial Number and POE Mac Address
                # Previously, PASSWORD is just the DEVICE_SERIAL
                #devicepass = data["serialnumber"]
                deviceuser = data["deviceid"]
                devicepass = self.compute_password(config.CONFIG_JWT_SECRET_KEY_DEVICE, data["deviceid"], data["serialnumber"], data['poemacaddress'], debug=False)
                #print(devicepass)

                # if secure is True, device will only be able to publish and subscribe to server/<deviceid>/# and <deviceid>/# respectively
                # this means a hacker can only hack that particular device and will not be able to eavesdrop on other devices
                # if secure is False, device will be able to publish and subscribe to/from other devices which enables multi-subscriptions
                secure = True
                result = message_broker_api().register(deviceuser, devicepass, secure)
                #print(result)
                if not result:
                    response = json.dumps({'status': 'NG', 'message': 'Device could not be registered in message broker'})
                    print('\r\nERROR Add Device: Device could not be registered  in message broker [{},{}]\r\n'.format(entityname, devicename))
                    return response, status.HTTP_500_INTERNAL_SERVER_ERROR
            except Exception as e:
                print("Exception encountered {}".format(e))
                response = json.dumps({'status': 'NG', 'message': 'Device could not be registered in message broker'})
                print('\r\nERROR Add Device: Device could not be registered in message broker [{},{}]\r\n'.format(entityname, devicename))
                return response, status.HTTP_500_INTERNAL_SERVER_ERROR

            # add default uart notification recipients
            # this is necessary so that an entry exist for consumption of notification manager
            try:
                source = "uart"
                notification = rest_api_utils.utils().build_default_notifications(source, token, self.database_client, username)
                if notification is not None:
                    self.database_client.update_device_notification(entityname, devicename, source, notification)
            except Exception as e:
                print("Exception encountered {} update_device_notification".format(e))

            # create free subscription for device
            try:
                res = subscription_service.create_free_sub_for_new_device_by_device_id(data["deviceid"])
                if not res:
                    print('subscription created failed create_free_sub_for_new_device_by_device_id')
            except Exception as e:
                print("Exception encountered {} create_free_sub_for_new_device_by_device_id".format(e))

            # send email confirmation
            try:
                pubtopic = CONFIG_PREPEND_REPLY_TOPIC + CONFIG_SEPARATOR + data["deviceid"] + CONFIG_SEPARATOR + "email" + CONFIG_SEPARATOR + "send_device_registration"
                payload  = json.dumps({"serialnumber": data["serialnumber"], "recipients": [username]})
                self.messaging_client.publish(pubtopic, payload)
            except Exception as e:
                print("Exception encountered {} publish".format(e))


            msg = {'status': 'OK', 'message': 'Devices registered successfully.'}
            if new_token:
                msg['new_token'] = new_token
            response = json.dumps(msg)
            print('\r\nDevice registered successful: {}\r\n{}\r\n'.format(username, response))
            return response

        elif flask.request.method == 'DELETE':
            if orgname is not None:
                # check authorization
                if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.DELETE) == False:
                    response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                    print('\r\nERROR Delete Device: Authorization not allowed [{}]\r\n'.format(username))
                    return response, status.HTTP_401_UNAUTHORIZED

            # check if device is registered
            device = self.database_client.find_device(entityname, devicename)
            if not device:
                response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
                print('\r\nERROR Delete Device: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
                return response, status.HTTP_404_NOT_FOUND


            # cleanup device
            self.device_cleanup(entityname, device['deviceid'], device['devicename'])


            # send email confirmation
            try:
                pubtopic = CONFIG_PREPEND_REPLY_TOPIC + CONFIG_SEPARATOR + device["deviceid"] + CONFIG_SEPARATOR + "email" + CONFIG_SEPARATOR + "send_device_unregistration"
                payload  = json.dumps({"serialnumber": device["serialnumber"], "recipients": [username]})
                self.messaging_client.publish(pubtopic, payload)
            except:
                pass


            msg = {'status': 'OK', 'message': 'Devices unregistered successfully.'}
            if new_token:
                msg['new_token'] = new_token
            response = json.dumps(msg)
            print('\r\nDevice unregistered successful: {}\r\n{}\r\n'.format(username, response))
            return response


    ########################################################################################################
    #
    # GET DEVICE
    #
    # - Request:
    #   GET /devices/device/<devicename>
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'device': {'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': string, 'heartbeat': string, 'version': string, location: {'latitude': float, 'longitude': float} }}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_device(self, devicename):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get Device: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Device: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        #print('get_device {} devicename={}'.format(username, devicename))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0 or len(devicename) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get Device: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Device: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get Device: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get Device: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # check if device is registered
        device = self.database_client.find_device(entityname, devicename)
        if not device:
            response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
            print('\r\nERROR Get Device: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND


        msg = {'status': 'OK', 'message': 'Devices queried successfully.', 'device': device}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        #print('\r\nDevice queried successful: {}\r\n{}\r\n'.format(username, response))
        return response


    ########################################################################################################
    #
    # GET DEVICE DESCRIPTOR
    #
    # - Request:
    #   GET /devices/device/<devicename>/descriptor
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'descriptor': {} }}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_device_descriptor(self, devicename):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get Device Descriptor: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Device Descriptor: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        #print('get_device_descriptor {} devicename={}'.format(username, devicename))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0 or len(devicename) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get Device Descriptor: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Device Descriptor: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get Device Descriptor: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get Device Descriptor: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        if True:
            # check if device is registered
            device = self.database_client.find_device(entityname, devicename)
            if not device:
                response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
                print('\r\nERROR Get Device Descriptor: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
                return response, status.HTTP_404_NOT_FOUND

            # get descriptor from database
            # this assumes that the device sends the descriptor during device bootup
            descriptor = self.database_client.get_device_descriptor(entityname, devicename)
            if descriptor is None:
                # device did not send descriptor on bootup, so query the device
                api = "get_descriptor"
                data = {}
                data['token'] = {'access': auth_header_token}
                data['devicename'] = devicename
                data['username'] = username
                response, status_return = self.messaging_requests.process(api, data)
                if status_return == 503: # HTTP_503_SERVICE_UNAVAILABLE
                    return response, status_return
                else:
                    # get the descriptor in response
                    response = json.loads(response)
                    descriptor = response['value']
                    self.database_client.set_device_descriptor(entityname, devicename, descriptor)
                    response = json.dumps(response)
        else:
            # get latest descriptor from device
            # this assumes that the device does not send the descriptor during device bootup
            # and that it can change everytime so device must be queried instead of checking database
            api = "get_descriptor"
            data = {}
            data['token'] = {'access': auth_header_token}
            data['devicename'] = devicename
            data['username'] = username
            response, status_return = self.messaging_requests.process(api, data)
            if status_return == 503: # HTTP_503_SERVICE_UNAVAILABLE
                # if device is not available get descriptor from database
                descriptor = self.database_client.get_device_descriptor(entityname, devicename)
                if descriptor is None:
                    return response, status_return
            else:
                # get the descriptor in response
                response = json.loads(response)
                descriptor = response['value']
                self.database_client.set_device_descriptor(entityname, devicename, descriptor)
                response = json.dumps(response)


        msg = {'status': 'OK', 'message': 'Device Descriptor queried successfully.', 'descriptor': descriptor}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        #print('\r\nDevice Descriptor queried successful: {}\r\n{}\r\n'.format(username, response))
        return response


    ########################################################################################################
    #
    # UPDATE DEVICE NAME
    #
    # - Request:
    #   POST /devices/device/<devicename>/name
    #   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
    #   data: {'new_devicename': string}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def update_devicename(self, devicename):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Update Device Name: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Update Device Name: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        #print('get_device {} devicename={}'.format(username, devicename))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0 or len(devicename) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Update Device Name: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Update Device Name: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Update Device Name: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get Device: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED

            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username

        # check if device is registered
        device = self.database_client.find_device(entityname, devicename)
        if not device:
            response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
            print('\r\nERROR Update Device Name: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND


        # check if new device name is already registered
        data = flask.request.get_json()
        if data is None:
            response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
            print('\r\nERROR Update Device Name: Parameters not included [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_400_BAD_REQUEST
        if data.get("new_devicename") is None:
            response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
            print('\r\nERROR Update Device Name: Parameters not included [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_400_BAD_REQUEST
        if len(data["new_devicename"]) > 32 or len(data["new_devicename"]) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Devicename length is invalid'})
            print('\r\nERROR Update Device Name: Devicename length is invalid\r\n')
            return response, status.HTTP_400_BAD_REQUEST
        device = self.database_client.find_device(entityname, data["new_devicename"])
        if device:
            response = json.dumps({'status': 'NG', 'message': 'Device name is already registered'})
            print('\r\nERROR Update Device Name: Device name is already registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_400_BAD_REQUEST


        # update device name in notifications and configurations
        devices = self.database_client.get_devices(entityname)
        try:
            for devicex in devices:
                self.database_client.update_device_notification_devicenamechange_by_deviceid(devicex["deviceid"], devicename, data["new_devicename"])
        except Exception as e:
            print("Exception update_device_notification_devicenamechange_by_deviceid")
            print(e)
        try:
            for devicex in devices:
                self.database_client.update_device_peripheral_configuration_devicenamechange_by_deviceid(devicex["deviceid"], devicename, data["new_devicename"])
        except Exception as e:
            print("Exception update_device_peripheral_configuration_devicenamechange_by_deviceid")
            print(e)

        # update device name in subscription
        try:
            subscription = subscription_service.get_one({'deviceid': device["deviceid"]})
            subscription.devicename = data["new_devicename"]
            subscription_service.update(subscription._id,subscription)
        except Exception as e:
            print(e)


        # update the device name
        self.database_client.update_devicename(entityname, devicename, data["new_devicename"])


        msg = {'status': 'OK', 'message': 'Device name updated successfully.'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        #print('\r\nDevice name updated successful: {}\r\n{}\r\n'.format(username, response))
        return response


    ########################################################################################################
    # GET  /devices/device/<devicename>/xxx
    # POST /devices/device/<devicename>/xxx
    ########################################################################################################
    #
    # GET STATUS
    # - Request:
    #   GET /devices/device/<devicename>/status
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   { 'status': 'OK', 'message': string, 'value': { 'status': int, 'version': string } }
    #   { 'status': 'NG', 'message': string, 'value': { 'heartbeat': string, 'version': string} }
    #
    def get_status(self, devicename):
        api = 'get_status'

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED

        # get username from token
        data = {}
        data['token'] = {'access': auth_header_token}
        data['devicename'] = devicename
        username = self.database_client.get_username_from_token(data['token'])
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        data['username'] = username
        #print('get_status {} devicename={}'.format(data['username'], data['devicename']))


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get Status: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username

        response, status_return = self.messaging_requests.process(api, data)
        if status_return == 503: # HTTP_503_SERVICE_UNAVAILABLE
            # if device is unreachable, get the cached heartbeat and version
            cached_value = self.database_client.get_device_cached_values(entityname, devicename)
            if not cached_value:
                return response, status_return
            response = json.loads(response)
            response['value'] = cached_value
            response = json.dumps(response)
            return response, status_return

        if status_return == 200:
            response = json.loads(response)
            version = response["value"]["version"]
            response = json.dumps(response)
            self.database_client.save_device_version(entityname, devicename, version)

        return response



    #
    # GET STATUSES
    # - Request:
    #   GET /devices/status
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   { 'status': 'OK', 'message': string, 'value': [{ "devicename": string, 'status': int, 'version': string }] }
    #   { 'status': 'NG', 'message': string, 'value': [{ "devicename": string, 'heartbeat': string, 'version': string}] }
    #
    def get_statuses(self):
        api = 'get_status'

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED

        # get username from token
        token = {'access': auth_header_token}
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        #print('get_status {} devicename={}'.format(data['username'], data['devicename']))


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get Statuses: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        thread_list = []
        devices = self.database_client.get_devicenames(entityname)
        for device in devices:
            data = {}
            data['token'] = token
            data['devicename'] = device["devicename"]
            data['username'] = entityname
            thr = threading.Thread(target = self.get_status_threaded, args = (entityname, api, data, device, ))
            thread_list.append(thr) 
            thr.start()
        for thr in thread_list:
            thr.join()
        #print(devices)

        msg = {'status': 'OK', 'message': 'Device statuses queried successfully.', 'devices': devices}
        response = json.dumps(msg)
        return response

    #
    # SET STATUS
    # - Request:
    #   POST /devices/device/<devicename>/status
    #   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
    #   data: { 'status': int }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string, 'value': {'status': string} }
    #   { 'status': 'NG', 'message': string}
    #
    def set_status(self, devicename):
        api = 'set_status'

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED

        # get parameter input
        data = flask.request.get_json()
        if data is None:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Set status: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST
        if data.get('status') is None:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Set status: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # get username from token
        data['token'] = {'access': auth_header_token}
        data['devicename'] = devicename
        data['username'] = self.database_client.get_username_from_token(data['token'])
        if data['username'] is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        #print('set_status {} devicename={}'.format(data['username'], data['devicename']))

        return self.messaging_requests.process(api, data)

    #
    # GET SETTINGS
    # - Request:
    #   GET /devices/device/<devicename>/settings
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   { 'status': 'OK', 'message': string }
    #   { 'status': 'NG', 'message': string }
    #
    def get_settings(self, devicename):
        api = 'get_settings'

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED

        # get username from token
        data = {}
        data['token'] = {'access': auth_header_token}
        data['devicename'] = devicename
        username = self.database_client.get_username_from_token(data['token'])
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        data['username'] = username
        #print('get_settings {} devicename={}'.format(data['username'], data['devicename']))

        return self.messaging_requests.process(api, data)

    #
    # SET SETTINGS
    # - Request:
    #   POST /devices/device/<devicename>/settings
    #   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
    #   data: { 'status': int }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string, 'value': { 'sensorrate': int } }
    #   { 'status': 'NG', 'message': string}
    #
    def set_settings(self, devicename):
        api = 'set_settings'

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED

        # get parameter input
        data = flask.request.get_json()
        if data is None:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Set settings: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # get username from token
        data['token'] = {'access': auth_header_token}
        data['devicename'] = devicename
        data['username'] = self.database_client.get_username_from_token(data['token'])
        if data['username'] is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        #print('set_settings {} devicename={}'.format(data['username'], data['devicename']))

        return self.messaging_requests.process(api, data)





    ########################################################################################################
    #
    # GET ALL XXX DEVICES
    #
    # - Request:
    #   GET /devices/device/DEVICENAME/i2c/sensors
    #   headers: { 'Authorization': 'Bearer ' + token.access }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string}, ...] }
    #   { 'status': 'NG', 'message': string }
    #
    #
    # GET ALL ADC DEVICES
    # GET ALL 1WIRE DEVICES
    # GET ALL TPROBE DEVICES
    #
    # - Request:
    #   GET /devices/device/DEVICENAME/adc/sensors
    #   GET /devices/device/DEVICENAME/1wire/sensors
    #   GET /devices/device/DEVICENAME/tprobe/sensors
    #   headers: { 'Authorization': 'Bearer ' + token.access }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'manufacturer': string, 'model': string, 'timestamp': string}, ...] }
    #   { 'status': 'NG', 'message': string }
    #
    ########################################################################################################
    def get_all_xxx_sensors(self, devicename, xxx):

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get All {} Sensors: Invalid authorization header\r\n'.format(xxx))
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get All {} Sensors: Token expired\r\n'.format(xxx))
            return response, status.HTTP_401_UNAUTHORIZED
        #print('get_all_i2c_sensors {} devicename={}'.format(username, devicename))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get All {} Sensors: Empty parameter found\r\n'.format(xxx))
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get All {} Sensors: Token expired [{}]\r\n'.format(xxx, username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get All {} Sensors: Token is invalid [{}]\r\n'.format(xxx, username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get All Sensors: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username

        sensors = self.database_client.get_all_sensors(entityname, devicename, xxx)


        msg = {'status': 'OK', 'message': 'All Sensors queried successfully.', 'sensors': sensors}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        #print('\r\nGet All {} Sensors successful: {}\r\n{} sensors\r\n'.format(xxx, username, len(sensors)))
        return response


    ########################################################################################################
    #
    # GET XXX DEVICES
    #
    # - Request:
    #   GET /devices/device/DEVICENAME/i2c/NUMBER/sensors
    #   headers: { 'Authorization': 'Bearer ' + token.access }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string, 'enabled': int}, ...] }
    #   { 'status': 'NG', 'message': string }
    #
    #
    # GET ADC DEVICES
    # GET 1WIRE DEVICES
    # GET TPROBE DEVICES
    #
    # - Request:
    #   GET /devices/device/DEVICENAME/adc/NUMBER/sensors
    #   GET /devices/device/DEVICENAME/1wire/NUMBER/sensors
    #   GET /devices/device/DEVICENAME/tprobe/NUMBER/sensors
    #   headers: { 'Authorization': 'Bearer ' + token.access }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'manufacturer': string, 'model': string, 'timestamp': string, 'enabled': int}, ...] }
    #   { 'status': 'NG', 'message': string }
    #
    ########################################################################################################
    def get_xxx_sensors(self, devicename, xxx, number):

        if xxx == "i2c" or xxx == "adc" or xxx == "1wire" or xxx == "tprobe":
            api = 'get_{}_devs'.format(xxx)
        else:
            api = 'get_ldsu_devs'

        # check number parameter
        #if int(number) > 4 or int(number) < 1:
        #    response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        #    print('\r\nERROR Invalid parameters\r\n')
        #    return response, status.HTTP_400_BAD_REQUEST

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get {} Sensors: Invalid authorization header\r\n'.format(xxx))
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get {} Sensors: Token expired\r\n'.format(xxx))
            return response, status.HTTP_401_UNAUTHORIZED
        #print('get_{}_sensors {} devicename={} number={}'.format(xxx, username, devicename, number))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get {} Sensors: Empty parameter found\r\n'.format(xxx))
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get {} Sensors: Token expired [{}]\r\n'.format(xxx, username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get {} Sensors: Token is invalid [{}]\r\n'.format(xxx, username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get Peripheral Sensors: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # query peripheral sensors
        sensors = self.database_client.get_sensors(entityname, devicename, xxx, number)

        # set to query device
        data = {}
        data['token'] = token
        data['devicename'] = devicename
        data['username'] = username
        if api != "get_ldsu_devs":
            data["number"] = int(number)

        # query device
        response, status_return = self.messaging_requests.process(api, data)

        if status_return == 200:
            # map queried result with database result
            #print("from device")
            response = json.loads(response)
            #print(response["value"])

            if api == "get_ldsu_devs":
                pass

            elif xxx == "i2c":
                # if I2C
                #print("I2C")
                for sensor in sensors:
                    found = False
                    for item in response["value"]:
                        # match found for database result and actual device result
                        # set database record to configured and actual device item["enabled"]
                        if sensor["address"] == item["address"]:
                            # device is configured
                            self.database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], item["enabled"], 1)
                            sensor["enabled"] = item["enabled"]
                            sensor["configured"] = 1
                            found = True
                            break
                    # no match found
                    # set database record to unconfigured and disabled
                    if found == False:
                        self.database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], 0, 0)
                        sensor["enabled"] = 0
                        sensor["configured"] = 0
            elif xxx == "adc" or xxx == "1wire" or xxx == "tprobe":
                # if ADC/1WIRE/TPROBE
                #print("ADC/1WIRE/TPROBE")
                for sensor in sensors:
                    found = False
                    # check if this is the active sensor
                    # if not the active sensor, then set database record to unconfigured and disabled
                    #print(sensor)
    #                if sensor['configured']:
                    for item in response["value"]:
                        if item["class"] == rest_api_utils.utils().get_i2c_device_class(sensor["class"]):
                            self.database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], item["enabled"], 1)
                            sensor["enabled"] = item["enabled"]
                            sensor["configured"] = 1
                            found = True
                            break
                    if found == False:
                        # set database record to unconfigured and disabled
                        self.database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], 0, 0)
                        sensor["enabled"] = 0
                        sensor["configured"] = 0
    #                else:
    #                    # set database record to unconfigured and disabled
    #                    self.database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], 0, 0)
    #                    sensor["enabled"] = 0
    #                    sensor["configured"] = 0
            #print()
        else:
            # cannot communicate with device so set database record to unconfigured and disabled
            self.database_client.disable_unconfigure_sensors(entityname, devicename)
            for sensor in sensors:
                sensor["enabled"] = 0
                sensor["configured"] = 0

        # get sensor readings for enabled input devices
        for sensor in sensors:
            if sensor['type'] == 'input' and sensor['enabled']:
                address = None
                if sensor.get("address") is not None:
                    address = sensor["address"]
                source = "{}{}".format(xxx, number)
                sensor_reading = self.database_client.get_sensor_reading(entityname, devicename, source, address)
                if sensor_reading is not None:
                    sensor['readings'] = sensor_reading

        if status_return == 200:
            msg = {'status': 'OK', 'message': 'Sensors queried successfully.', 'sensors': sensors}
        else:
            msg = {'status': 'OK', 'message': 'Sensors queried successfully but device is offline.', 'sensors': sensors}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        #print('\r\nGet {} Sensors successful: {}\r\n{} sensors\r\n'.format(xxx, username, len(sensors)))
        return response





    ########################################################################################################
    #
    # ADD I2C DEVICE
    #
    # - Request:
    #   POST /devices/device/<devicename>/i2c/NUMBER/sensors/sensor/<sensorname>
    #   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
    #   data: {'address': int, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'attributes': []}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    # ADD ADC DEVICE
    # ADD 1WIRE DEVICE
    # ADD TPROBE DEVICE
    #
    # - Request:
    #   POST /devices/device/<devicename>/adc/NUMBER/sensors/sensor/<sensorname>
    #   POST /devices/device/<devicename>/1wire/NUMBER/sensors/sensor/<sensorname>
    #   POST /devices/device/<devicename>/tprobe/NUMBER/sensors/sensor/<sensorname>
    #   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
    #   data: {'manufacturer': string, 'model': string, 'class': string, 'type': string, 'attributes': []}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    #
    # DELETE I2C DEVICE
    #
    # - Request:
    #   DELETE /devices/device/<devicename>/i2c/NUMBER/sensors/sensor/<sensorname>
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    # DELETE ADC DEVICE
    # DELETE 1WIRE DEVICE
    # DELETE TPROBE DEVICE
    #
    # - Request:
    #   DELETE /devices/device/<devicename>/adc/NUMBER/sensors/sensor/<sensorname>
    #   DELETE /devices/device/<devicename>/1wire/NUMBER/sensors/sensor/<sensorname>
    #   DELETE /devices/device/<devicename>/tprobe/NUMBER/sensors/sensor/<sensorname>
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def register_xxx_sensor(self, devicename, xxx, number, sensorname):

        # check number parameter
        if int(number) > 4 or int(number) < 1:
            response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
            print('\r\nERROR Invalid parameters\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Add/Delete {} Sensor: Invalid authorization header\r\n'.format(xxx))
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Add/Delete {} Sensor: Token expired\r\n'.format(xxx))
            return response, status.HTTP_401_UNAUTHORIZED
        #print('register_{}_sensor {} devicename={} number={} sensorname={}'.format(xxx, username, devicename, number, sensorname))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0 or len(devicename) == 0 or len(sensorname) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Add/Delete {} Sensor: Empty parameter found\r\n'.format(xxx))
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Add/Delete {} Sensor: Token expired [{}]\r\n'.format(xxx, username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Add/Delete {} Sensor: Token is invalid [{}]\r\n'.format(xxx, username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        if flask.request.method == 'POST':
            if orgname is not None:
                # check authorization
                if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
                    response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                    print('\r\nERROR Add Peripheral Sensor: Authorization not allowed [{}]\r\n'.format(username))
                    return response, status.HTTP_401_UNAUTHORIZED

            # get parameters
            data = flask.request.get_json()
            #print(data)
            if xxx == 'i2c':
                if data['address'] is None:
                    response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
                    print('\r\nERROR Add {} Sensor: Parameters not included [{},{}]\r\n'.format(xxx, entityname, devicename))
                    return response, status.HTTP_400_BAD_REQUEST
                data["address"] = int(data["address"])
                if data["address"] == 0:
                    response = json.dumps({'status': 'NG', 'message': 'Invalid address'})
                    print('\r\nERROR Add {} Sensor: Invalid address [{},{}]\r\n'.format(xxx, entityname, devicename))
                    return response, status.HTTP_400_BAD_REQUEST
                # check if sensor address is registered
                # address should be unique within a slot
                if self.database_client.get_sensor_by_address(entityname, devicename, xxx, number, data["address"]):
                    response = json.dumps({'status': 'NG', 'message': 'Sensor address is already taken'})
                    print('\r\nERROR Add {} Sensor: Sensor address is already taken [{},{},{}]\r\n'.format(xxx, entityname, devicename, data["address"]))
                    return response, status.HTTP_409_CONFLICT

            if data["manufacturer"] is None or data["model"] is None or data["class"] is None or data["type"] is None or data["units"] is None or data["formats"] is None or data["attributes"] is None:
                response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
                print('\r\nERROR Add {} Sensor: Parameters not included [{},{}]\r\n'.format(xxx, entityname, devicename))
                return response, status.HTTP_400_BAD_REQUEST
            #print(data["manufacturer"])
            #print(data["model"])

            # check if sensor is registered
            # name should be unique all throughout the slots
            if self.database_client.check_sensor(entityname, devicename, sensorname):
                response = json.dumps({'status': 'NG', 'message': 'Sensor name is already taken'})
                print('\r\nERROR Add {} Sensor: Sensor name is already taken [{},{},{}]\r\n'.format(xxx, entityname, devicename, sensorname))
                return response, status.HTTP_409_CONFLICT

            # can only register 1 device for adc/1wire/tprobe
            if xxx != 'i2c':
                if self.database_client.get_sensors_count(entityname, devicename, xxx, number) > 0:
                    response = json.dumps({'status': 'NG', 'message': 'Cannot add more than 1 sensor for {}'.format(xxx)})
                    print('\r\nERROR Add {} Sensor: Cannot add more than 1 sensor [{},{},{}]\r\n'.format(xxx, entityname, devicename, sensorname))
                    return response, status.HTTP_400_BAD_REQUEST

            # add sensor to database
            result = self.database_client.add_sensor(entityname, devicename, xxx, number, sensorname, data)
            #print(result)
            if not result:
                response = json.dumps({'status': 'NG', 'message': 'Sensor could not be registered'})
                print('\r\nERROR Add {} Sensor: Sensor could not be registered [{},{}]\r\n'.format(xxx, entityname, devicename))
                return response, status.HTTP_500_INTERNAL_SERVER_ERROR

            msg = {'status': 'OK', 'message': 'Sensor registered successfully.'}
            if new_token:
                msg['new_token'] = new_token
            response = json.dumps(msg)
            #print('\r\n{} Sensor registered successful: {}\r\n{}\r\n'.format(xxx, entityname, response))
            return response

        elif flask.request.method == 'DELETE':
            if orgname is not None:
                # check authorization
                if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.DELETE) == False:
                    response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                    print('\r\nERROR Delete Peripheral Sensor: Authorization not allowed [{}]\r\n'.format(username))
                    return response, status.HTTP_401_UNAUTHORIZED

            # check if sensor is registered
            sensor = self.database_client.get_sensor(entityname, devicename, xxx, number, sensorname)
            if not sensor:
                response = json.dumps({'status': 'NG', 'message': 'Sensor is not registered'})
                print('\r\nERROR Delete {} Sensor: Sensor is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
                return response, status.HTTP_404_NOT_FOUND

            # delete necessary sensor-related database information
            self.sensor_cleanup(entityname, devicename, None, xxx, number, sensorname, sensor)

            msg = {'status': 'OK', 'message': 'Sensor unregistered successfully.'}
            if new_token:
                msg['new_token'] = new_token
            response = json.dumps(msg)
            #print('\r\n{} Sensor unregistered successful: {}\r\n{}\r\n'.format(xxx, username, response))
            return response


    ########################################################################################################
    #
    # GET I2C DEVICE
    #
    # - Request:
    #   GET /devices/device/<devicename>/i2c/NUMBER/sensors/sensor/<sensorname>
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'sensor': {'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string}}
    #   {'status': 'NG', 'message': string}
    #
    # GET ADC DEVICE
    # GET 1WIRE DEVICE
    # GET TPROBE DEVICE
    #
    # - Request:
    #   GET /devices/device/<devicename>/adc/NUMBER/sensors/sensor/<sensorname>
    #   GET /devices/device/<devicename>/1wire/NUMBER/sensors/sensor/<sensorname>
    #   GET /devices/device/<devicename>/tprobe/NUMBER/sensors/sensor/<sensorname>
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'sensor': {'sensorname': string, 'manufacturer': string, 'model': string, 'timestamp': string}}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_xxx_sensor(self, devicename, xxx, number, sensorname):

        # check number parameter
        if int(number) > 4 or int(number) < 1:
            response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
            print('\r\nERROR Invalid parameters\r\n')
            return response, status.HTTP_400_BAD_REQUEST

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
        #print('get_{}_sensor {} devicename={} number={} sensorname={}'.format(xxx, username, devicename, number, sensorname))

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


        msg = {'status': 'OK', 'message': 'Sensor queried successfully.', 'sensor': sensor}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        #print('\r\n{} Sensor queried successful: {}\r\n{}\r\n'.format(xxx, username, response))
        return response


    ########################################################################################################
    #
    # DOWNLOAD DEVICE SENSOR DATA
    #
    # - Request:
    #   POST /devices/device/DEVICENAME/sensordata
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    # CLEAR DEVICE SENSOR DATA
    #
    # - Request:
    #   POST /devices/device/DEVICENAME/sensordata
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def download_device_sensor_data(self, devicename):

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get Device Sensor Data: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Download Device Sensor Data: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        #print('download_device_sensor_data {} devicename={}'.format(username, devicename))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0 or len(devicename) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Download Device Sensor Data: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Download Device Sensor Data: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Download Device Sensor Data: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        if flask.request.method == 'POST':
            if orgname is not None:
                # check authorization
                if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
                    response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                    print('\r\nERROR Download Device Sensor Data: Authorization not allowed [{}]\r\n'.format(username))
                    return response, status.HTTP_401_UNAUTHORIZED

            # check if device is registered
            device = self.database_client.find_device(entityname, devicename)
            if not device:
                response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
                print('\r\nERROR Download Device Sensor Data: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
                return response, status.HTTP_404_NOT_FOUND

            # get device ldsus
            ldsus = self.database_client.get_ldsus(username, devicename)
            if len(ldsus) == 0:
                response = json.dumps({'status': 'NG', 'message': 'No LDSU is registered'})
                print('\r\nERROR Download Device Sensor Data: No LDSU is registered [{},{}]\r\n'.format(entityname, devicename))
                return response, status.HTTP_404_NOT_FOUND

            # get name of user
            name = None
            info = self.database_client.get_user_info(token["access"])
            if info:
                # handle no family name
                if 'given_name' in info:
                    name = info['given_name']
                if 'family_name' in info:
                    if info['family_name'] != "NONE":
                        name += " " + info['family_name']

            # send to downloader manager
            payload = {"name": name, "email": username, "devicename": device["devicename"], "ldsus": []}
            for ldsu in ldsus:
                numdevices = self.device_client.get_obj_numdevices(ldsu["descriptor"]["OBJ"])
                for x in range(numdevices):
                    #print("{} {}/{}".format(ldsu["descriptor"]["OBJ"], x, numdevices))
                    descriptor = self.device_client.get_objidx(ldsu["descriptor"]["OBJ"], x)
                    type = self.device_client.get_objidx_type(descriptor)
                    format = self.device_client.get_objidx_format(descriptor)
                    accuracy = self.device_client.get_objidx_accuracy(descriptor)
                    payload["ldsus"].append({"UID": ldsu["UID"], "SAID": x, "FORMAT": format, "ACCURACY": accuracy})
            try:
                pubtopic = CONFIG_PREPEND_REPLY_TOPIC + CONFIG_SEPARATOR + device["deviceid"] + CONFIG_SEPARATOR + "download_device_sensor_data"
                payload = json.dumps(payload)
                self.messaging_client.publish(pubtopic, payload)
            except:
                pass

            msg = {'status': 'OK', 'message': 'An email will be sent to you shortly once it is ready to download.'}

        elif flask.request.method == 'DELETE':
            if orgname is not None:
                # check authorization
                if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.DELETE) == False:
                    response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                    print('\r\nERROR Delete Device Sensor Data: Authorization not allowed [{}]\r\n'.format(username))
                    return response, status.HTTP_401_UNAUTHORIZED

            # check if device is registered
            device = self.database_client.find_device(entityname, devicename)
            if not device:
                response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
                print('\r\nERROR Delete Device Sensor Data: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
                return response, status.HTTP_404_NOT_FOUND

            self.database_client.delete_device_sensor_reading(entityname, devicename)
            #print("clear_device_sensor_data")
            msg = {'status': 'OK', 'message': 'Sensor data deleted successfully.'}


        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        #print('\r\nSensor download triggered successful: {}\r\n{}\r\n'.format(username, response))
        return response