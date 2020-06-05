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
#from jose import jwk, jwt
#import http.client
#from s3_client import s3_client
#import threading
#import copy
#from redis_client import redis_client
#import statistics
import rest_api_utils
from database import database_categorylabel, database_crudindex



class device_hierarchies:

    def __init__(self, database_client, messaging_requests):
        self.database_client = database_client
        self.messaging_requests = messaging_requests


    def get_default_device_hierarchy(self, devicename):

        hierarchy = {
            "name": devicename,
            "children": [

                {
                    "name": "UART",
                    "children": [
                    {
                        "name": "UART 1"
                    },
                    ]
                },

                {
                    "name": "GPIO",
                    "children": [
                    {
                        "name": "GPIO 1"
                    },
                    {
                        "name": "GPIO 2"
                    },
                    {
                        "name": "GPIO 3"
                    },
                    {
                        "name": "GPIO 4"
                    },
                    ]
                },

                {
                    "name": "I2C",
                    "children": [
                    {
                        "name": "I2C 1"
                    },
                    {
                        "name": "I2C 2"
                    },
                    {
                        "name": "I2C 3"
                    },
                    {
                        "name": "I2C 4"
                    },
                    ]
                },

                {
                    "name": "ADC",
                    "children": [
                    {
                        "name": "ADC 1"
                    },
                    {
                        "name": "ADC 2"
                    },
                    ]
                },

                {
                    "name": "1WIRE",
                    "children": [
                    {
                        "name": "1WIRE 1"
                    },
                    ]
                },

                {
                    "name": "TPROBE",
                    "children": [
                    {
                        "name": "TPROBE 1"
                    },
                    ]
                },

            ]
        }

        return hierarchy


    def get_default_device_hierarchy_ex(self, devicename):

        hierarchy = {
            "name": devicename,
            "children": [
                {
                    "name": "UART",
                },
                {
                    "name": "LDS BUS 1",
                },
                {
                    "name": "LDS BUS 2",
                },
                {
                    "name": "LDS BUS 3",
                }
            ]
        }

        return hierarchy


    def get_running_sensors(self, token, username, devicename, device):

        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username

        # query device
        api = "get_devs"
        data = {}
        data['token'] = token
        data['devicename'] = devicename
        data['username'] = username
        response, status_return = self.messaging_requests.process(api, data)
        if status_return == 200:
            device['status'] = 1
            # query database
            sensors = self.database_client.get_all_device_sensors(entityname, devicename)

            # map queried result with database result
            #print("from device")
            response = json.loads(response)
            #print(response["value"])

            for sensor in sensors:
                #print(sensor)
                found = False
                peripheral = "{}{}".format(sensor['source'], sensor['number'])

                if sensor["source"] == "i2c":
                    if response["value"].get(peripheral):
                        for item in response["value"][peripheral]:
                            # match found for database result and actual device result
                            # set database record to configured and actual device item["enabled"]
                            if sensor["address"] == item["address"]:
                                self.database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], item["enabled"], 1)
                                found = True
                                break
                else:
                    if response["value"].get(peripheral):
                        for item in response["value"][peripheral]:
                            if item["class"] == rest_api_utils.utils().get_i2c_device_class(sensor["class"]):
                                self.database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], item["enabled"], 1)
                                found = True
                                break

                # no match found
                # set database record to unconfigured and disabled
                if found == False:
                    self.database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], 0, 0)
            #print()
        else:
            device['status'] = 0
            # cannot communicate with device so set database record to unconfigured and disabled
            self.database_client.disable_unconfigure_sensors(entityname, devicename)
            #print('\r\nERROR Get All Device Sensors Dataset: Device is offline\r\n')
            return response, status_return
        return response, 200


    def generate_device_hierarchy(self, username, devicename, hierarchy, checkdevice=0, status=None, token=None):

        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username

        if checkdevice == 1:
            if status is not None:
                hierarchy["active"] = status
                if status == 1:
                    device = {}
                    self.get_running_sensors(token, username, devicename, device)
                    hierarchy["active"] = device["status"]
            else:
                device = {}
                self.get_running_sensors(token, username, devicename, device)
                hierarchy["active"] = device["status"]

        sensors = self.database_client.get_all_device_sensors(entityname, devicename)
        for sensor in sensors:
            #print("{} {} {}".format(sensor["sensorname"], sensor["source"], sensor["number"]))
            peripheral = sensor["source"].upper()
            for child in hierarchy["children"]:
                if child["name"] == peripheral:
                    peripheral += " {}".format(sensor["number"])
                    for granchild in child["children"]:
                        if granchild["name"] == peripheral:
                            if granchild.get("children") is None:
                                granchild["children"] = []
                            item = {
                                "name": sensor["sensorname"],
                                "children": [
                                {
                                    "name": sensor["class"]
                                }
                                ]
                            }
                            if sensor.get("subclass"):
                                item["children"].append({"name": sensor["subclass"]})

                            if checkdevice == 1:
                                if hierarchy["active"] == 0:
                                    item["active"] = 0
                                    for x in item["children"]:
                                        x["active"] = 0
                                else:
                                    item["active"] = sensor["enabled"]
                                    for x in item["children"]:
                                        x["active"] = sensor["enabled"]

                            granchild["children"].append(item)
                            break
                    break

        return hierarchy


    def generate_device_hierarchy_ex(self, username, devicename, hierarchy, checkdevice=0, status=None, token=None):

        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username

        if checkdevice == 1:
            if status is not None:
                hierarchy["active"] = status
                #if status == 1:
                #    device = {}
                #    self.get_running_sensors(token, username, devicename, device)
                #    hierarchy["active"] = device["status"]
            #else:
                #device = {}
                #self.get_running_sensors(token, username, devicename, device)
                #hierarchy["active"] = device["status"]

        sensors = self.database_client.get_all_device_sensors(entityname, devicename)
        for child in hierarchy["children"]:
            #print("{} {} {}".format(sensor["sensorname"], sensor["source"], sensor["number"]))
            for sensor in sensors:
                if sensor["port"] == child["name"][-1:]:
                    #print("{} {}".format(child["name"], sensor["sensorname"]))
                    if child.get("children") is None:
                        child["children"] = []
                        grandgrandchild = {
                            "name": sensor["sensorname"] + " - " + sensor["class"],
                            "active": sensor["enabled"]
                        }
                        grandchild = {
                            "name": sensor["name"],
                            "children": [grandgrandchild]
                        }
                        child["children"].append(grandchild)
                    else:
                        found = False
                        for granchild in child["children"]:
                            if granchild["name"] == sensor["name"]:
                                grandgrandchild = {
                                    "name": sensor["sensorname"] + " - " + sensor["class"],
                                    "active": sensor["enabled"]
                                }
                                granchild["children"].append(grandgrandchild)
                                found = True
                                break
                        if not found:
                            grandgrandchild = {
                                "name": sensor["sensorname"] + " - " + sensor["class"],
                                "active": sensor["enabled"]
                            }
                            grandchild = {
                                "name": sensor["name"],
                                "children": [grandgrandchild]
                            }
                            child["children"].append(grandchild)

        return hierarchy


    ########################################################################################################
    #
    # GET DEVICE HIERARCHY TREE
    #
    # - Request:
    #   GET /devices/device/<devicename>/hierarchy
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'hierarchy': {"name": string, "children": [{"name": "children", ...}, ...]} }
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_device_hierarchy(self, devicename):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get hierarchy tree: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get hierarchy tree: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED

        print('get_device_hierarchy {} devicename={}'.format(username, devicename))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0 or len(devicename) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get hierarchy tree: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get hierarchy tree: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get hierarchy tree: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get hierarchy tree: Authorization not allowed [{}]\r\n'.format(username))
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
            print('\r\nERROR Get hierarchy tree: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND


        # generate hierarchy
        hierarchy = self.get_default_device_hierarchy_ex(devicename)
        hierarchy = self.generate_device_hierarchy_ex(username, devicename, hierarchy)


        msg = {'status': 'OK', 'message': 'Get hierarchy tree successful.', 'hierarchy': hierarchy}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nGet hierarchy tree successful: {}\r\n\r\n'.format(username))
        return response


    ########################################################################################################
    #
    # GET DEVICE HIERARCHY TREE (WITH STATUS)
    #
    # - Request:
    #   POST /devices/device/<devicename>/hierarchy
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   data: {'checkdevice': int, 'status': int}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'hierarchy': {"name": string, "children": [{"name": "children", ...}, ...]} }
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_device_hierarchy_with_status(self, devicename):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get hierarchy tree: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get hierarchy tree: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED

        print('get_device_hierarchy_with_status {} devicename={}'.format(username, devicename))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0 or len(devicename) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get hierarchy tree: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get hierarchy tree: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get hierarchy tree: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get hierarchy tree: Authorization not allowed [{}]\r\n'.format(username))
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
            print('\r\nERROR Get hierarchy tree: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND


        # generate hierarchy
        checkdevice = 0
        status = None
        data = flask.request.get_json()
        if data is not None:
            if data.get("checkdevice") is not None:
                checkdevice = data["checkdevice"]
            if data.get("status") is not None:
                status = data["status"]
        hierarchy = self.get_default_device_hierarchy_ex(devicename)
        hierarchy = self.generate_device_hierarchy_ex(username, devicename, hierarchy, checkdevice, status, token)


        msg = {'status': 'OK', 'message': 'Get hierarchy tree successful.', 'hierarchy': hierarchy}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nGet hierarchy tree successful: {}\r\n\r\n'.format(username))
        return response
