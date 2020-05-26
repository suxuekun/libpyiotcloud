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
                        devicenames.append(device["devicename"])
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
    #   GET /devicegroups/<devicegroupname>
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
    #   POST /devicegroups/<devicegroupname>
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
    #   DELETE /devicegroups/<devicegroupname>
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
                    devicenames.append(device["devicename"])
            msg['devicegroup']['devices'] = devicenames

        elif flask.request.method == 'POST':
            if orgname is not None:
                # check authorization
                if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.CREATE) == False:
                    response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                    print('\r\nERROR Add DeviceGroup: Authorization not allowed [{}]\r\n'.format(username))
                    return response, status.HTTP_401_UNAUTHORIZED

            # check device group if exist
            if self.database_client.get_devicegroup(entityname, devicegroupname) is not None:
                response = json.dumps({'status': 'NG', 'message': 'Device group name is already used'})
                print('\r\nERROR Add DeviceGroup: Name is already used [{},{}]\r\n'.format(entityname, devicegroupname))
                return response, status.HTTP_409_CONFLICT

            # add device list if provided 
            deviceids = []
            data = flask.request.get_json()
            if data is not None and data.get("devices") is not None:
                #print(data["devices"])
                for devicename in data["devices"]:
                    device = self.database_client.find_device(entityname, devicename)
                    if device:
                        deviceids.append(device["deviceid"])

            # create device group
            msg = {'status': 'OK', 'message': 'Device group added successfully.'}
            self.database_client.add_devicegroup(entityname, devicegroupname, deviceids)

            msg = {'status': 'OK', 'message': 'Devices set to device group successfully.'}

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
            return response, status.HTTP_400_BAD_REQUEST


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
            msg = {'status': 'OK', 'message': 'Device added to device group successfully.'}

            # add device to device group
            result = self.database_client.add_device_to_devicegroup(entityname, devicegroupname, device['deviceid'])
            if result == False:
                response = json.dumps({'status': 'NG', 'message': 'Device already in device group'})
                print('\r\nERROR Add/Delete Device To/From DeviceGroup: Device already in device group\r\n')
                return response, status.HTTP_400_BAD_REQUEST

        elif flask.request.method == 'DELETE':
            msg = {'status': 'OK', 'message': 'Device removed from device group successfully.'}

            # remove device from device group
            self.database_client.remove_device_from_devicegroup(entityname, devicegroupname, device['deviceid'])


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
