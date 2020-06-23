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
from rest_api_config import config
#from database import database_client
#from flask_cors import CORS
from flask_api import status
from jose import jwk, jwt
#import http.client
#from s3_client import s3_client
import threading
import copy
#from redis_client import redis_client
#import statistics
import rest_api_utils
from database import database_categorylabel, database_crudindex



#CONFIG_SEPARATOR            = '/'
#CONFIG_PREPEND_REPLY_TOPIC  = "server"



class device_otaupdates:

    def __init__(self, database_client, storage_client, messaging_requests):
        self.database_client = database_client
        self.storage_client = storage_client
        self.messaging_requests = messaging_requests


    def sort_by_devicename(self, elem):
        return elem['devicename']

    ########################################################################################################
    #
    # UPDATE FIRMWARE
    #
    # - Request:
    #   POST /devices/device/<devicename>/firmware
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   data: {'version': string}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def update_firmware(self, devicename):
        api = 'beg_ota'

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Upgrade Device Firmware: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED

        # get username from token
        data = flask.request.get_json()
        data['token'] = {'access': auth_header_token}
        data['devicename'] = devicename
        username = self.database_client.get_username_from_token(data['token'])
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Upgrade Device Firmware: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        data['username'] = username
        print('update_firmware {} devicename={}'.format(data['username'], data['devicename']))


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Upgrade Device Firmware: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # check if a parameter is empty
        result, document = self.storage_client.get_device_firmware_updates()
        if not result:
            response = json.dumps({'status': 'NG', 'message': 'Could not retrieve JSON document'})
            print('\r\nERROR Upgrade Device Firmware: Could not retrieve JSON document [{}]\r\n'.format(entityname))
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR

        # remove devices parameter, issue with Android
        if data.get("devices"):
            data.pop("devices")

        # get the size and location
        if data.get("version"):
            for firmware in document["ft900"]["firmware"]:
                if firmware["version"] == data["version"]:
                    data["size"]     = firmware["size"]
                    data["location"] = firmware["location"]
                    data["version"]  = firmware["version"]
                    data["checksum"] = firmware["checksum"]
                    break
        else:
            for firmware in document["ft900"]["firmware"]:
                if firmware["version"] == document["ft900"]["latest"]:
                    data["size"]     = firmware["size"]
                    data["location"] = firmware["location"]
                    data["version"]  = firmware["version"]
                    data["checksum"] = firmware["checksum"]
                    break

        # trigger device to update firmware
        response, status_return = self.messaging_requests.process(api, data)
        if status_return != 200:
            # save ota firmware update status in database
            self.database_client.set_ota_status_pending(entityname, devicename, data["version"])
            msg = {'status': 'NG', 'message': 'Device is offline. Device has been scheduled for update on device bootup.'}
            response = json.dumps(msg)
            return response


        # save ota firmware update status in database
        self.database_client.set_ota_status_ongoing(entityname, devicename, data["version"])
        #ota_status = self.database_client.get_ota_status(username, devicename)
        #print(ota_status)


        msg = {'status': 'OK', 'message': 'Upgrade Device Firmware successful.'}
        response = json.dumps(msg)
        print('\r\nUpgrade Device Firmware successful: {} {}\r\n'.format(username, devicename))
        return response


    def update_firmwares_thread(self, api, data, entityname, devicename, version):

        # trigger device to update firmware
        response, status_return = self.messaging_requests.process(api, data)
        if status_return != 200:
            self.database_client.set_ota_status_pending(entityname, devicename, version)
            print("{} {}".format(devicename, "pending"))
            return

        # save ota firmware update status in database
        self.database_client.set_ota_status_ongoing(entityname, devicename, version)
        print("{} {}".format(devicename, "ongoing"))


    ########################################################################################################
    #
    # UPDATE FIRMWARES
    #
    # - Request:
    #   POST /devices/firmware
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   data: {'version': string, 'devices': ['devicename', ...]}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def update_firmwares(self):
        api = 'beg_ota'

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Update Firmwares: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED

        # get username from token
        data = flask.request.get_json()
        data['token'] = {'access': auth_header_token}
        username = self.database_client.get_username_from_token(data['token'])
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Update Firmwares: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        data['username'] = username
        print('update_firmwares {}'.format(data['username']))


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Update Firmwares: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # check if a parameter is empty
        result, document = self.storage_client.get_device_firmware_updates()
        if not result:
            response = json.dumps({'status': 'NG', 'message': 'Could not retrieve JSON document'})
            print('\r\nERROR Update Firmwares: Could not retrieve JSON document [{}]\r\n'.format(entityname))
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR

        # get the size and location
        if data.get("version"):
            for firmware in document["ft900"]["firmware"]:
                if firmware["version"] == data["version"]:
                    data["size"]     = firmware["size"]
                    data["location"] = firmware["location"]
                    data["version"]  = firmware["version"]
                    data["checksum"] = firmware["checksum"]
                    break
        else:
            for firmware in document["ft900"]["firmware"]:
                if firmware["version"] == document["ft900"]["latest"]:
                    data["size"]     = firmware["size"]
                    data["location"] = firmware["location"]
                    data["version"]  = firmware["version"]
                    data["checksum"] = firmware["checksum"]
                    break

        #if data.get("devices"):
        #    print(data["devices"])

        device_list = self.database_client.get_devices(entityname)
        thread_list = []

        for device in device_list:
            if data.get("devices"):
                if device["devicename"] not in data["devices"]:
                    continue
            #print(device["devicename"])
            data_thr = copy.deepcopy(data)

            # remove devices parameter
            if data_thr.get("devices"):
                data_thr.pop("devices")
            data_thr["devicename"] = device["devicename"]

            thr = threading.Thread(target = self.update_firmwares_thread, args = (api, data_thr, entityname, device["devicename"], data["version"], ))
            thr.start()
            thread_list.append(thr) 

        for thr in thread_list:
            thr.join()


        msg = {'status': 'OK', 'message': 'Update Firmwares successful.'}
        response = json.dumps(msg)
        print('\r\nUpdate Firmwares successful: {}\r\n'.format(username))
        return response


    ########################################################################################################
    #
    # GET UPDATE FIRMWARE
    #
    # - Request:
    #   GET /devices/device/<devicename>/firmware
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_update_firmware(self, devicename):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get Upgrade Device Firmware: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Upgrade Device Firmware: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED

        print('get_update_firmware {} devicename={}'.format(username, devicename))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0 or len(devicename) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get Upgrade Device Firmware: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Upgrade Device Firmware: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get Upgrade Device Firmware: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get Upgrade Device Firmware: Authorization not allowed [{}]\r\n'.format(username))
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
            print('\r\nERROR Get Upgrade Device Firmware: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND


        # check database for ota status
        ota_status = self.database_client.get_ota_status(entityname, devicename)
        if ota_status is None:
            response = json.dumps({'status': 'NG', 'message': 'OTA not started'})
            print('\r\nERROR Get Upgrade Device Firmware: OTA not started\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        result = "ongoing"
        if ota_status["status"] != "ongoing":
            result = ota_status["status"]
            print(ota_status)


        msg = {'status': 'OK', 'message': 'Device upgrade queried successfully.', 'result': result}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nDevice upgrade queried successful: {}\r\n\r\n'.format(username))
        return response


    ########################################################################################################
    #
    # GET OTA STATUSES
    #
    # - Request:
    #   GET /devices/ota
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string. 'ota': [{"devicename": string, "deviceid", string, "version": string, "status":string, "time": string, "timestamp": int}, ...]}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_ota_statuses(self):
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

        print('get_ota_statuses {}'.format(username))

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

        devices = self.database_client.get_devices(entityname)
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
        if len(ota_statuses):
            ota_statuses.sort(key=self.sort_by_devicename)


        msg = {'status': 'OK', 'message': 'Get OTA statuses successful.', 'ota': ota_statuses}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nGet OTA statuses successful: {}\r\n\r\n'.format(username))
        return response


    ########################################################################################################
    #
    # GET OTA STATUS
    #
    # - Request:
    #   GET /devices/device/<devicename>/ota
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'ota': {"version": string, "status":string, "time": string, "timestamp": int} }
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_ota_status(self, devicename):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get OTA status: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get OTA status: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED

        print('get_ota_status {} devicename={}'.format(username, devicename))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0 or len(devicename) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get OTA status: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get OTA status: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get OTA status: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get OTA status: Authorization not allowed [{}]\r\n'.format(username))
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
            print('\r\nERROR Get OTA status: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND


        # check database for ota status
        ota_status = self.database_client.get_ota_status(entityname, devicename)
        if ota_status is None:
            ota_status = {}
            if device.get("version"):
                ota_status["version"] = device["version"]
            else:
                ota_status["version"] = "0.1"
            ota_status["status"] = "n/a"
            ota_status["time"] = "n/a"
            ota_status["timestamp"] = "n/a"
        elif ota_status.get("timestamp") and ota_status.get("timestart"):
            ota_status["time"] = "{} seconds".format(ota_status["timestamp"] - ota_status["timestart"])
            ota_status.pop("timestart")
            ota_status.pop("deviceid")


        msg = {'status': 'OK', 'message': 'Get OTA status successful.', 'ota': ota_status}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nGet OTA status successful: {}\r\n\r\n'.format(username))
        return response



    def decode_password(self, secret_key, password):

        return jwt.decode(password, secret_key, algorithms=['HS256'])

    def compute_password(self, secret_key, uuid, serial_number, mac_address, debug=False):

        if secret_key=='' or uuid=='' or serial_number=='' or mac_address=='':
            printf("secret key, uuid, serial number and mac address should not be empty!")
            return None

        params = {
            "uuid": uuid,                  # device uuid
            "serialnumber": serial_number, # device serial number
            "poemacaddress": mac_address,  # device mac address in uppercase string ex. AA:BB:CC:DD:EE:FF
        }
        password = jwt.encode(params, secret_key, algorithm='HS256')

        # pyjwt returns bytes while jose returns string
        # if bytes is returned, then convert to string
        if type(password) == bytes:
            password = password.decode("utf-8")

        if debug:
            print("")
            print("compute_password")
            rest_api_utils.utils().print_json(params)
            print(password)
            print("")

            payload = self.decode_password(secret_key, password)
            print("")
            print("decode_password")
            rest_api_utils.utils().print_json(payload)
            print("")

        return password


    ########################################################################################################
    #
    # DOWNLOAD FIRMWARE
    #
    # - Request:
    #   GET /firmware/<device>/<filename>
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   binary file
    #
    ########################################################################################################
    def download_firmware_file(self, device, filename):

        deviceuser, devicepass, reason = rest_api_utils.utils().get_auth_header_user_pass_ota()
        if deviceuser is None or devicepass is None:
            response = json.dumps({'status': 'NG', 'message': reason})
            print('\r\nERROR Get Device Firmware Updates: {}\r\n'.format(reason))
            return response, status.HTTP_401_UNAUTHORIZED

        file_path = "firmware/" + device + "/" + filename
        print('download_firmware_file {}'.format(file_path))

        # get the device if valid
        device = self.database_client.find_device_by_id(deviceuser)
        if device is None:
            response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
            print('\r\nERROR Get Device Firmware Updates: Device is not registered [{},{}]\r\n'.format(deviceuser, devicepass))
            return response, status.HTTP_404_NOT_FOUND

        # check if password is correct
        if device.get("poemacaddress") is None:
            # if no macaddress, password must be the serialnumber
            if devicepass != device["serialnumber"]:
                response = json.dumps({'status': 'NG', 'message': 'Invalid password'})
                print('\r\nERROR Get Device Firmware Updates: Invalid password\r\n')
                return response, status.HTTP_401_UNAUTHORIZED
        else:
            # if has macaddress, password must be the JWT(uuid, serialnumber, macaddress)
            devicepass_computed = self.compute_password(config.CONFIG_JWT_SECRET_KEY_DEVICE, device["deviceid"], device["serialnumber"], device['poemacaddress'], debug=False)
            if devicepass_computed != devicepass:
                response = json.dumps({'status': 'NG', 'message': 'Invalid password'})
                print('\r\nERROR Get Device Firmware Updates: Invalid password\r\n')
                print(deviceuser)
                print(devicepass_computed)
                print(devicepass)
                return response, status.HTTP_401_UNAUTHORIZED

        result, binary = self.storage_client.get_firmware(file_path)
        if not result:
            response = json.dumps({'status': 'NG', 'message': 'Could not retrieve JSON document'})
            print('\r\nERROR Get Device Firmware Updates: Could not retrieve JSON document\r\n')
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR

        print('download_firmware_file {} OK'.format(file_path))
        return binary

