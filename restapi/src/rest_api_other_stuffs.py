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
from rest_api_config import config
#from database import database_client
#from flask_cors import CORS
from flask_api import status
#from jose import jwk, jwt
import jwt
#import http.client
#from s3_client import s3_client
#import threading
#import copy
#from redis_client import redis_client
#import statistics
import rest_api_utils



#CONFIG_SEPARATOR            = '/'
#CONFIG_PREPEND_REPLY_TOPIC  = "server"



class other_stuffs:

    def __init__(self, database_client, storage_client):
        self.database_client = database_client
        self.storage_client = storage_client


    ########################################################################################################
    #
    # SEND FEEDBACK
    #
    # - Request:
    #   POST /others/feedback
    #   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
    #   data: { 'feedback': string, 'rating': int, 'contactme': boolean, 'recipient': string }
    #   // recipient is temporary for testing purposes only
    #
    # - Response:
    #  {'status': 'OK', 'message': string}
    #  {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def send_feedback(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Send Feedback: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Send Feedback: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('send_feedback {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Send Feedback: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Send Feedback: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Send Feedback: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED

        # check if a parameter is empty
        data = flask.request.get_json()
        if data["feedback"] is None or data["rating"] is None or data["contactme"] is None:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Send Feedback: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST
        feedback = data['feedback']
        rating = data['rating']
        contactme = data['contactme']
        if data.get("recipient"):
            recipient = data['recipient']

        response = json.dumps({'status': 'OK', 'message': 'Feedback sent successfully.'})
        print('\r\nFeedback sent successfully: {}\r\n{}\r\n'.format(username, response))
        return response


    ########################################################################################################
    #
    # GET FAQS/ABOUT
    #
    # - Request:
    #   GET /others/ITEM
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'url': {'terms': string, 'privacy': string, 'license': string} }
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_item(self, item):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get About: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get About: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_{} {}'.format(item, username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get About: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get About: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get About: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED

        # check if a parameter is empty
        url = {}
        if item == "faqs":
            url["faqs"] = "https://richmondu.com/faqs"
        elif item == "about":
            url["terms"]   = "https://richmondu.com/terms"
            url["privacy"] = "https://richmondu.com/privacy"
            url["license"] = "https://richmondu.com/license"
        else:
            response = json.dumps({'status': 'NG', 'message': 'Invalid request found'})
            print('\r\nERROR Get Item Url: Invalid request found\r\n')
            return response, status.HTTP_400_BAD_REQUEST


        msg = {'status': 'OK', 'message': 'Content queried successfully.'}
        msg['url'] = url
        response = json.dumps(msg)
        print('\r\nContent queried successfully: {}\r\n{}\r\n'.format(username, response))
        return response


    ########################################################################################################
    #
    # GET SUPPORTED I2C DEVICES
    #
    # - Request:
    #   GET /others/i2cdevices
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'document': json_object } }
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_supported_i2c_devices(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get Supported I2C Devices: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Supported I2C Devices: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_supported_i2c_devices {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get Supported I2C Devices: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Supported I2C Devices: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get Supported I2C Devices: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED

        # check if a parameter is empty
        result, document = self.storage_client.get_supported_i2c_devices()
        if not result:
            response = json.dumps({'status': 'NG', 'message': 'Could not retrieve JSON document'})
            print('\r\nERROR Get Supported I2C Devices: Could not retrieve JSON document [{}]\r\n'.format(username))
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR


        msg = {'status': 'OK', 'message': 'Content queried successfully.'}
        msg['document'] = document
        response = json.dumps(msg)
        print('\r\nContent queried successfully: {}\r\n'.format(username))
        return response


    ########################################################################################################
    #
    # GET SUPPORTED SENSORS
    #
    # - Request:
    #   GET /others/sensordevices
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'document': json_object } }
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_supported_sensors(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get Supported Sensor Devices: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Supported Sensor Devices: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_supported_sensor_devices {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get Supported Sensor Devices: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Supported Sensor Devices: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get Supported Sensor Devices: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED

        # check if a parameter is empty
        result, document = self.storage_client.get_supported_sensor_devices()
        if not result:
            response = json.dumps({'status': 'NG', 'message': 'Could not retrieve JSON document'})
            print('\r\nERROR Get Supported Sensor Devices: Could not retrieve JSON document [{}]\r\n'.format(username))
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR


        msg = {'status': 'OK', 'message': 'Content queried successfully.', 'document': document}
        response = json.dumps(msg)
        print('\r\nContent queried successfully: {}\r\n{}\r\n'.format(username, response))
        return response


    ########################################################################################################
    #
    # GET DEVICE FIRMWARE UPDATES
    #
    # - Request:
    #   GET /others/firmwareupdates
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'document': json_object } }
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_device_firmware_updates(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get Device Firmware Updates: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Device Firmware Updates: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_device_firmware_updates {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get Device Firmware Updates: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Device Firmware Updates: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get Device Firmware Updates: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED

        # check if a parameter is empty
        result, document = self.storage_client.get_device_firmware_updates()
        if not result:
            response = json.dumps({'status': 'NG', 'message': 'Could not retrieve JSON document'})
            print('\r\nERROR Get Device Firmware Updates: Could not retrieve JSON document [{}]\r\n'.format(username))
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR


        msg = {'status': 'OK', 'message': 'Content queried successfully.', 'document': document}
        response = json.dumps(msg)
        print('\r\nContent queried successfully: {}\r\n{}\r\n'.format(username, response))
        return response


    ########################################################################################################
    #
    # REGISTER DEVICE TOKEN
    #
    # - Request:
    #   POST /mobile/devicetoken
    #   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
    #   data: {'token': jwtEncode(devicetoken, service)}
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def register_mobile_device_token(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Register mobile device token: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Register mobile device token: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('register_mobile_device_token username={}'.format(username))

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Register mobile device token: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Register mobile device token: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED

        # decode the devicetoken and service
        data = flask.request.get_json()
        if data.get("token") is None:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Register mobile device token: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST
        if len(data["token"]) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found 2'})
            print('\r\nERROR Register mobile device token: Empty parameter found 2\r\n')
            return response, status.HTTP_400_BAD_REQUEST
        devicetoken, service, reason = rest_api_utils.utils().get_jwtencode_user_pass(data["token"])
        if devicetoken is None or service is None:
            response = json.dumps({'status': 'NG', 'message': reason})
            print('\r\nERROR Register mobile device token: Devicetoken, service format invalid\r\n')
            return response, status.HTTP_400_BAD_REQUEST
        if service != "APNS" and service != "GCM":
            response = json.dumps({'status': 'NG', 'message': reason})
            print('\r\nERROR Register mobile device token: Service value is invalid\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # add mobile device token
        self.database_client.add_mobile_device_token(username, devicetoken, service, token["access"])

        #print('\r\nAdded mobile device token\r\n{}\r\n{}\r\n{}\r\n'.format(devicetoken, service, token["access"]))
        #print("")
        #devicetoken = self.database_client.get_all_mobile_device_token(username)
        #print(len(devicetoken))
        #print(devicetoken)
        #print("")

        response = json.dumps({'status': 'OK', 'message': 'Register mobile device token successful'})
        print('\r\nRegister mobile device token successful: {} {} {}\r\n'.format(username, service, devicetoken))
        return response


    ########################################################################################################
    #
    # COMPUTE PASSWORD
    #
    # - Request:
    #   POST /devicesimulator/devicepassword
    #   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
    #   data: {'uuid': string, 'serialnumber': string, 'poemacaddress': string}
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def compute_device_password(self):

        # decode the devicetoken and service
        data = flask.request.get_json()
        if data is None:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Compute password: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST
        if data.get("uuid") is None or data.get("serialnumber") is None or data.get("poemacaddress") is None:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Compute password: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # compute the password
        params = {
            "uuid": data["uuid"],                  # device uuid
            "serialnumber": data["serialnumber"], # device serial number
            "poemacaddress": data["poemacaddress"],  # device mac address in uppercase string ex. AA:BB:CC:DD:EE:FF
        }
        password = jwt.encode(params, config.CONFIG_JWT_SECRET_KEY_DEVICE, algorithm='HS256')
        password = password.decode("utf-8")

        response = json.dumps({'status': 'OK', 'message': 'Compute password successful', 'password': password})
        print('\r\nCompute password successful: {}\r\n'.format(data["uuid"]))
        return response

