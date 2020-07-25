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



class device_peripheral_properties:

    def __init__(self, database_client, messaging_requests):
        self.database_client = database_client
        self.messaging_requests = messaging_requests


    def is_message_list_valid(self, notification, isuart=False):
        max_message_len = 100

        # check message parameters
        if notification.get("messages") is None:
            return False
        messages = notification["messages"]
        if isuart:
            if len(messages) != 1:
                print("uart messages should be 1")
                return False
        else:
            if len(messages) != 2:
                print("ldsu messages should be 2")
                return False

        # check if the messages are valid if enabled
        for message in messages:
            if message.get("enable") is None or message.get("message") is None:
                return False
            if message["enable"] == True:
                message["message"] = message["message"].strip()
                # check empty message
                if len(message["message"]) == 0:
                    print("empty notification message")
                    return False
                # check message is more than maximum length
                if len(message["message"]) > max_message_len:
                    print("too big notification message {}".format(len(message["message"])))
                    return False
        return True

    def is_email_list_valid(self, notification, users):
        email = notification["endpoints"]["email"]
        if email["enable"] == False:
            return True

        # email is enabled, so check the recipients
        recipients = email["recipients"]
        recipients = recipients.split(",")
        for x in range(len(recipients)):
            recipients[x] = recipients[x].strip()

        # check for duplicates
        if len(recipients) != len(set(recipients)):
            print("some duplicates in the list {}".format(recipients))
            return False

        # check if the emails are valid
        for recipient in recipients:
            found = False
            for user in users:
                if recipient == user["email"]:
                    found = True
                    break
            if not found:
                print("email {} not found".format(recipient))
                return False
        return True

    def is_sms_list_valid(self, notification, users):
        mobile = notification["endpoints"]["mobile"]
        if mobile["enable"] == False:
            return True

        # mobile is enabled, so check the recipients
        recipients = mobile["recipients"]
        recipients = recipients.split(",")
        for x in range(len(recipients)):
            recipients[x] = recipients[x].strip()

        # check for duplicates
        if len(recipients) != len(set(recipients)):
            print("some duplicates in the list {}".format(recipients))
            return False

        # check if the numbers are valid
        for recipient in recipients:
            found = False
            for user in users:
                if user.get("phone_number"):
                    if recipient == user["phone_number"]:
                        if user.get("phone_number_verified"):
                            if user["phone_number_verified"] == True:
                                found = True
                                break
            if not found:
                print("sms {} not found".format(recipient))
                return False
        return True

    def is_pushnotif_list_valid(self, notification, users):
        mobile = notification["endpoints"]["notification"]
        if mobile["enable"] == False:
            return True

        # mobile is enabled, so check the recipients
        recipients = mobile["recipients"]
        recipients = recipients.split(",")
        for x in range(len(recipients)):
            recipients[x] = recipients[x].strip()

        # check for duplicates
        if len(recipients) != len(set(recipients)):
            print("some duplicates in the list {}".format(recipients))
            return False

        # empty recipient will use own
        if len(recipients) == 1:
            if recipients[0] == "":
                return True

        notification["endpoints"]["notification"]["recipients_ex"] = []

        # check if the numbers are valid
        for recipient in recipients:
            found = False
            for user in users:
                if user.get("phone_number"):
                    if recipient == user["phone_number"]:
                        if user.get("phone_number_verified"):
                            if user["phone_number_verified"] == True:
                                found = True
                                if user.get("email"):
                                    if user.get("email_verified"):
                                        if user["email_verified"] == True:
                                            notification["endpoints"]["notification"]["recipients_ex"].append(user["email"])
                                break
            if not found:
                print("pushsms {} not found".format(recipient))
                return False
        return True

    def is_device_list_valid(self, notification, entityname):
        modem = notification["endpoints"]["modem"]
        if modem["enable"] == False:
            return True

        # modem is enabled, so check the recipients
        isgroup = False
        if modem.get("isgroup") is not None:
            isgroup = modem["isgroup"]

        recipients = modem["recipients"]
        recipients = recipients.split(",")
        for x in range(len(recipients)):
            recipients[x] = recipients[x].strip()

        # check for duplicates
        if len(recipients) != len(set(recipients)):
            print("some duplicates in the list {}".format(recipients))
            return False

        if isgroup == False:
            # check if the device recipients are valid
            devices = self.database_client.get_devices(entityname)
            for recipient in recipients:
                found = False
                for device in devices:
                    if recipient == device["devicename"]:
                        found = True
                        break
                if not found:
                    print("device {} not found".format(recipient))
                    return False
        else:
            # check if the devicegroup recipients are valid
            devicegroups = self.database_client.get_devicegroups(entityname)
            for recipient in recipients:
                found = False
                for devicegroup in devicegroups:
                    if recipient == devicegroup["groupname"]:
                        found = True
                        break
                if not found:
                    print("devicegroup {} not found".format(recipient))
                    return False

        return True

    def is_configuration_valid(self, configuration, entityname):
        mode = configuration["mode"]

        if configuration.get("alert") is None:
            return False
        if configuration["alert"].get("type") is None:
            return False
        if configuration["alert"].get("period") is None:
            return False

        if mode == 0:
            if configuration.get("threshold") is None:
                return False
            if configuration["threshold"].get("value") is None:
                return False

        elif mode == 1:
            if configuration.get("threshold") is None:
                return False
            if configuration["threshold"].get("min") is None:
                return False
            if configuration["threshold"].get("max") is None:
                return False
            if configuration["threshold"].get("activate") is None:
                return False

        elif mode == 2:
            if configuration.get("hardware") is None:
                return False

            if configuration["hardware"].get("enable") is None:
                return False
            if not configuration["hardware"]["enable"]:
                return True
            if configuration["hardware"].get("recipients") is None:
                return False

            # hardware is enabled, so check the recipients
            isgroup = False
            if configuration["hardware"].get("isgroup") is not None:
                isgroup = configuration["hardware"]["isgroup"]

            recipients = configuration["hardware"]["recipients"]
            recipients = recipients.split(",")
            for x in range(len(recipients)):
                recipients[x] = recipients[x].strip()

            # check for duplicates
            if len(recipients) != len(set(recipients)):
                print("some duplicates in the list {}".format(recipients))
                return False

            if isgroup == False:
                # check if the device recipients are valid
                devices = self.database_client.get_devices(entityname)
                for recipient in recipients:
                    found = False
                    for device in devices:
                        if recipient == device["devicename"]:
                            found = True
                            break
                    if not found:
                        print("device {} not found".format(recipient))
                        return False
            else:
                # check if the devicegroup recipients are valid
                devicegroups = self.database_client.get_devicegroups(entityname)
                for recipient in recipients:
                    found = False
                    for devicegroup in devicegroups:
                        if recipient == devicegroup["groupname"]:
                            found = True
                            break
                    if not found:
                        print("devicegroup {} not found".format(recipient))
                        return False

        return True

    #
    # GET UART PROPERTIES
    #
    # - Request:
    #   GET /devices/device/<devicename>/uart/properties
    #   headers: { 'Authorization': 'Bearer ' + token.access }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string, 'value': { 'baudrate': int, 'parity': int, 'flowcontrol': int, 'stopbits': int, 'databits': int } }
    #   { 'status': 'NG', 'message': string }
    #
    def get_uart_prop(self, devicename):
        api = 'get_uart_prop'

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        #data = {}
        #data['token'] = token
        #data['devicename'] = devicename
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        #data['username'] = username
        #print('get_uart_prop {} devicename={}'.format(data['username'], data['devicename']))


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get Uart: Authorization not allowed [{}]\r\n'.format(username))
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
            print('\r\nERROR Get Uart: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND


        configuration = self.database_client.get_device_peripheral_configuration(entityname, devicename, "uart", 1, None)
        if configuration:
            value = configuration["attributes"]
            print(configuration["attributes"])
        else:
            value = {
                "baudrate": 7,
                "parity": 0,
                "flowcontrol": 0,
                "stopbits": 0,
                "databits": 1,
            }

        source = "uart"
        notification = self.database_client.get_device_notification(entityname, devicename, source)
        if notification is not None:
            if notification.get("endpoints"):
                if notification["endpoints"].get("notification"):
                    if notification["endpoints"]["notification"].get("recipients_ex") is not None:
                        print(notification["endpoints"]["notification"]["recipients_ex"])
                        notification["endpoints"]["notification"].pop("recipients_ex")
            value['notification'] = notification
        else:
            value['notification'] = rest_api_utils.utils().build_default_notifications("uart", token, self.database_client)

        msg = {'status': 'OK', 'message': 'UART properties retrieved successfully.', 'value': value}
        response = json.dumps(msg)
        return response


    #
    # SET UART PROPERTIES
    #
    # - Request:
    #   POST /devices/device/<devicename>/uart/properties
    #   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
    #   data: { 'baudrate': int, 'parity': int, 'flowcontrol': int, 'stopbits': int, 'databits': int }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string }
    #   { 'status': 'NG', 'message': string }
    #
    def set_uart_prop(self, devicename):
        api = 'set_uart_prop'

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED

        # get username from token
        data = flask.request.get_json()
        if data is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
            print('\r\nERROR Invalid parameters\r\n')
            return response, status.HTTP_400_BAD_REQUEST
        if data.get('baudrate') is None or data.get('parity') is None or data.get('databits') is None or data.get('stopbits') is None or data.get('flowcontrol') is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
            print('\r\nERROR Invalid parameters\r\n')
            return response, status.HTTP_400_BAD_REQUEST
        if data.get('notification') is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
            print('\r\nERROR Invalid parameters\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # get notifications and remove from list
        notification = data['notification']
        data.pop('notification')
        #print(notification)
        #print(data)

        username = self.database_client.get_username_from_token({'access': auth_header_token})
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        #print('set_uart_prop {} devicename={}'.format(username, devicename))


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Set Uart: Authorization not allowed [{}]\r\n'.format(username))
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
            print('\r\nERROR Set Uart: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND


        # check list of email and sms and devices are valid
        users = self.database_client.get_registered_users()
        if not self.is_email_list_valid(notification, users):
            response = json.dumps({'status': 'NG', 'message': 'At least one of the emails do not belong to a verified user account. All Email recipients should belong to a valid user account.'})
            print('\r\nERROR Set Uart: Email list is not valid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        if not self.is_sms_list_valid(notification, users):
            response = json.dumps({'status': 'NG', 'message': 'At least one of the mobile numbers do not belong to a verified user account. All SMS recipients should belong to a valid user account.'})
            print('\r\nERROR Set Uart: Mobile number list is not valid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        if not self.is_pushnotif_list_valid(notification, users):
            response = json.dumps({'status': 'NG', 'message': 'At least one of the mobile numbers do not belong to a verified user account. All Push Notification recipients should belong to a valid user account.'})
            print('\r\nERROR Set Uart: Mobile number list is not valid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        if not self.is_device_list_valid(notification, entityname):
            response = json.dumps({'status': 'NG', 'message': 'At least one of the device/devicegroup is not valid. All device/devicegroup recipients should be valid.'})
            print('\r\nERROR Set Uart: Device/device group list is not valid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        if not self.is_message_list_valid(notification, True):
            response = json.dumps({'status': 'NG', 'message': 'At least one of the alert messages is not valid. All alert messages should be valid.'})
            print('\r\nERROR Set Uart: Alert messages is not valid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        source = "uart"
        item = self.database_client.update_device_notification(entityname, devicename, source, notification)

        # update device configuration database for device bootup
        #print("data={}".format(data))
        item = self.database_client.update_device_peripheral_configuration(entityname, devicename, "uart", 1, None, None, None, data)


        data['token'] = {'access': auth_header_token}
        data['devicename'] = devicename
        data['username'] = username
        response, status_return = self.messaging_requests.process(api, data)
        if status_return != 200:
            return response, status_return

        msg = {'status': 'OK', 'message': 'UART properties set successfully.'}
        response = json.dumps(msg)
        return response


    #
    # ENABLE/DISABLE UART
    #
    # - Request:
    #   POST /devices/device/DEVICENAME/uart/enable
    #   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
    #   data: { 'enable': int }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string }
    #   { 'status': 'NG', 'message': string }
    #
    #@app.route('/devices/device/<devicename>/uart/enable', methods=['POST'])
    #def enable_uart(self, devicename):
    #    api = 'enable_uart'

    #    # get token from Authorization header
    #    auth_header_token = self.utils.get_auth_header_token()
    #    if auth_header_token is None:
    #        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
    #        print('\r\nERROR Invalid authorization header\r\n')
    #        return response, status.HTTP_401_UNAUTHORIZED

    #    # get username from token
    #    data = flask.request.get_json()

    #    # check parameter input
    #    if data['enable'] is None:
    #        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
    #        print('\r\nERROR Invalid parameters\r\n')
    #        return response, status.HTTP_400_BAD_REQUEST

    #    data['token'] = {'access': auth_header_token}
    #    data['devicename'] = devicename
    #    username = self.database_client.get_username_from_token(data['token'])
    #    if username is None:
    #        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
    #        print('\r\nERROR Token expired\r\n')
    #        return response, status.HTTP_401_UNAUTHORIZED
    #    data['username'] = username
    #    print('enable_uart {} devicename={}'.format(data['username'], data['devicename']))

    #    return self.messaging_requests.process(api, data)

    
    #
    # GET UARTS
    #
    # - Request:
    #   GET /devices/device/<devicename>/uarts
    #   headers: { 'Authorization': 'Bearer ' + token.access }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string, 
    #     'value': { 
    #       'uarts': [
    #         {'enabled': int}, 
    #       ]
    #     }
    #   }
    #   { 'status': 'NG', 'message': string }
    #
    #@app.route('/devices/device/<devicename>/uarts', methods=['GET'])
    #def get_uarts(self, devicename):
    #    api = 'get_uarts'

    #    # get token from Authorization header
    #    auth_header_token = self.utils.get_auth_header_token()
    #    if auth_header_token is None:
    #        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
    #        print('\r\nERROR Invalid authorization header\r\n')
    #        return response, status.HTTP_401_UNAUTHORIZED
    #    token = {'access': auth_header_token}

    #    # get username from token
    #    data = {}
    #    data['token'] = token
    #    data['devicename'] = devicename
    #    username = self.database_client.get_username_from_token(data['token'])
    #    if username is None:
    #        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
    #        print('\r\nERROR Token expired\r\n')
    #        return response, status.HTTP_401_UNAUTHORIZED
    #    data['username'] = username
    #    print('get_uarts {} devicename={}'.format(data['username'], data['devicename']))

    #    return self.messaging_requests.process(api, data)
    
    

    ########################################################################################################
    #
    # SET LDSU DEVICE PROPERTIES
    #
    # - Request:
    #   POST /devices/device/DEVICENAME/UUID/NUMBER/sensors/sensor/<sensorname>/properties
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   data: adsasdasdasdasdasdasdasd
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def set_xxx_dev_prop(self, devicename, xxx, number, sensorname):
        #print('set_{}_dev_prop'.format(xxx))

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Set {} Sensor: Invalid authorization header\r\n'.format(xxx))
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token} 
        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Set {} Sensor: Token expired\r\n'.format(xxx))
            return response, status.HTTP_401_UNAUTHORIZED
        #print('{} devicename={} number={} sensorname={}'.format(username, devicename, number, sensorname))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0 or len(devicename) == 0 or len(sensorname) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Set {} Sensor: Empty parameter found\r\n'.format(xxx))
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Set {} Sensor: Token expired [{}]\r\n'.format(xxx, username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Set {} Sensor: Token is invalid [{}]\r\n'.format(xxx, username))
            return response, status.HTTP_401_UNAUTHORIZED

        # get username from token
        data = flask.request.get_json()
        if data is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
            print('\r\nERROR Invalid parameters\r\n')
            return response, status.HTTP_400_BAD_REQUEST


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Set Peripheral Sensor: Authorization not allowed [{}]\r\n'.format(username))
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
            print('\r\nERROR Set {} Sensor: Device is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        # check if ldsu is registered
        ldsu = self.database_client.get_ldsu(entityname, devicename, xxx)
        if not ldsu:
            response = json.dumps({'status': 'NG', 'message': 'LDSU is not registered'})
            print('\r\nERROR Set {} Sensor: LDSU is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        # check if sensor is registered
        sensor = self.database_client.get_sensor(entityname, devicename, xxx, number, sensorname)
        if not sensor:
            response = json.dumps({'status': 'NG', 'message': 'Sensor is not registered'})
            print('\r\nERROR Set {} Sensor: Sensor is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND
        if sensor["sensorname"] != sensorname:
            response = json.dumps({'status': 'NG', 'message': 'Sensor name is incorrect'})
            print('\r\nERROR Set {} Sensor: Sensor name is incorrect [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_400_BAD_REQUEST


        # no notification data
        if not data.get("notification"):
            # set to disabled and configured
            self.database_client.set_enable_configure_sensor(entityname, devicename, xxx, number, sensorname, 0, 1)
            # update configuration
            item = self.database_client.update_device_peripheral_configuration(entityname, devicename, xxx, int(number), None, None, None, data)
            response = json.dumps({'status': 'OK', 'message': 'Sensor set successfully'})
            return response


        # has notification parameter (for class and subclass)
        notification = data['notification']
        data.pop('notification')

        # check list of email and sms and devices are valid
        users = self.database_client.get_registered_users()
        if not self.is_email_list_valid(notification, users):
            response = json.dumps({'status': 'NG', 'message': 'At least one of the emails do not belong to a verified user account. All email recipients should belong to a valid user account.'})
            print('\r\nERROR Set Peripheral Sensor: Email list is not valid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        if not self.is_sms_list_valid(notification, users):
            response = json.dumps({'status': 'NG', 'message': 'At least one of the mobile numbers do not belong to a verified user account. All SMS recipients should belong to a valid user account.'})
            print('\r\nERROR Set Peripheral Sensor: Mobile number list is not valid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        if not self.is_pushnotif_list_valid(notification, users):
            response = json.dumps({'status': 'NG', 'message': 'At least one of the mobile numbers do not belong to a verified user account. All Push Notification recipients should belong to a valid user account.'})
            print('\r\nERROR Set  Peripheral Sensor: Mobile number list is not valid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        if not self.is_device_list_valid(notification, entityname):
            response = json.dumps({'status': 'NG', 'message': 'At least one of the device/devicegroup is not valid. All device/devicegroup recipients should be valid.'})
            print('\r\nERROR Set Peripheral Sensor: Device/device group list is not valid [{}]\r\n'.format(username))
            return response, status.HTTP_404_NOT_FOUND
        if not self.is_configuration_valid(data, entityname):
            response = json.dumps({'status': 'NG', 'message': 'Configuration is not valid.'})
            print('\r\nERROR Set Peripheral Sensor: Configuration is not valid [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST
        if not self.is_message_list_valid(notification):
            response = json.dumps({'status': 'NG', 'message': 'At least one of the alert messages is not valid. All alert messages should be valid.'})
            print('\r\nERROR Set Peripheral Sensor: Alert messages is not valid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # set to disabled and configured
        self.database_client.set_enable_configure_sensor(entityname, devicename, xxx, number, sensorname, 0, 1)

        # update notification and configuration
        self.database_client.update_device_notification_with_notification_subclass(entityname, devicename, xxx, notification, None, int(number))
        item = self.database_client.update_device_peripheral_configuration(entityname, devicename, xxx, int(number), None, None, None, data)


        msg = {'status': 'OK', 'message': 'Sensor properties set successfully.'}
        response = json.dumps(msg)
        return response



    ########################################################################################################
    #
    # GET LDSU DEVICE PROPERTIES
    #
    # - Request:
    #   POST /devices/device/DEVICENAME/UUID/NUMBER/sensors/sensor/<sensorname>/properties
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'value': {}}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_xxx_dev_prop(self, devicename, xxx, number, sensorname):
        #print('get_{}_dev_prop'.format(xxx))

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
        #print('{} devicename={} number={} sensorname={}'.format(username, devicename, number, sensorname))

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


        # check if device is registered
        deviceinfo = self.database_client.find_device(entityname, devicename)
        if not deviceinfo:
            response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
            print('\r\nERROR Get {} Sensor: Device is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        # check if ldsu is registered
        ldsu = self.database_client.get_ldsu(entityname, devicename, xxx)
        if not ldsu:
            response = json.dumps({'status': 'NG', 'message': 'LDSU is not registered'})
            print('\r\nERROR Get {} Sensor: LDSU is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        # check if sensor is registered
        sensor = self.database_client.get_sensor(entityname, devicename, xxx, number, sensorname)
        if not sensor:
            response = json.dumps({'status': 'NG', 'message': 'Sensor is not registered'})
            print('\r\nERROR Get {} Sensor: Sensor is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND
        if sensor["sensorname"] != sensorname:
            response = json.dumps({'status': 'NG', 'message': 'Sensor name is incorrect'})
            print('\r\nERROR Get {} Sensor: Sensor name is incorrect [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_400_BAD_REQUEST

        # get sensor configuration
        value = {}
        configuration = self.database_client.get_device_peripheral_configuration(entityname, devicename, xxx, int(number), None)
        if configuration:
            value = configuration["attributes"]

        # get sensor notification
        (notification, subattributes_notification) = self.database_client.get_device_notification_with_notification_subclass(entityname, devicename, xxx, int(number))
        if notification is not None:
            if notification.get("endpoints"):
                if notification["endpoints"].get("notification"):
                    if notification["endpoints"]["notification"].get("recipients_ex") is not None:
                        #print(notification["endpoints"]["notification"]["recipients_ex"])
                        notification["endpoints"]["notification"].pop("recipients_ex")
            value['notification'] = notification
        else:
            value['notification'] = rest_api_utils.utils().build_default_notifications(xxx, token, self.database_client)

        msg = {'status': 'OK', 'message': 'Sensor properties retrieved successfully.', 'value': value}
        response = json.dumps(msg)
        return response


    ########################################################################################################
    #
    # DELETE LDSU DEVICE PROPERTIES
    #
    # - Request:
    #   DELETE /devices/device/DEVICENAME/UUID/NUMBER/sensors/sensor/<sensorname>/properties
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'value': {}}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def delete_xxx_dev_prop(self, devicename, xxx, number, sensorname):
        #print('delete_{}_dev_prop'.format(xxx))

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Delete {} Sensor: Invalid authorization header\r\n'.format(xxx))
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token} 
        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Delete {} Sensor: Token expired\r\n'.format(xxx))
            return response, status.HTTP_401_UNAUTHORIZED
        #print('{} devicename={} number={} sensorname={}'.format(username, devicename, number, sensorname))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0 or len(devicename) == 0 or len(sensorname) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Delete {} Sensor: Empty parameter found\r\n'.format(xxx))
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Delete {} Sensor: Token expired [{}]\r\n'.format(xxx, username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Delete {} Sensor: Token is invalid [{}]\r\n'.format(xxx, username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.DELETE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Delete Peripheral Sensor: Authorization not allowed [{}]\r\n'.format(username))
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
            print('\r\nERROR Delete {} Sensor: Device is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        # check if ldsu is registered
        ldsu = self.database_client.get_ldsu(entityname, devicename, xxx)
        if not ldsu:
            response = json.dumps({'status': 'NG', 'message': 'LDSU is not registered'})
            print('\r\nERROR Delete {} Sensor: LDSU is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        # check if sensor is registered
        sensor = self.database_client.get_sensor(entityname, devicename, xxx, number, sensorname)
        if not sensor:
            response = json.dumps({'status': 'NG', 'message': 'Sensor is not registered'})
            print('\r\nERROR Delete {} Sensor: Sensor is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND
        if sensor["sensorname"] != sensorname:
            response = json.dumps({'status': 'NG', 'message': 'Sensor name is incorrect'})
            print('\r\nERROR Delete {} Sensor: Sensor name is incorrect [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_400_BAD_REQUEST

        # delete sensor configuration
        self.database_client.delete_device_peripheral_configuration(entityname, devicename, xxx, int(number), None)

        # delete sensor notification
        self.database_client.delete_device_notification_sensor_ex(entityname, devicename, xxx, int(number))

        # set to disabled and unconfigured
        self.database_client.set_enable_configure_sensor(entityname, devicename, xxx, number, sensorname, 0, 0)

        response = json.dumps({'status': 'OK', 'message': 'Sensor properties deleted'})
        return response


    ########################################################################################################
    #
    # ENABLE/DISABLE LDSU DEVICE
    #
    # - Request:
    #   POST /devices/device/DEVICENAME/UUID/NUMBER/sensors/sensor/SENSORNAME/enable
    #   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
    #   data: { 'enable': int }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string }
    #   { 'status': 'NG', 'message': string }
    #
    ########################################################################################################
    def enable_xxx_dev(self, devicename, xxx, number, sensorname):
        api = 'enable_ldsu_dev'

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED

        # check parameter input
        data = flask.request.get_json()
        if data is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
            print('\r\nERROR Invalid parameters\r\n')
            return response, status.HTTP_400_BAD_REQUEST
        if data.get('enable') is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
            print('\r\nERROR Invalid parameters\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # get username from token
        data['token'] = {'access': auth_header_token}
        data['devicename'] = devicename
        username = self.database_client.get_username_from_token(data['token'])
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        data['username'] = username


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Enable Peripheral Sensor: Authorization not allowed [{}]\r\n'.format(username))
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
            print('\r\nERROR Enable {} Sensor: Device is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        # check if ldsu is registered
        ldsu = self.database_client.get_ldsu(entityname, devicename, xxx)
        if not ldsu:
            response = json.dumps({'status': 'NG', 'message': 'LDSU is not registered'})
            print('\r\nERROR Enable {} Sensor: LDSU is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        # check if sensor is registered
        sensor = self.database_client.get_sensor(entityname, devicename, xxx, number, sensorname)
        if not sensor:
            response = json.dumps({'status': 'NG', 'message': 'Sensor is not registered'})
            print('\r\nERROR Enable {} Sensor: Sensor is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND
        if sensor["sensorname"] != sensorname:
            response = json.dumps({'status': 'NG', 'message': 'Sensor name is incorrect'})
            print('\r\nERROR Enable {} Sensor: Sensor name is incorrect [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_400_BAD_REQUEST

        # check if sensor is configured
        if sensor["configured"] == 0:
            response = json.dumps({'status': 'NG', 'message': 'Sensor is not yet configured'})
            print('\r\nERROR Enable {} Sensor: Sensor is yet configured [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_400_BAD_REQUEST

        #print('enable_{}_dev {} devicename={} number={}'.format(xxx, entityname, devicename, number))


        # get opmode
        mode = str(0)
        configuration = self.database_client.get_device_peripheral_configuration(entityname, devicename, xxx, int(number), None)
        if configuration:
            if configuration["attributes"].get("opmode") is not None:
                mode = str(configuration["attributes"]["opmode"])


        # set enabled to do_enable and configured to 1
        # set enabled
        do_enable = data['enable']
        self.database_client.set_enable_configure_sensor(entityname, devicename, xxx, number, sensorname, do_enable, 1)
        self.database_client.set_enable_device_peripheral_configuration(entityname, devicename, xxx, int(number), None, do_enable)

        # communicate with device
        data["UID"] = xxx
        data['SAID'] = number
        data['MODE'] = mode
        response, status_return = self.messaging_requests.process(api, data)
        if status_return != 200:
            # allow enabling/disabling even when device is offline
            return response, status_return


        msg = {'status': 'OK', 'message': 'Sensor enabled/disabled successfully.'}
        response = json.dumps(msg)
        return response


    ########################################################################################################
    #
    # CHANGE LDSU DEVICE NAME
    #
    # - Request:
    #   POST /devices/device/DEVICENAME/UUID/NUMBER/sensors/sensor/SENSORNAME/enable
    #   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
    #   data: { 'name': string }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string }
    #   { 'status': 'NG', 'message': string }
    #
    ########################################################################################################
    def change_xxx_dev_name(self, devicename, xxx, number, sensorname):
        #print('change_{}_dev_name'.format(xxx))

        # check number parameter
        #if int(number) > 4 or int(number) < 1:
        #    response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        #    print('\r\nERROR Invalid parameters\r\n')
        #    return response, status.HTTP_400_BAD_REQUEST

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED

        # get username from token
        username = self.database_client.get_username_from_token({'access': auth_header_token})
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED

        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Change Peripheral Sensor Name: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED

            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # check parameters
        data = flask.request.get_json()
        if data is None:
            response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
            print('\r\nERROR Change Peripheral Sensor Name: Parameters not included [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_400_BAD_REQUEST
        if data.get('name') is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
            print('\r\nERROR Invalid parameters\r\n')
            return response, status.HTTP_400_BAD_REQUEST
        # check LDSUdevicename
        if len(data['name']) > 32 or len(data['name']) == 0:
            response = json.dumps({'status': 'NG', 'message': 'LDSUdevicename length is invalid'})
            print('\r\nERROR Change Peripheral Sensor Name: LDSUdevicename length is invalid [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_400_BAD_REQUEST

        # check if device is registered
        deviceinfo = self.database_client.find_device(entityname, devicename)
        if not deviceinfo:
            response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
            print('\r\nERROR Change Peripheral Sensor Name: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        # check if ldsu is registered
        ldsu = self.database_client.get_ldsu(entityname, devicename, xxx)
        if not ldsu:
            response = json.dumps({'status': 'NG', 'message': 'LDSU is not registered'})
            print('\r\nERROR Change {} Sensor Name: LDSU is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        # check if sensor is registered
        sensor = self.database_client.get_sensor(entityname, devicename, xxx, number, None)
        if not sensor:
            response = json.dumps({'status': 'NG', 'message': 'Sensor is not registered'})
            print('\r\nERROR Change {} Sensor Name: Sensor is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND
        if sensor["sensorname"] != sensorname:
            response = json.dumps({'status': 'NG', 'message': 'Sensor name is incorrect'})
            print('\r\nERROR Enable {} Sensor: Sensor name is incorrect [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_400_BAD_REQUEST

        # change name
        result = self.database_client.change_sensor_name(entityname, devicename, xxx, number, data["name"])


        msg = {'status': 'OK', 'message': 'Peripheral Sensor name changed successfully.'}
        response = json.dumps(msg)
        #print('\r\nPeripheral Sensor name changed successful: {} {}\r\n'.format(username, devicename))
        return response


    ########################################################################################################
    #
    # DELETE PERIPHERAL SENSOR PROPERTIES
    #
    # - Request:
    #   DELETE /devices/device/DEVICENAME/sensors/properties
    #   headers: { 'Authorization': 'Bearer ' + token.access }
    #
    # - Response:
    #   { 'status': 'OK', 'message': string }
    #   { 'status': 'NG', 'message': string }
    #
    ########################################################################################################
    def delete_all_device_sensors_properties(self, devicename):

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Delete All Device Sensors Properties: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Delete All Device Sensors Properties: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        #print('delete_all_device_sensors_properties {} devicename={}'.format(username, devicename))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Delete All Device Sensors Properties: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Delete All Device Sensors Properties: Token expired [{} {}]\r\n'.format(username, devicename))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Delete All Device Sensors Properties: Token is invalid [{} {}]\r\n'.format(username, devicename))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.DELETE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Delete All Device Sensors Properties: Authorization not allowed [{}]\r\n'.format(username))
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
            print('\r\nERROR Delete All Device Sensors Properties: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        self.database_client.delete_all_device_peripheral_configuration(entityname, devicename)


        msg = {'status': 'OK', 'message': 'Delete All Device Sensors Properties deleted successfully.',}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        #print('\r\nDelete All Device Sensors Properties successful: {} {}\r\n'.format(username, devicename))
        return response



    ########################################################################################################
    #
    # GET LDSU DEVICE READINGS
    #
    # - Request:
    #   POST /devices/device/DEVICENAME/UUID/NUMBER/sensors/sensor/<sensorname>/readings
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'value': {}}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_xxx_dev_readings(self, devicename, xxx, number, sensorname):

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get {} Sensor Readings: Invalid authorization header\r\n'.format(xxx))
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token} 
        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get {} Sensor Readings: Token expired\r\n'.format(xxx))
            return response, status.HTTP_401_UNAUTHORIZED
        #print('get_{}_dev_readings {} devicename={} number={} sensorname={}'.format(xxx, username, devicename, number, sensorname))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0 or len(devicename) == 0 or len(sensorname) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get {} Sensor Readings: Empty parameter found\r\n'.format(xxx))
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get {} Sensor Readings: Token expired [{}]\r\n'.format(xxx, username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get {} Sensor Readings: Token is invalid [{}]\r\n'.format(xxx, username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get Peripheral Sensor Readings: Authorization not allowed [{}]\r\n'.format(username))
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
            print('\r\nERROR Get {} Sensor Readings: Device is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        # check if ldsu is registered
        ldsu = self.database_client.get_ldsu(entityname, devicename, xxx)
        if not ldsu:
            response = json.dumps({'status': 'NG', 'message': 'LDSU is not registered'})
            print('\r\nERROR Get {} Sensor Readings: LDSU is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        # check if sensor is registered
        sensor = self.database_client.get_sensor(entityname, devicename, xxx, number, sensorname)
        if not sensor:
            response = json.dumps({'status': 'NG', 'message': 'Sensor is not registered'})
            print('\r\nERROR Get {} Sensor Readings: Sensor is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND
        if sensor["sensorname"] != sensorname:
            response = json.dumps({'status': 'NG', 'message': 'Sensor name is incorrect'})
            print('\r\nERROR Get {} Sensor Readings: Sensor name is incorrect [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_400_BAD_REQUEST
        if not sensor["enabled"]:
            response = json.dumps({'status': 'NG', 'message': 'Sensor is not enabled'})
            print('\r\nERROR Get {} Sensor Readings: Sensor is not enabled [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_400_BAD_REQUEST

        # get the sensor reading
        reading = self.database_client.get_sensor_reading(entityname, devicename, xxx, int(number))
        if reading:
            sensor["readings"] = reading


        msg = {'status': 'OK', 'message': 'Sensor readings retrieved successfully.', 'sensor': sensor}
        response = json.dumps(msg)
        return response