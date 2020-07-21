#import os
#import ssl
import json
import time
#import hmac
#import hashlib
import flask
#import base64
import datetime
#import calendar
#from flask_json import FlaskJSON, JsonError, json_response, as_json
#from certificate_generator import certificate_generator
#from messaging_client import messaging_client
from rest_api_config import config
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



#CONFIG_SEPARATOR            = '/'
#CONFIG_PREPEND_REPLY_TOPIC  = "server"

class classes:
    I2C_DEVICE_CLASS_SPEAKER         = 0
    I2C_DEVICE_CLASS_DISPLAY         = 1
    I2C_DEVICE_CLASS_LIGHT           = 2
    I2C_DEVICE_CLASS_POTENTIOMETER   = 3
    I2C_DEVICE_CLASS_TEMPERATURE     = 4
    I2C_DEVICE_CLASS_HUMIDITY        = 5
    I2C_DEVICE_CLASS_ANEMOMETER      = 6
    I2C_DEVICE_CLASS_BATTERY         = 7
    I2C_DEVICE_CLASS_FLUID           = 8
    I2C_DEVICE_CLASS_AMBIENTLIGHT    = 9
    I2C_DEVICE_CLASS_MOTIONDETECTION = 10
    I2C_DEVICE_CLASS_CO2GAS          = 11
    I2C_DEVICE_CLASS_VOCGAS          = 12



