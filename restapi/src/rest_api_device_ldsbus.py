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



class device_ldsbus:

    def __init__(self, database_client, messaging_requests, device_client):
        self.database_client = database_client
        self.messaging_requests = messaging_requests
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
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get LDSBUS: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # get ldsus and sensors in database
        ldsus = self.database_client.get_ldsus_by_port(entityname, devicename, portnumber)
        sensors = self.database_client.get_sensors_by_port(entityname, devicename, portnumber)
        ldsbus = [
            {
                "ldsus": ldsus,
                "sensors": sensors,
                "actuators": [],
            }
        ]


        msg = {'status': 'OK', 'message': 'LDSBUS queried successfully.'}
        if ldsbus:
            msg['ldsbus'] = ldsbus
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
        print('get_lds_bus_sensors {}'.format(username))

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


        # get component in database
        msg = {'status': 'OK', 'message': 'LDSBUS component queried successfully.'}
        if component == "ldsus":
            ldsus = self.database_client.get_ldsus_by_port(entityname, devicename, portnumber)
            if ldsus:
                msg['ldsus'] = ldsus
        elif component == "sensors":
            sensors = self.database_client.get_sensors_by_port(entityname, devicename, portnumber)
            if sensors:
                msg['sensors'] = sensors
        elif component == "actuators":
            actuators = None # TODO
            if actuators:
                msg['actuators'] = actuators

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
            print('\r\nERROR Get LDSBUS: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get LDSBUS: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('scan_lds_bus {}'.format(username))

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
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get LDSBUS: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


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


        if True:
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

            # get ldsus and sensors in database
            ldsus = self.database_client.get_ldsus_by_port(entityname, devicename, portnumber)
            sensors = self.database_client.get_sensors_by_port(entityname, devicename, portnumber)
            ldsbus = [
                {
                    "ldsus": ldsus,
                    "sensors": sensors,
                    "actuators": [],
                }
            ]
        else:
            ldsbus = response["value"]
            ldsus = ldsbus[0]["ldsus"]
            for ldsu in ldsus:
                ldsu["LABL"] = ldsu["NAME"]
                print(ldsu)
            print(ldsbus)


        msg = {'status': 'OK', 'message': 'LDSBUS queried successfully.'}
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

            self.database_client.delete_device_notification_sensor(entityname, devicename, ldsuuuid)
            self.database_client.delete_device_peripheral_configuration_by_source(entityname, devicename, ldsuuuid)
            self.database_client.delete_device_sensors_by_source(entityname, devicename, ldsuuuid)
            self.database_client.delete_ldsu(entityname, devicename, ldsuuuid)
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