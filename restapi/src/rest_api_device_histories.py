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



class device_histories:

    def __init__(self, database_client):
        self.database_client = database_client

    def sort_by_timestamp(self, elem):
        return elem['timestamp']

    def get_menos_usage(self, entityname, devicename, deviceid):
        usage = {}
        usage["devicename"] = devicename
        if deviceid is None:
            usage["Mobile"]       = self.database_client.get_menos_num_sms_by_currmonth(entityname, devicename)
            usage["Email"]        = self.database_client.get_menos_num_email_by_currmonth(entityname, devicename)
            usage["Notification"] = self.database_client.get_menos_num_notification_by_currmonth(entityname, devicename)
            usage["Modem"]        = self.database_client.get_menos_num_device_by_currmonth(entityname, devicename)
            usage["Storage"]      = self.database_client.get_menos_num_storage_by_currmonth(entityname, devicename)
        else:
            usage["Mobile"]       = self.database_client.get_menos_num_sms_by_deviceid_by_currmonth(deviceid)
            usage["Email"]        = self.database_client.get_menos_num_email_by_deviceid_by_currmonth(deviceid)
            usage["Notification"] = self.database_client.get_menos_num_notification_by_deviceid_by_currmonth(deviceid)
            usage["Modem"]        = self.database_client.get_menos_num_device_by_deviceid_by_currmonth(deviceid)
            usage["Storage"]      = self.database_client.get_menos_num_storage_by_deviceid_by_currmonth(deviceid)
        return usage


    ########################################################################################################
    #
    # GET HISTORIES
    #
    # - Request:
    #   GET /devices/histories
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   { 'status': 'OK', 'message': string, 
    #     'transactions': array[
    #       {'devicename': string, 'deviceid': string, 'direction': string, 'topic': string, 'payload': string, 'timestamp': string}, ...]}
    #   { 'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_device_histories(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get Histories: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Histories: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_device_histories {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get Histories: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Histories: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get Histories: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get Histories: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        histories = self.database_client.get_user_history(entityname)
        #print(histories)


        msg = {'status': 'OK', 'message': 'User histories queried successfully.', 'transactions': histories}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        return response


    ########################################################################################################
    #
    # GET HISTORIES FILTERED
    #
    # - Request:
    #   POST /devices/histories
    #   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
    #   data: { 'devicename': string, 'deviceid': string, 'direction': string, 'topic': string, 'datebegin': int, 'dateend': int }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string, 
    #     'transactions': array[
    #       {'devicename': string, 'deviceid': string, 'direction': string, 'topic': string, 'payload': string, 'timestamp': string}, ...]}
    #   { 'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_device_histories_filtered(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get Histories: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Histories: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_device_histories_filtered {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get Histories: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Histories: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get Histories: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get Histories: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # get filter data
        devicename = None
        direction = None
        topic = None
        datebegin = 0
        dateend = 0
        data = flask.request.get_json()
        if data.get("devicename"):
            devicename = data["devicename"]
        if data.get("direction"):
            direction = data["direction"]
        if data.get("topic"):
            topic = data["topic"]
        if data.get("datebegin"):
            datebegin = data["datebegin"]
            if data.get("dateend"):
                dateend = data["dateend"]

        histories = self.database_client.get_user_history_filtered(entityname, devicename, direction, topic, datebegin, dateend)
        #print(histories)


        msg = {'status': 'OK', 'message': 'User histories queried successfully.', 'transactions': histories}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        return response


    ########################################################################################################
    #
    # GET MENOS HISTORIES
    #
    # - Request:
    #   GET /devices/menos
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   { 'status': 'OK', 'message': string, 
    #     'transactions': array[
    #       {'devicename': string, 'deviceid': string, 'direction': string, 'topic': string, 'payload': string, 'timestamp': string}, ...]}
    #   { 'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_device_menos_histories(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get MENOS Histories: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get MENOS Histories: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_device_menos_histories {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get MENOS Histories: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get MENOS Histories: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get MENOS Histories: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get MENOS Histories: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # get menos histories of all devices of user
        histories = []
        devices = self.database_client.get_devices(entityname)
        for device in devices:
            transactions = self.database_client.get_menos_transaction(device["deviceid"])
            for transaction in transactions:
                transaction["devicename"] = device["devicename"]
            histories += transactions
        histories.sort(key=self.sort_by_timestamp, reverse=True)


        # get menos usage summary per device
        usages = []
        for device in devices:
            usage = self.get_menos_usage(entityname, device["devicename"], device["deviceid"])
            usages.append(usage)


        msg = {'status': 'OK', 'message': 'User MENOS histories queried successfully.', 'transactions': histories}
        if usages:
            msg['usages'] = usages
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        return response


    ########################################################################################################
    #
    # GET MENOS HISTORIES FILTERED
    #
    # - Request:
    #   POST /devices/menos
    #   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
    #   data: { 'devicename': string, 'deviceid': string, 'type': string, 'source': string, 'datebegin': int, 'dateend': int }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string, 
    #     'transactions': array[
    #       {'devicename': string, 'deviceid': string, 'direction': string, 'topic': string, 'payload': string, 'timestamp': string}, ...]}
    #   { 'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_device_menos_histories_filtered(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get MENOS Histories: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get MENOS Histories: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_device_menos_histories_filtered {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get MENOS Histories: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get MENOS Histories: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get MENOS Histories: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get MENOS Histories: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # get filter data
        devicename = None
        type = None
        source = None
        datebegin = 0
        dateend = 0
        data = flask.request.get_json()
        #print(data)
        if data.get("devicename"):
            devicename = data["devicename"]
        if data.get("type"):
            type = data["type"]
        if data.get("source"):
            source = data["source"]
        if data.get("datebegin"):
            datebegin = data["datebegin"]
            if data.get("dateend"):
                dateend = data["dateend"]

        # get menos histories of all devices of user
        histories = []
        devices = self.database_client.get_devices(entityname)
        if devicename is not None:
            for device in devices:
                if device["devicename"] == devicename:
                    transactions = self.database_client.get_menos_transaction_filtered(device["deviceid"], type, source, datebegin, dateend)
                    for transaction in transactions:
                        transaction["devicename"] = device["devicename"]
                    histories += transactions
                    break
        else:
            for device in devices:
                transactions = self.database_client.get_menos_transaction_filtered(device["deviceid"], type, source, datebegin, dateend)
                for transaction in transactions:
                    transaction["devicename"] = device["devicename"]
                histories += transactions
        histories.sort(key=self.sort_by_timestamp, reverse=True)


        # get menos usage summary per device
        usages = []
        if devicename is not None:
            usage = self.get_menos_usage(entityname, devicename, None)
            usages.append(usage)
        else:
            for device in devices:
                usage = self.get_menos_usage(entityname, device["devicename"], device["deviceid"])
                usages.append(usage)


        msg = {'status': 'OK', 'message': 'User MENOS histories queried successfully.', 'transactions': histories}
        if usages:
            msg['usages'] = usages
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        return response
