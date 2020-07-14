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
from rest_api_device import device



#CONFIG_SEPARATOR            = '/'
#CONFIG_PREPEND_REPLY_TOPIC  = "server"



class device_ldsbus:

    def __init__(self, database_client, messaging_requests, messaging_client, device_client):
        self.database_client = database_client
        self.messaging_requests = messaging_requests
        self.messaging_client = messaging_client
        self.device_client = device_client



    ########################################################################################################
    # 
    # GET LDS BUS
    #
    # - Request:
    #   GET /devices/device/DEVICENAME/ldsbus/PORTNUMBER
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   // PORT_NUMBER can be 1, 2, 3, or 0 (0 if all lds bus)
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'ldsbus': obj }
    #   {'status': 'NG', 'message': string}
    #
    # 
    # DELETE LDS BUS
    #
    # - Request:
    #   GET /devices/device/DEVICENAME/ldsbus/PORTNUMBER
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   // PORT_NUMBER can be 1, 2, 3, or 0 (0 if all lds bus)
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'ldsbus': obj }
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_lds_bus(self, devicename, portnumber):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get LDSBUS: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get LDSBUS: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_lds_bus {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get LDSBUS: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get LDSBUS: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get LDSBUS: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # check if device is registered
        deviceinfo = self.database_client.find_device(entityname, devicename)
        if not deviceinfo:
            response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
            print('\r\nERROR Get LDSBUS: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        if flask.request.method == 'GET':
            if orgname is not None:
                # check authorization
                if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                    response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                    print('\r\nERROR Get LDSBUS: Authorization not allowed [{}]\r\n'.format(username))
                    return response, status.HTTP_401_UNAUTHORIZED

            #portnumber = "0"
            if portnumber == "0":
                ldsbus = []
                for x in range(3):
                    # get ldsus and sensors in database
                    ldsus = self.database_client.get_ldsus_by_port(entityname, devicename, str(x+1))
                    sensors = self.database_client.get_sensors_by_port(entityname, devicename, str(x+1))

                    # get the sensor reading for all enabled sensors
                    for sensor in sensors:
                        if sensor["enabled"]:
                            reading = self.database_client.get_sensor_reading(entityname, devicename, sensor["source"], int(sensor["number"]))
                            if reading:
                                sensor["readings"] = reading

                    ldsbus.append({
                        "ldsus": ldsus,
                        "sensors": sensors,
                        "actuators": []
                    })

                #print(len(ldsbus))
                #print(len(ldsbus[0]["ldsus"]))
                #print(len(ldsbus[1]["ldsus"]))
                #print(len(ldsbus[2]["ldsus"]))

            elif portnumber == "1" or portnumber == "2" or portnumber == "3":
                # get ldsus and sensors in database
                ldsus = self.database_client.get_ldsus_by_port(entityname, devicename, portnumber)
                sensors = self.database_client.get_sensors_by_port(entityname, devicename, portnumber)

                # get the sensor reading for all enabled sensors
                for sensor in sensors:
                    if sensor["enabled"]:
                        reading = self.database_client.get_sensor_reading(entityname, devicename, sensor["source"], int(sensor["number"]))
                        if reading:
                            sensor["readings"] = reading

                ldsbus = [
                    {
                        "ldsus": ldsus,
                        "sensors": sensors,
                        "actuators": []
                    }
                ]

            else:
                response = json.dumps({'status': 'NG', 'message': 'Port number is not valid'})
                print('\r\nERROR Get LDSBUS: Port number is not valid [{},{}]\r\n'.format(entityname, devicename))
                return response, status.HTTP_404_NOT_FOUND

            msg = {'status': 'OK', 'message': 'LDSBUS queried successfully.', 'ldsbus': ldsbus}

        elif flask.request.method == 'DELETE':
            if orgname is not None:
                # check authorization
                if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.DELETE) == False:
                    response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                    print('\r\nERROR Get LDSBUS: Authorization not allowed [{}]\r\n'.format(username))
                    return response, status.HTTP_401_UNAUTHORIZED

            # cleanup sensors of the LDSUs in the specified port
            device_client = device(self.database_client, self.messaging_requests, self.messaging_client, self.device_client)
            sensors = self.database_client.get_all_device_sensors_by_port_by_deviceid(deviceinfo["deviceid"], portnumber)
            if sensors is not None:
                for sensor in sensors:
                    if sensor.get("source") and sensor.get("number") and sensor.get("sensorname"):
                        device_client.sensor_cleanup(None, None, deviceinfo["deviceid"], sensor["source"], sensor["number"], sensor["sensorname"], sensor)

            # cleanup LDSUs in the specified port
            self.database_client.delete_ldsus_by_port_by_deviceid(deviceinfo["deviceid"], portnumber)
            msg = {'status': 'OK', 'message': 'LDSBUS deleted successfully.'}


        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        return response


    ########################################################################################################
    # 
    # GET LDS BUS LDSUS/SENSORS/ACTUATORS
    #
    # - Request:
    #   GET /devices/device/DEVICENAME/ldsbus/PORTNUMBER/COMPONENT
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   // PORT_NUMBER can be 1, 2, 3, or 0 (0 if all lds bus)
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'ldsbus': obj }
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_lds_bus_component(self, devicename, portnumber, component):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get LDSBUS component: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get LDSBUS component: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_lds_bus_component {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get LDSBUS component: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get LDSBUS component: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get LDSBUS component: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get LDSBUS component: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # check if device is registered
        deviceinfo = self.database_client.find_device(entityname, devicename)
        if not deviceinfo:
            response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
            print('\r\nERROR Get LDSBUS component: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        # check if port number is valid
        if int(portnumber) < 0 or int(portnumber) > 3:
            response = json.dumps({'status': 'NG', 'message': 'Port number is not valid'})
            print('\r\nERROR Get LDSBUS component: Port number is not valid [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND


        # get component in database
        msg = {'status': 'OK', 'message': 'LDSBUS component queried successfully.'}
        if component == "ldsus":

            ldsus = []

            if int(portnumber) != 0:
                ldsus = self.database_client.get_ldsus_by_port(entityname, devicename, portnumber)
            else:
                ldsus = self.database_client.get_ldsus(entityname, devicename)

            msg['ldsus'] = ldsus

        elif component == "sensors":

            sensors = []

            if int(portnumber) != 0:
                sensors = self.database_client.get_sensors_by_port(entityname, devicename, portnumber)
            else:
                sensors = self.database_client.get_all_device_sensors_input(entityname, devicename)

            # get the sensor reading for all enabled sensors
            for sensor in sensors:
                if sensor["enabled"]:
                    reading = self.database_client.get_sensor_reading(entityname, devicename, sensor["source"], int(sensor["number"]))
                    if reading:
                        sensor["readings"] = reading
            msg['sensors'] = sensors

        elif component == "actuators":

            actuators = [] # TODO

            if int(portnumber) != 0:
                pass # TODO
            else:
                pass # TODO

            msg['actuators'] = actuators

        else:
            response = json.dumps({'status': 'NG', 'message': 'Component is not valid'})
            print('\r\nERROR Get LDSBUS component: Component is not valid [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND


        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        return response


    ########################################################################################################
    # 
    # SCAN LDS BUS
    #
    # - Request:
    #   POST /devices/device/DEVICENAME/ldsbus/PORTNUMBER
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   // PORT_NUMBER can be 1, 2, 3, or 0 (0 if all lds bus)
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'ldsbus': obj }
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def scan_lds_bus(self, devicename, portnumber):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Scan LDSBUS: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Scan LDSBUS: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('scan_lds_bus {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Scan LDSBUS: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Scan LDSBUS: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Scan LDSBUS: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Scan LDSBUS: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # check if device is registered
        deviceinfo = self.database_client.find_device(entityname, devicename)
        if not deviceinfo:
            response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
            print('\r\nERROR Scan LDSBUS: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        # check if port number is valid
        if int(portnumber) < 0 or int(portnumber) > 3:
            response = json.dumps({'status': 'NG', 'message': 'Port number is not valid'})
            print('\r\nERROR Scan LDSBUS: Port number is not valid [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND


        # get username from token
        data = {}
        data['token'] = token
        data['devicename'] = devicename
        data['username'] = username
        data['PORT'] = portnumber
        api = 'get_ldsu_descs'
        response, status_return = self.messaging_requests.process(api, data)
        if status_return != 200:
            return response, status_return
        response = json.loads(response)


        if response.get("value") is None:
            # async handling for multiple chunks
            # do nothing
            time.sleep(1)
            pass
        else:
            # sync handling for single chunk

            # set status for non-present LDSUs
            ldsus = self.database_client.get_ldsus(entityname, devicename)
            for ldsu in ldsus:
                found = False
                for descriptor in response["value"]:
                    if ldsu["UID"] == descriptor["UID"]:
                        found = True
                        break
                if not found:
                    if portnumber == "0":
                        print("not found {}".format(ldsu["UID"]))
                        self.database_client.set_ldsu_status(entityname, devicename, ldsu["UID"], 0)
                    else:
                        if portnumber == ldsu["PORT"]:
                            # set unreachable if different port
                            print("not found {}".format(ldsu["UID"]))
                            self.database_client.set_ldsu_status(entityname, devicename, ldsu["UID"], 0)

            # process response
            for descriptor in response["value"]:
                # add or update ldsu
                ldsu = self.database_client.set_ldsu(entityname, devicename, descriptor)
                # add or update sensors
                obj = ldsu["descriptor"]["OBJ"]
                num = self.device_client.get_obj_numdevices(obj)
                for x in range(num):
                    descriptor = self.device_client.get_objidx(obj, x)
                    if descriptor:
                        source = ldsu["UID"]
                        sensorname = ldsu["LABL"] + " " + descriptor["SAID"]
                        number = self.device_client.get_objidx_said(descriptor)
                        sensor = {
                            'port'     : ldsu["PORT"],
                            'name'     : ldsu["LABL"],
                            'class'    : self.device_client.get_objidx_class(descriptor),
                            #'address'  : self.device_client.get_objidx_address(descriptor),
                            'address'  : int(self.device_client.get_objidx_said(descriptor)), # use said to fix sensor data compatibility
                            'format'   : self.device_client.get_objidx_format(descriptor),
                            'type'     : self.device_client.get_objidx_type(descriptor),
                            'unit'     : self.device_client.get_objidx_unit(descriptor),
                            'accuracy' : self.device_client.get_objidx_accuracy(descriptor),
                            'minmax'   : self.device_client.get_objidx_minmax(descriptor),
                            'obj'      : obj,
                        }
                        opmodes = self.device_client.get_objidx_modes(descriptor)
                        if opmodes:
                            sensor['opmodes'] = []
                            for opmode in opmodes:
                                sensor['opmodes'].append({
                                    'id'         : int(opmode['ID']),
                                    'name'       : opmode['Name'],
                                    'minmax'     : [opmode['Min'], opmode['Max']],
                                    'accuracy'   : opmode['Accuracy'],
                                    'description': opmode['Description']
                                })
                        self.database_client.add_sensor(entityname, devicename, source, number, sensorname, sensor)


        if portnumber == "0":
            ldsbus = []

            for x in range(3):
                # get ldsus and sensors in database
                ldsus = self.database_client.get_ldsus_by_port(entityname, devicename, str(x+1))
                sensors = self.database_client.get_sensors_by_port(entityname, devicename, str(x+1))

                # get the sensor reading for all enabled sensors
                for sensor in sensors:
                    if sensor["enabled"]:
                        reading = self.database_client.get_sensor_reading(entityname, devicename, sensor["source"], int(sensor["number"]))
                        if reading:
                            sensor["readings"] = reading

                ldsbus.append({
                    "ldsus": ldsus,
                    "sensors": sensors,
                    "actuators": []
                })

        elif portnumber == "1" or portnumber == "2" or portnumber == "3":
            # get ldsus and sensors in database
            ldsus = self.database_client.get_ldsus_by_port(entityname, devicename, portnumber)
            if len(ldsus):
                sensors = self.database_client.get_sensors_by_port(entityname, devicename, portnumber)

                # get the sensor reading for all enabled sensors
                for sensor in sensors:
                    if sensor["enabled"]:
                        reading = self.database_client.get_sensor_reading(entityname, devicename, sensor["source"], int(sensor["number"]))
                        if reading:
                            sensor["readings"] = reading
            else:
                sensors = []

            ldsbus = [
                {
                    "ldsus": ldsus,
                    "sensors": sensors,
                    "actuators": [],
                }
            ]


        msg = {'status': 'OK', 'message': 'LDSBUS triggered scanning successfully.'}
        if ldsbus:
            msg['ldsbus'] = ldsbus
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        return response


    ########################################################################################################
    # 
    # GET LDSU
    #
    # - Request:
    #   GET /devices/device/DEVICENAME/ldsu/LDSUUUID
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'ldsu': obj }
    #   {'status': 'NG', 'message': string}
    #
    # DELETE LDSU
    #
    # - Request:
    #   DELETE /devices/device/DEVICENAME/ldsu/LDSUUUID
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_ldsu(self, devicename, ldsuuuid):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get LDSU: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get LDSU: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        #print('change_ldsu_name {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get LDSU: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get LDSU: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get LDSU: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # check if device is registered
        deviceinfo = self.database_client.find_device(entityname, devicename)
        if not deviceinfo:
            response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
            print('\r\nERROR Get LDSU: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        # check if ldsu is registered
        ldsu = self.database_client.get_ldsu(entityname, devicename, ldsuuuid)
        if not ldsu:
            response = json.dumps({'status': 'NG', 'message': 'LDSU is not registered'})
            print('\r\nERROR Get LDSU: LDSU is not registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND


        if flask.request.method == 'GET':
            if orgname is not None:
                # check authorization
                if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                    response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                    print('\r\nERROR Get LDSU: Authorization not allowed [{}]\r\n'.format(username))
                    return response, status.HTTP_401_UNAUTHORIZED

            ldsu = self.database_client.get_ldsu(entityname, devicename, ldsuuuid)
            msg = {'status': 'OK', 'message': 'LDSU retrieved successfully.', 'ldsu': ldsu}

        elif flask.request.method == 'DELETE':
            if orgname is not None:
                # check authorization
                if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.DELETE) == False:
                    response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                    print('\r\nERROR Delete LDSU: Authorization not allowed [{}]\r\n'.format(username))
                    return response, status.HTTP_401_UNAUTHORIZED

            # cleanup sensors of the LDSUs in the specified port
            device_client = device(self.database_client, self.messaging_requests, self.messaging_client, self.device_client)
            sensors = self.database_client.get_all_device_sensors_by_source_by_deviceid(deviceinfo["deviceid"], ldsuuuid)
            if sensors is not None:
                for sensor in sensors:
                    if sensor.get("source") and sensor.get("number") and sensor.get("sensorname"):
                        device_client.sensor_cleanup(None, None, deviceinfo["deviceid"], sensor["source"], sensor["number"], sensor["sensorname"], sensor)

            # cleanup LDSU
            self.database_client.delete_ldsu_by_deviceid(deviceinfo["deviceid"], ldsuuuid)
            msg = {'status': 'OK', 'message': 'LDSU deleted successfully.'}


        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        return response


    ########################################################################################################
    # 
    # CHANGE LDSU NAME
    #
    # - Request:
    #   GET /devices/device/DEVICENAME/ldsu/LDSUUUID/name
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   data: {'name': string}
    #   // PORT_NUMBER can be 1, 2, 3, or 0 (0 if all lds bus)
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'ldsbus': obj }
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def change_ldsu_name(self, devicename, ldsuuuid):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Change LDSU name: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Change LDSU name: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        #print('change_ldsu_name {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Change LDSU name: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Change LDSU name: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Change LDSU name: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Change LDSU name: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # check if device is registered
        deviceinfo = self.database_client.find_device(entityname, devicename)
        if not deviceinfo:
            response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
            print('\r\nERROR Change LDSU name: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        # check if ldsu is registered
        ldsu = self.database_client.get_ldsu(entityname, devicename, ldsuuuid)
        if not ldsu:
            response = json.dumps({'status': 'NG', 'message': 'LDSU is not registered'})
            print('\r\nERROR Change LDSU name: LDSU is not registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND


        data = flask.request.get_json()
        if data is None or data.get("name") is None:
            response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
            print('\r\nERROR Change LDSU name: Parameters not included [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_400_BAD_REQUEST

        self.database_client.change_ldsu_name(entityname, devicename, ldsuuuid, data["name"])


        msg = {'status': 'OK', 'message': 'LDSU name changed successfully.'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        return response


    ########################################################################################################
    # 
    # IDENTIFY LDSU
    #
    # - Request:
    #   GET /devices/device/DEVICENAME/ldsu/LDSUUUID/identify
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   data: {'name': string}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'ldsbus': obj }
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def identify_ldsu(self, devicename, ldsuuuid):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Identify LDSU: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Identify LDSU: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        #print('identify_ldsu {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Identify LDSU: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Identify LDSU: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Identify LDSU: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Identify LDSU: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # check if device is registered
        deviceinfo = self.database_client.find_device(entityname, devicename)
        if not deviceinfo:
            response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
            print('\r\nERROR Identify LDSU: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        # check if ldsu is registered
        ldsu = self.database_client.get_ldsu(entityname, devicename, ldsuuuid)
        if not ldsu:
            response = json.dumps({'status': 'NG', 'message': 'LDSU is not registered'})
            print('\r\nERROR Identify LDSU: LDSU is not registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND


        # get username from token
        data = {}
        data['token'] = token
        data['devicename'] = devicename
        data['username'] = username
        data['UID'] = ldsuuuid
        api = 'identify_ldsu'
        response, status_return = self.messaging_requests.process(api, data)
        if status_return != 200:
            return response, status_return


        msg = {'status': 'OK', 'message': 'LDSU identified successfully.'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        return response