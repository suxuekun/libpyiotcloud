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



class device_groups:

    def __init__(self, database_client):
        self.database_client = database_client

    def sort_by_devicename(self, elem):
        return elem['devicename']


    ########################################################################################################
    # 
    # GET DEVICE GROUPS
    #
    # - Request:
    #   GET /devicegroups
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'devicegroups': array[{'groupname': string, 'devices': [{'devicename': string}], ...}]}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_device_group_list(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get Device Groups: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Device Groups: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        #print('get_device_list {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get Device Groups: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Device Groups: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get Device Groups: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get Device Groups: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        devicegroups = self.database_client.get_devicegroups(entityname)

        # update the devicenames to be deviceids
        if devicegroups:
            for devicegroup in devicegroups:
                devicenames = []
                for deviceid in devicegroup['devices']:
                    device = self.database_client.find_device_by_id(deviceid)
                    if device:
                        device.pop("username")
                        devicenames.append(device)
                devicegroup['devices'] = devicenames


        msg = {'status': 'OK', 'message': 'Device groups queried successfully.', 'devicegroups': devicegroups}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('get_device_list {} {} devices'.format(username, len(devicegroups)))
        return response


    ########################################################################################################
    #
    #
    # GET DEVICE GROUP
    #
    # - Request:
    #   GET /devicegroups/group/<devicegroupname>
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'devicegroup': {'groupname': string, 'devices': [{'devicename': string}], ...}}
    #   {'status': 'NG', 'message': string}
    #
    #
    # ADD DEVICE GROUP
    #
    # - Request:
    #   POST /devicegroups/group/<devicegroupname>
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    #
    # DELETE DEVICE GROUP
    #
    # - Request:
    #   DELETE /devicegroups/group/<devicegroupname>
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def register_devicegroups(self, devicegroupname):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get/Add/Delete DeviceGroup: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get/Add/Delete DeviceGroup: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('register_devicegroups {} devicegroupname={}'.format(username, devicegroupname))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0 or len(devicegroupname) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get/Add/Delete DeviceGroup: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get/Add/Delete DeviceGroup: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get/Add/Delete DeviceGroup: Token is invalid [{}]\r\n'.format(username))
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
                    print('\r\nERROR Get DeviceGroup: Authorization not allowed [{}]\r\n'.format(username))
                    return response, status.HTTP_401_UNAUTHORIZED

            msg = {'status': 'OK', 'message': 'Device group retrieved successfully.'}

            # get device group if exist
            msg['devicegroup'] = self.database_client.get_devicegroup(entityname, devicegroupname)
            if msg['devicegroup'] is None:
                response = json.dumps({'status': 'NG', 'message': 'Device group not found'})
                print('\r\nERROR Get DeviceGroup: Device group not found [{},{}]\r\n'.format(entityname, devicegroupname))
                return response, status.HTTP_404_NOT_FOUND

            # update the devicenames to be deviceids
            devicenames = []
            for deviceid in msg['devicegroup']['devices']:
                device = self.database_client.find_device_by_id(deviceid)
                if device:
                    device.pop("username")
                    devicenames.append(device)
            msg['devicegroup']['devices'] = devicenames

        elif flask.request.method == 'POST':
            if orgname is not None:
                # check authorization
                if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.CREATE) == False:
                    response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                    print('\r\nERROR Add DeviceGroup: Authorization not allowed [{}]\r\n'.format(username))
                    return response, status.HTTP_401_UNAUTHORIZED

            # check devicegroupname
            if len(devicegroupname) == 0:
                response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
                print('\r\nERROR Add DeviceGroup: Empty parameter found\r\n')
                return response, status.HTTP_400_BAD_REQUEST

            # check device group if exist
            if self.database_client.get_devicegroup(entityname, devicegroupname) is not None:
                response = json.dumps({'status': 'NG', 'message': 'Device group name is already used'})
                print('\r\nERROR Add DeviceGroup: Name is already used [{},{}]\r\n'.format(entityname, devicegroupname))
                return response, status.HTTP_409_CONFLICT

            # add device list if provided 
            deviceids = []
            data = flask.request.get_json()
            if data is not None and data.get("devices") is not None:
                # check if devices are valid
                devices = self.database_client.get_devices(entityname)
                for device in data["devices"]:
                    found = False
                    for devicex in devices:
                        if device == devicex["devicename"]:
                            found = True
                            break
                    if not found:
                        response = json.dumps({'status': 'NG', 'message': 'One of the devices specified is not registered'})
                        print('\r\nERROR Add DeviceGroup: One of the devices specified is not registered\r\n')
                        return response, status.HTTP_400_BAD_REQUEST

                # check if the devices dont belong to a group already
                if len(data["devices"]):
                    ungrouped_devices = self.database_client.get_ungroupeddevices(entityname)
                    for devicename in data["devices"]:
                        found = False
                        for ungrouped_device in ungrouped_devices:
                            if devicename == ungrouped_device["devicename"]:
                                found = True
                                break
                        if found == False:
                            response = json.dumps({'status': 'NG', 'message': 'Atleast one of the devices already belong to a group'})
                            print('\r\nERROR Add DeviceGroup: Atleast one of the devices already belong to a group\r\n')
                            return response, status.HTTP_400_BAD_REQUEST

                        # get the deviceids given the devicenames
                        device = self.database_client.find_device(entityname, devicename)
                        if device:
                            deviceids.append(device["deviceid"])

            # create device group
            self.database_client.add_devicegroup(entityname, devicegroupname, deviceids)
            msg = {'status': 'OK', 'message': 'Device group added successfully.'}

        elif flask.request.method == 'DELETE':
            if orgname is not None:
                # check authorization
                if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.DELETE) == False:
                    response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                    print('\r\nERROR Delete DeviceGroup: Authorization not allowed [{}]\r\n'.format(username))
                    return response, status.HTTP_401_UNAUTHORIZED

            # check device group if exist
            if self.database_client.get_devicegroup(entityname, devicegroupname) is None:
                response = json.dumps({'status': 'NG', 'message': 'Device group not found'})
                print('\r\nERROR Delete DeviceGroup: Device group not found [{},{}]\r\n'.format(entityname, devicegroupname))
                return response, status.HTTP_404_NOT_FOUND

            # delete device group
            msg = {'status': 'OK', 'message': 'Device group deleted successfully.'}
            self.database_client.delete_devicegroup(entityname, devicegroupname)


        print('\r\n%s: {}\r\n{}\r\n'.format(username, msg["message"]))
        response = json.dumps(msg)
        return response


    ########################################################################################################
    #
    #
    # GET DEVICE GROUP DETAILED
    #
    # - Request:
    #   GET /devicegroups/group/<devicegroupname>/devices
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'devices': array[{'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': string, 'heartbeat': string, 'version': string}, ...]}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_devicegroup_detailed(self, devicegroupname):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get/Add/Delete DeviceGroup: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get/Add/Delete DeviceGroup: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_devicegroup_detailed {} devicegroupname={}'.format(username, devicegroupname))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0 or len(devicegroupname) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get/Add/Delete DeviceGroup: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get/Add/Delete DeviceGroup: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get/Add/Delete DeviceGroup: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get DeviceGroup: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED

        msg = {'status': 'OK', 'message': 'Device group retrieved successfully.'}

        # get device group if exist
        msg['devicegroup'] = self.database_client.get_devicegroup(entityname, devicegroupname)
        if msg['devicegroup'] is None:
            response = json.dumps({'status': 'NG', 'message': 'Device group not found'})
            print('\r\nERROR Get DeviceGroup: Device group not found [{},{}]\r\n'.format(entityname, devicegroupname))
            return response, status.HTTP_404_NOT_FOUND

        # update the devicenames to be deviceids
        devices = self.database_client.get_devices(entityname)
        device_list = []
        for deviceid in msg['devicegroup']['devices']:
            for device in devices:
                if deviceid == device["deviceid"]:
                    if device.get("username"):
                        device.pop("username")
                    device_list.append(device)
                    break
        msg['devicegroup']['devices'] = device_list


        print('\r\n%s: {}\r\n{}\r\n'.format(username, msg["message"]))
        response = json.dumps(msg)
        return response


    ########################################################################################################
    #
    #
    # GET UNGROUPED DEVICES
    #
    # - Request:
    #   GET /devicegroups/ungrouped
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'devices': array[{'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': string, 'heartbeat': string, 'version': string}, ...]}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_ungroupeddevices(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get Ungrouped Devices: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Ungrouped Devices: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_ungroupeddevices {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get Ungrouped Devices: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Ungrouped Devices: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get Ungrouped Devices: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Ungrouped Devices: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
        else:
            # no active organization, just a normal user
            entityname = username


        devices = self.database_client.get_ungroupeddevices(entityname)
        msg = {'status': 'OK', 'message': 'Ungrouped devices retrieved successfully.', 'devices': devices}


        print('\r\n {}\r\n{}\r\n'.format(username, msg["message"]))
        response = json.dumps(msg)
        return response


    ########################################################################################################
    #
    #
    # GET MIXED DEVICES
    #
    # - Request:
    #   GET /devicegroups/mixed
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'devices': array[{'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': string, 'heartbeat': string, 'version': string}, ...]}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_mixeddevices(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get Mixed Devices: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Mixed Devices: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_mixeddevices {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get Mixed Devices: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Mixed Devices: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get Mixed Devices: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Mixed Devices: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
        else:
            # no active organization, just a normal user
            entityname = username


        # get ungrouped devices
        devices = self.database_client.get_ungroupeddevices(entityname)

        # get device groups
        devicegroups = self.database_client.get_devicegroups(entityname)
        if devicegroups:
            for devicegroup in devicegroups:
                devicenames = []
                for deviceid in devicegroup['devices']:
                    device = self.database_client.find_device_by_id(deviceid)
                    if device:
                        device.pop("username")
                        devicenames.append(device)
                devicegroup['devices'] = devicenames

        msg = {'status': 'OK', 'message': 'Mixed devices retrieved successfully.', 'data': {'devices': devices, 'devicegroups': devicegroups} }



        print('\r\n {}\r\n{}\r\n'.format(username, msg["message"]))
        response = json.dumps(msg)
        return response


    ########################################################################################################
    #
    # UPDATE DEVICE GROUP NAME
    #
    # - Request:
    #   POST /devicegroups/<devicegroupname>/name
    #   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
    #   data: {'new_groupname': string}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def update_devicegroupname(self, devicegroupname):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Update Device Group Name: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Update Device Group Name: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('update_devicegroupname {} devicegroupname={}'.format(username, devicegroupname))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0 or len(devicegroupname) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Update Device Group Name: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Update Device Group Name: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Update Device Group Name: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Update Device Group Name: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username

        # check devicegroupname
        if len(devicegroupname) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Update Device Group Name: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if device group is registered
        if self.database_client.get_devicegroup(entityname, devicegroupname) is None:
            response = json.dumps({'status': 'NG', 'message': 'Device group is not registered'})
            print('\r\nERROR Update Device Group Name: Device group is not registered [{},{}]\r\n'.format(entityname, devicegroupname))
            return response, status.HTTP_404_NOT_FOUND


        # check if new device group name is already registered
        data = flask.request.get_json()
        if not data.get("new_groupname"):
            response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
            print('\r\nERROR Update Device Group Name: Parameters not included [{},{}]\r\n'.format(entityname, devicegroupname))
            return response, status.HTTP_400_BAD_REQUEST
        if len(data["new_groupname"]) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Update Device Group Name: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST
        if self.database_client.get_devicegroup(entityname, data["new_groupname"]) is not None:
            response = json.dumps({'status': 'NG', 'message': 'Device group name is already registered'})
            print('\r\nERROR Update Device Group Name: Device group name is already registered [{},{}]\r\n'.format(entityname, devicegroupname))
            return response, status.HTTP_409_CONFLICT


        # update the device group name
        self.database_client.update_name_devicegroup(entityname, devicegroupname, data["new_groupname"])


        msg = {'status': 'OK', 'message': 'Device Group name updated successfully.'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nDevice Group name updated successful: {}\r\n{}\r\n'.format(username, response))
        return response


    ########################################################################################################
    #
    #
    # ADD DEVICE TO DEVICE GROUP
    #
    # - Request:
    #   POST /devicegroups/<devicegroupname>/device/<devicename>
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   data: {'destdevicegroupname': string}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    #
    # REMOVE DEVICE FROM DEVICE GROUP
    #
    # - Request:
    #   DELETE /devicegroups/<devicegroupname>/device/<devicename>
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def register_device_to_devicegroups(self, devicegroupname, devicename):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Add/Delete Device To/From DeviceGroup: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Add/Delete Device To/From DeviceGroup: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('register_device_to_devicegroups {} devicegroupname={}'.format(username, devicegroupname))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0 or len(devicegroupname) == 0 or len(devicename) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Add/Delete Device To/From DeviceGroup: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Add/Delete Device To/From DeviceGroup: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Add/Delete Device To/From DeviceGroup: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Add/Delete Device To/From DeviceGroup: Authorization not allowed [{}]\r\n'.format(username))
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
            print('\r\nERROR Add/Delete Device To/From DeviceGroup: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        # check if device group is registered
        if self.database_client.get_devicegroup(entityname, devicegroupname) is None:
            response = json.dumps({'status': 'NG', 'message': 'Device group is not registered'})
            print('\r\nERROR Add/Delete Device To/From DeviceGroup: Device group is not registered [{},{}]\r\n'.format(entityname, devicegroupname))
            return response, status.HTTP_404_NOT_FOUND

        if flask.request.method == 'POST':
            msg = {'status': 'OK', 'message': ''}

            # check if new device name is already registered
            destdevicegroupname = None
            data = flask.request.get_json()
            if data is not None:
                if data.get("destdevicegroupname") is not None:
                    destdevicegroupname = data["destdevicegroupname"]

            if destdevicegroupname is None:
                msg['message'] = 'Device added to device group successfully.'

                # check if the devices dont belong to a group already
                ungrouped_devices = self.database_client.get_ungroupeddevices(entityname)
                found = False
                for ungrouped_device in ungrouped_devices:
                    if devicename == ungrouped_device["devicename"]:
                        found = True
                        break
                if found == False:
                    response = json.dumps({'status': 'NG', 'message': 'The device already belong to a group'})
                    print('\r\nERROR Add DeviceGroup: The device already belong to a group\r\n')
                    return response, status.HTTP_400_BAD_REQUEST

                # add device to device group
                result = self.database_client.add_device_to_devicegroup(entityname, devicegroupname, device['deviceid'])
                if result == False:
                    response = json.dumps({'status': 'NG', 'message': 'Device already in device group'})
                    print('\r\nERROR Add/Delete Device To/From DeviceGroup: Device already in device group\r\n')
                    return response, status.HTTP_400_BAD_REQUEST

            else:
                msg['message'] = 'Device transferred to device group successfully.'

                # check if destination group is valid
                if self.database_client.get_devicegroup(entityname, destdevicegroupname) is None:
                    response = json.dumps({'status': 'NG', 'message': 'Device group is not registered'})
                    print('\r\nERROR Transfer Device To/From DeviceGroup: Device group is not registered [{},{}]\r\n'.format(entityname, destdevicegroupname))
                    return response, status.HTTP_404_NOT_FOUND

                # remove device from device group
                self.database_client.remove_device_from_devicegroup(entityname, devicegroupname, device['deviceid'])

                # add device to device group
                result = self.database_client.add_device_to_devicegroup(entityname, destdevicegroupname, device['deviceid'])
                if result == False:
                    response = json.dumps({'status': 'NG', 'message': 'Device already in device group'})
                    print('\r\nERROR Transfer Device To/From DeviceGroup: Device already in device group\r\n')
                    return response, status.HTTP_400_BAD_REQUEST

        elif flask.request.method == 'DELETE':
            msg = {'status': 'OK', 'message': 'Device removed from device group successfully.'}

            # remove device from device group
            result = self.database_client.remove_device_from_devicegroup(entityname, devicegroupname, device['deviceid'])
            if result == False:
                response = json.dumps({'status': 'NG', 'message': 'Device not part of device group'})
                print('\r\nERROR Remove Device From DeviceGroup: Device not part of device group\r\n')
                return response, status.HTTP_400_BAD_REQUEST


        print('\r\n%s: {}\r\n{}\r\n'.format(username, msg["message"]))
        response = json.dumps(msg)
        return response


    ########################################################################################################
    #
    #
    # SET DEVICES TO DEVICE GROUP
    #
    # - Request:
    #   POST /devicegroups/<devicegroupname>/devices
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   data: {'devices': ["devicename", ...]}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def set_devices_to_devicegroups(self, devicegroupname):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Add/Delete Device To/From DeviceGroup: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Add/Delete Device To/From DeviceGroup: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('set_devices_to_devicegroups {} devicegroupname={}'.format(username, devicegroupname))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0 or len(devicegroupname) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Add/Delete Device To/From DeviceGroup: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Add/Delete Device To/From DeviceGroup: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Add/Delete Device To/From DeviceGroup: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Add/Delete Device To/From DeviceGroup: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # check if new device group name is already registered
        data = flask.request.get_json()
        if data is None or data.get("devices") is None:
            response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
            print('\r\nERROR Add/Delete Device To/From DeviceGroup: Parameters not included [{},{}]\r\n'.format(username, devicegroupname))
            return response, status.HTTP_400_BAD_REQUEST


        # check if the devices dont belong to a group already
        if len(data["devices"]):
            devicegroup = self.database_client.get_devicegroup(entityname, devicegroupname)
            if devicegroup:
                devicenames = []
                for deviceid in devicegroup['devices']:
                    device = self.database_client.find_device_by_id(deviceid)
                    if device:
                        devicenames.append(device["devicename"])

            ungrouped_devices = self.database_client.get_ungroupeddevices(entityname)
            for devicename in data["devices"]:
                found = False
                for ungrouped_device in ungrouped_devices:
                    if devicename == ungrouped_device["devicename"]:
                        found = True
                        break
                if found == False:
                    if devicename not in devicenames:
                        response = json.dumps({'status': 'NG', 'message': 'Atleast one of the devices already belong to a group'})
                        print('\r\nERROR Add/Delete Device To/From DeviceGroup: Atleast one of the devices already belong to a group\r\n')
                        return response, status.HTTP_400_BAD_REQUEST

        # get the deviceids given the devicenames
        deviceids = []
        for devicename in data["devices"]:
            device = self.database_client.find_device(entityname, devicename)
            if device:
                deviceids.append(device["deviceid"])

        self.database_client.set_devices_to_devicegroup(entityname, devicegroupname, deviceids)
        msg = {'status': 'OK', 'message': 'Devices set to device group successfully.'}


        print('\r\n%s: {}\r\n{}\r\n'.format(username, msg["message"]))
        response = json.dumps(msg)
        return response


    ########################################################################################################
    #
    # GET DEVICE GROUP LOCATION 
    #
    # - Request:
    #   GET /devicegroups/group/DEVICEGROUPNAME/location
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'locations': [{'devicename': string, 'latitude': float, 'longitude': float}] }
    #   {'status': 'NG', 'message': string}
    #
    # SET DEVICE GROUP LOCATION 
    #
    # - Request:
    #   POST /devicegroups/group/DEVICEGROUPNAME/location
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   data: { 'locations': [{devicename: string, location: {'latitude': float, 'longitude': float}}, ...] }
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    # DELETE DEVICE GROUP LOCATION 
    #
    # - Request:
    #   DELETE /devicegroups/group/DEVICEGROUPNAME/location
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_devicegroup_locations(self, devicegroupname):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Set Devices Locations: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Set Devices Locations: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_devicegroup_locations {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Set Devices Locations: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Set Devices Locations: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Set Devices Locations: Token is invalid [{}]\r\n'.format(username))
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
                    print('\r\nERROR Get DeviceGroup Locations: Authorization not allowed [{}]\r\n'.format(username))
                    return response, status.HTTP_401_UNAUTHORIZED

            # get device group if exist
            devicegroup = self.database_client.get_devicegroup(entityname, devicegroupname)
            if devicegroup is None:
                response = json.dumps({'status': 'NG', 'message': 'Device group not found'})
                print('\r\nERROR Get DeviceGroup Locations: Device group not found [{},{}]\r\n'.format(entityname, devicegroupname))
                return response, status.HTTP_404_NOT_FOUND

            # delete location of each device in the device group
            locations = []
            for deviceid in devicegroup["devices"]:
                device = self.database_client.find_device_by_id(deviceid)
                if device:
                    location = self.database_client.get_device_location(entityname, device["devicename"])
                    if location:
                        locations.append({"devicename": device["devicename"], "location": location})


            msg = {'status': 'OK', 'message': 'DeviceGroup locations retrieved successfully.'}
            if locations:
                msg['locations'] = locations
            if new_token:
                msg['new_token'] = new_token
            response = json.dumps(msg)
            print('\r\nDeviceGroup locations retrieved successful: {}\r\n'.format(username))
            return response

        elif flask.request.method == 'POST':
            if orgname is not None:
                # check authorization
                if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
                    response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                    print('\r\nERROR Set DeviceGroup Locations: Authorization not allowed [{}]\r\n'.format(username))
                    return response, status.HTTP_401_UNAUTHORIZED

            # check if new device name is already registered
            data = flask.request.get_json()
            if data.get("locations") is None:
                response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
                print('\r\nERROR Set DeviceGroup Locations: Parameters not included [{},{}]\r\n'.format(username, devicename))
                return response, status.HTTP_400_BAD_REQUEST

            # get devices of the user
            #devices = self.database_client.get_devices(entityname)

            # set the location to database
            for location in data["locations"]:
                self.database_client.add_device_location(entityname, location["devicename"], location["location"])


            msg = {'status': 'OK', 'message': 'Devices locations updated successfully.'}
            if new_token:
                msg['new_token'] = new_token
            response = json.dumps(msg)
            print('\r\nDeviceGroup locations updated successful: {}\r\n'.format(username))
            return response

        elif flask.request.method == 'DELETE':
            if orgname is not None:
                # check authorization
                if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.DELETE) == False:
                    response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                    print('\r\nERROR Delete DeviceGroup Locations: Authorization not allowed [{}]\r\n'.format(username))
                    return response, status.HTTP_401_UNAUTHORIZED


            # get device group if exist
            devicegroup = self.database_client.get_devicegroup(entityname, devicegroupname)
            if devicegroup is None:
                response = json.dumps({'status': 'NG', 'message': 'Device group not found'})
                print('\r\nERROR Delete DeviceGroup Locations: Device group not found [{},{}]\r\n'.format(entityname, devicegroupname))
                return response, status.HTTP_404_NOT_FOUND

            # delete location of each device in the device group
            for deviceid in devicegroup["devices"]:
                device = self.database_client.find_device_by_id(deviceid)
                if device:
                    self.database_client.delete_device_location(entityname, device["devicename"])


            msg = {'status': 'OK', 'message': 'DeviceGroup locations deleted successfully.'}
            if new_token:
                msg['new_token'] = new_token
            response = json.dumps(msg)
            print('\r\nDeviceGroup locations deleted successful: {}\r\n'.format(username))
            return response


    ########################################################################################################
    #
    # GET DEVICE GROUP OTA STATUSES
    #
    # - Request:
    #   GET /devicegroups/group/<devicegroupname>/ota
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string. 'ota': [{"devicename": string, "deviceid", string, "version": string, "status":string, "time": string, "timestamp": int}, ...]}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_devicegroup_ota_statuses(self, devicegroupname):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get OTA statuses: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get OTA statuses: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED

        print('get_devicegroup_ota_statuses {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get OTA statuses: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get OTA statuses: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get OTA statuses: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get OTA statuses: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # check database for ota status
        ota_statuses = self.database_client.get_ota_statuses(entityname)
        if ota_statuses is None:
            ota_statuses = []

        # get device group if exist
        devicegroup = self.database_client.get_devicegroup(entityname, devicegroupname)
        if devicegroup is None:
            response = json.dumps({'status': 'NG', 'message': 'Device group not found'})
            print('\r\nERROR Delete DeviceGroup Locations: Device group not found [{},{}]\r\n'.format(entityname, devicegroupname))
            return response, status.HTTP_404_NOT_FOUND

        if len(devicegroup["devices"]):
            devices = self.database_client.get_devices(entityname)
            for x in range(len(devices)-1,-1,-1):
                if devices[x]["deviceid"] not in devicegroup["devices"]:
                    del devices[x]
                    continue
            for x in range(len(ota_statuses)-1,-1,-1):
                if ota_statuses[x]["deviceid"] not in devicegroup["devices"]:
                    del ota_statuses[x]
                    continue

        for device in devices:
            found = False
            for ota_status in ota_statuses:
                if device["deviceid"] == ota_status["deviceid"]:
                    ota_status["devicename"] = device["devicename"]
                    if ota_status["status"] == "completed":
                        #print(ota_status)
                        if ota_status.get("timestamp") and ota_status.get("timestart"):
                            ota_status["time"] = "{} seconds".format(ota_status["timestamp"] - ota_status["timestart"])
                            ota_status.pop("timestart")
                            found = True
                            break
                    elif ota_status["status"] == "pending" or ota_status["status"] == "ongoing":
                        ota_status["time"] = "n/a"
                        ota_status["timestamp"] = "n/a"
                        if ota_status.get("timestart"):
                            ota_status.pop("timestart")
                        found = True
                        break
            if found == False:
                ota_status = {
                    "deviceid"   : device["deviceid"],
                    "devicename" : device["devicename"],
                    "status"     : "n/a",
                    "time"       : "n/a",
                    "timestamp"  : "n/a",
                }
                if device.get("version"):
                    ota_status["version"] = device["version"]
                else:
                    ota_status["version"] = "0.1"
                ota_statuses.append(ota_status)
        print(len(ota_statuses))
        print(ota_statuses)
        if len(ota_statuses):
            ota_statuses.sort(key=self.sort_by_devicename)


        msg = {'status': 'OK', 'message': 'Get OTA statuses successful.', 'ota': ota_statuses}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nGet OTA statuses successful: {}\r\n\r\n'.format(username))
        return response

