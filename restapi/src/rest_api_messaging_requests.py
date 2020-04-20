#import os
#import ssl
import json
import time
#import hmac
#import hashlib
#import flask
#import base64
import datetime
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
import threading
#import copy
#from redis_client import redis_client
#import statistics



CONFIG_SEPARATOR            = '/'
CONFIG_PREPEND_REPLY_TOPIC  = "server"

CONFIG_WAIT_DEVICE_RESPONSE_TIMEOUT_SEC  = 3
CONFIG_WAIT_DEVICE_RESPONSE_FREQUENCY_MS = 250
CONFIG_USE_REDIS_FOR_MQTT_RESPONSE  = True



class messaging_requests:

    def __init__(self, database_client, messaging_client, redis_client, event_dict, queue_dict):
        self.database_client = database_client
        self.messaging_client = messaging_client
        self.redis_client = redis_client
        self.event_dict = event_dict
        self.queue_dict = queue_dict


    def generate_publish_topic(self, data, deviceid, api, separator):
        topic = deviceid + separator + api 
        return topic

    def generate_publish_payload(self, data):
        data.pop('username')
        data.pop('token')
        data.pop('devicename')
        payload = json.dumps(data)
        return payload

    def generate_subscribe_topic(self, topic, separator):
        topic = CONFIG_PREPEND_REPLY_TOPIC + separator + topic
        return topic

    def process(self, api, data, timeout=CONFIG_WAIT_DEVICE_RESPONSE_TIMEOUT_SEC):

        #print("\r\nAPI: {} {} devicename={}".format(api, data['username'], data['devicename']))

        username = data['username']
        token = data['token']
        devicename = data['devicename']

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED

        # check if device is registered
        if not self.database_client.find_device(username, devicename):
            response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
            print('\r\nERROR Device is not registered [{}]\r\n'.format(username))
            return response, status.HTTP_404_NOT_FOUND

        # get deviceid for subscribe purpose (AMQP)
        deviceid = self.database_client.get_deviceid(username, devicename)

        # construct publish/subscribe topics and payloads
        pubtopic = self.generate_publish_topic(data, deviceid, api, CONFIG_SEPARATOR)
        payload = self.generate_publish_payload(data)
        subtopic = self.generate_subscribe_topic(pubtopic, CONFIG_SEPARATOR)

        try:
            # subscribe for response
            ret = self.messaging_client.subscribe(subtopic, subscribe=True, deviceid=deviceid)
            if ret:
                # use event object to wait for response
                event_response_available = threading.Event()
                self.event_dict[subtopic] = event_response_available

                # publish request
                self.messaging_client.publish(pubtopic, payload)

                # receive response
                #start = time.time()
                event_response_available.wait(timeout)
                #print("{}".format(time.time()-start))
                if CONFIG_USE_REDIS_FOR_MQTT_RESPONSE:
                    response = self.redis_client.mqtt_response_get_payload(subtopic)
                    if response:
                        self.redis_client.mqtt_response_del_payload(subtopic)
                else:
                    if subtopic in self.queue_dict:
                        response = self.queue_dict[subtopic].decode("utf-8")
                        self.queue_dict.pop(subtopic)
                    else:
                        response = None
                #response = receive_message(subtopic, timeout)

                # unsubscribe for response
                self.messaging_client.subscribe(subtopic, subscribe=False)
            else:
                msg = {'status': 'NG', 'message': 'Could not communicate with device'}
                if new_token:
                    msg['new_token'] = new_token
                response = json.dumps(msg)
                print('\r\nERROR Could not communicate with device [{}, {}]\r\n'.format(username, devicename))
                return response, status.HTTP_500_INTERNAL_SERVER_ERROR
        except:
            msg = {'status': 'NG', 'message': 'Could not communicate with device'}
            if new_token:
                msg['new_token'] = new_token
            response = json.dumps(msg)
            print('\r\nERROR Could not communicate with device [{}, {}]\r\n'.format(username, devicename))
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR

        # return HTTP response
        if response is None:
            msg = {'status': 'NG', 'message': 'Device is unreachable'}
            if new_token:
                msg['new_token'] = new_token
            response = json.dumps(msg)
            print('\r\nERROR Device is unreachable [{}, {}] DATETIME {}\r\n'.format(username, devicename, datetime.datetime.now()))
            return response, status.HTTP_503_SERVICE_UNAVAILABLE

        #print(response)
        msg = {'status': 'OK', 'message': 'Device accessed successfully.'}
        if new_token:
            msg['new_token'] = new_token
        try:
            msg['value'] = (json.loads(response))["value"]
            response = json.dumps(msg)
        except:
            response = json.dumps(msg)
        return response, 200