class utils:

    def __init__(self):
        pass


    def sort_by_timestamp(self, elem):
        return elem['timestamp']

    def sort_by_devicename(self, elem):
        return elem['devicename']

    def sort_by_sensorname(self, elem):
        return elem['sensorname']


    def print_json(self, json_object, is_json=True, label=None):
        if is_json:
            json_formatted_str = json.dumps(json_object, indent=2)
        else: 
            json_formatted_str = json_object
        if label is None:
            print(json_formatted_str)
        else:
            print("{}\r\n{}".format(label, json_formatted_str))


    def get_i2c_device_class(self, classname):
        if classname == "temperature":
            return classes.I2C_DEVICE_CLASS_TEMPERATURE
        elif classname == "humidity":
            return classes.I2C_DEVICE_CLASS_HUMIDITY
        elif classname == "ambient light":
            return classes.I2C_DEVICE_CLASS_AMBIENTLIGHT
        elif classname == "motion detection":
            return classes.I2C_DEVICE_CLASS_MOTIONDETECTION
        elif classname == "Co2 gas":
            return classes.I2C_DEVICE_CLASS_CO2GAS
        elif classname == "VOC gas":
            return classes.I2C_DEVICE_CLASS_VOCGAS

        elif classname == "anemometer":
            return classes.I2C_DEVICE_CLASS_ANEMOMETER
        elif classname == "battery":
            return classes.I2C_DEVICE_CLASS_BATTERY
        elif classname == "fluid":
            return classes.I2C_DEVICE_CLASS_FLUID

        elif classname == "speaker":
            return classes.I2C_DEVICE_CLASS_SPEAKER
        elif classname == "display":
            return classes.I2C_DEVICE_CLASS_DISPLAY
        elif classname == "light":
            return classes.I2C_DEVICE_CLASS_LIGHT
        elif classname == "potentiometer":
            return classes.I2C_DEVICE_CLASS_POTENTIOMETER

        return 0xFF


    # Authorization header for the access token
    def get_auth_header_token(self):
        auth_header = flask.request.headers.get('Authorization')
        if auth_header is None:
            print("No Authorization header")
            return None
        token = auth_header.split(" ")
        if len(token) != 2:
            print("No Authorization Bearer header")
            return None
        if token[0] != "Bearer":
            print("No Bearer header")
            return None
        #print("auth header: {}".format(token[1]))
        return token[1]


    # Authorization header for username and password
    def get_auth_header_user_pass(self):
        auth_header = flask.request.headers.get('Authorization')
        if auth_header is None:
            reason = "No Authorization header"
            print(reason)
            return None, None, reason
        token = auth_header.split(" ")
        if len(token) != 2:
            reason = "No Authorization Bearer header"
            print(reason)
            return None, None, reason
        if token[0] != "Bearer":
            reason = "No Bearer header"
            print(reason)
            return None, None, reason
        return self.get_jwtencode_user_pass(token[1], to_lower=True)


    # Authorization header: Bearer JWT
    def get_jwtencode_user_pass(self, token, to_lower=False):
        payload = None
        try:
            payload = jwt.decode(token, config.CONFIG_JWT_SECRET_KEY, algorithms=['HS256'])
        except Exception as e:
            reason = "JWT decode exception"
            print(reason)
            print(e)
            return None, None, reason
        if payload is None:
            reason = "JWT decode failed"
            print(reason)
            return None, None, reason
        if not payload.get("username") or not payload.get("password") or not payload.get("iat") or not payload.get("exp"):
            reason = "JWT has missing fields"
            print(reason)
            return None, None, reason

        currepoch = int(time.time())
        if False:
            print("username: {}".format(payload["username"]))
            print("password: {}".format(payload["password"]))
            print("cur: {}".format(currepoch))
            print("iat: {}".format(payload["iat"]))
            print("exp: {}".format(payload["exp"]))

        if payload["exp"] - payload["iat"] != config.CONFIG_JWT_EXPIRATION:
            reason = "JWT expiration date is incorrect"
            print(reason)
            return None, None, reason
        # add lee way for both time start and time end
        # so that minor differences in time will not fail
        # example if pc is NOT set to automatically synchronize with SNTP
        # allow difference of +/- 60 seconds
        if currepoch < payload["iat"] - config.CONFIG_JWT_ADJUSTMENT:
            print("username: {}".format(payload["username"]))
            print("password: {}".format(payload["password"]))
            print("cur: {}".format(currepoch))
            print("iat: {}".format(payload["iat"]))
            print("exp: {}".format(payload["exp"]))
            reason = "currepoch({}) < payload[iat]({})".format(currepoch, payload["iat"])
            return None, None, reason
        elif currepoch > payload["exp"] + config.CONFIG_JWT_ADJUSTMENT:
            print("username: {}".format(payload["username"]))
            print("password: {}".format(payload["password"]))
            print("cur: {}".format(currepoch))
            print("iat: {}".format(payload["iat"]))
            print("exp: {}".format(payload["exp"]))
            reason = "currepoch({}) > payload[exp]({})".format(currepoch, payload["exp"])
            return None, None, reason
        if to_lower:
            return payload["username"].lower(), payload["password"], ""
        return payload["username"], payload["password"], ""

    # Authorization header for username and password
    def get_auth_header_user_pass_ota(self):
        auth_header = flask.request.headers.get('Authorization')
        if auth_header is None:
            reason = "No Authorization header"
            print(reason)
            return None, None, reason
        token = auth_header.split(" ")
        if len(token) != 2:
            reason = "No Authorization Bearer header"
            print(reason)
            return None, None, reason
        if token[0] != "Bearer":
            reason = "No Bearer header"
            print(reason)
            return None, None, reason
        return self.get_jwtencode_user_pass_ota(token[1])


    # Authorization header: Bearer JWT
    def get_jwtencode_user_pass_ota(self, token):
        payload = None
        try:
            payload = jwt.decode(token, config.CONFIG_JWT_SECRET_KEY_DEVICE, algorithms=['HS256'])
        except:
            reason = "JWT decode exception"
            print(reason)
            return None, None, reason
        if payload is None:
            reason = "JWT decode failed"
            print(reason)
            return None, None, reason
        if not payload.get("username") or not payload.get("password") or not payload.get("iat") or not payload.get("exp"):
            reason = "JWT has missing fields"
            print(reason)
            return None, None, reason

        currepoch = int(time.time())
        if True:
            print("username: {}".format(payload["username"]))
            print("password: {}".format(payload["password"]))
            print("cur: {}".format(currepoch))
            print("iat: {}".format(payload["iat"]))
            print("exp: {}".format(payload["exp"]))

        if payload["exp"] - payload["iat"] != config.CONFIG_JWT_EXPIRATION:
            reason = "JWT expiration date is incorrect"
            print(reason)
            return None, None, reason
        # add lee way for both time start and time end
        # so that minor differences in time will not fail
        # example if pc is NOT set to automatically synchronize with SNTP
        # allow difference of +/- 60 seconds
        if currepoch < payload["iat"] - config.CONFIG_JWT_ADJUSTMENT:
            print("username: {}".format(payload["username"]))
            print("password: {}".format(payload["password"]))
            print("cur: {}".format(currepoch))
            print("iat: {}".format(payload["iat"]))
            print("exp: {}".format(payload["exp"]))
            reason = "currepoch({}) < payload[iat]({})".format(currepoch, payload["iat"])
            return None, None, reason
        elif currepoch > payload["exp"] + config.CONFIG_JWT_ADJUSTMENT:
            print("username: {}".format(payload["username"]))
            print("password: {}".format(payload["password"]))
            print("cur: {}".format(currepoch))
            print("iat: {}".format(payload["iat"]))
            print("exp: {}".format(payload["exp"]))
            reason = "currepoch({}) > payload[exp]({})".format(currepoch, payload["exp"])
            return None, None, reason
        return payload["username"], payload["password"], payload


    def build_default_notifications(self, type, token, database_client):
        notifications = {}

        if type == "uart":
            notifications["messages"] = [
                {
                    "message": "Hello World", 
                    "enable": True
                }
            ]
        elif type == "gpio":
            notifications["messages"] = [
                {
                    "message": "Hello World", 
                    "enable": True
                }, 
                {
                    "message": "Hi World", 
                    "enable": True
                }
            ]
        else:
            notifications["messages"] = [
                {
                    "message": "Sensor threshold activated", 
                    "enable": True
                }, 
                {
                    "message": "Sensor threshold deactivated", 
                    "enable": True
                }
            ]

        notifications["endpoints"] = {
            "mobile": {
                "enable": False,
                "recipients": ""
            },
            "email": {
                "enable": False,
                "recipients": ""
            },
            "notification": {
                "enable": False,
                "recipients": ""
            },
            "modem": {
                "enable": False,
                "recipients": "",
                "isgroup": False
            },
            "storage": {
                "enable": False,
                "recipients": ""
            },
        }

        info = database_client.get_user_info(token['access'])
        if info is None:
            return None

        if info.get("email"):
            notifications["endpoints"]["email"]["recipients"] = info["email"]
            #notifications["endpoints"]["email"]["recipients_list"].append(info["email"])

        if info.get("email_verified"):
            notifications["endpoints"]["email"]["enable"] = info["email_verified"]

        if info.get("phone_number"):
            notifications["endpoints"]["mobile"]["recipients"] = info["phone_number"]
            #notifications["endpoints"]["mobile"]["recipients_list"].append(info["phone_number"])
            #notifications["endpoints"]["notification"]["recipients"] = info["phone_number"]
            #notifications["endpoints"]["notification"]["recipients_list"].append({ "to": info["phone_number"], "group": False })

        if type == "uart":
            if info.get("phone_number_verified"):
                notifications["endpoints"]["mobile"]["enable"] = info["phone_number_verified"]
                #notifications["endpoints"]["notification"]["enable"] = False

        return notifications
