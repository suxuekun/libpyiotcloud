import time
import hmac
import hashlib
import datetime
import random
import copy
from rest_api_config import config
from pymongo import MongoClient # MongoDB
#import psycopg2                # PostgreSQL
from cognito_client import cognito_client
from paypal_client import paypal_client
import statistics



class database_models:

    MONGODB    = 0
    AWSCOGNITO = 1
    POSTGRESQL = 2



##########################################################
# USER database   : AWS Cognito or MongoDB or PostgreSQL
# DEVICE database : MongoDB or PostgreSQL
##########################################################
class database_client:

    def __init__(self, model_users=database_models.AWSCOGNITO, model_devices=database_models.MONGODB):
        self.use_cognito = True if model_users==database_models.AWSCOGNITO else False

        # user database
        if model_users == database_models.AWSCOGNITO:
            self._users = database_client_cognito()
        elif model_users == database_models.MONGODB:
            self._users = database_client_mongodb()
        elif model_users == database_models.POSTGRESQL:
            self._users = database_client_postgresql()

        # device database
        if model_devices == database_models.MONGODB:
            self._devices = database_client_mongodb()
        elif model_devices == database_models.POSTGRESQL:
            self._devices = database_client_postgresql()

        # subscriptions database
        self._subscriptions = self._devices

        # transactions database
        self._transactions = self._devices

        # idp database
        self._idp = self._devices


    def initialize(self):
        self._users.initialize()
        self._devices.initialize()

    def is_using_cognito(self):
        return self.use_cognito



    ##########################################################
    # ota firmware update
    ##########################################################

    def set_ota_status_ongoing(self, username, devicename, version):
        self.set_ota_status(username, devicename, version, "ongoing")

    def set_ota_status_pending(self, username, devicename, version):
        self.set_ota_status(username, devicename, version, "pending")

    def set_ota_status(self, username, devicename, version, status):
        deviceid = self._devices.get_deviceid(username, devicename)
        self._devices.set_ota_status(username, deviceid, version, status)

    def set_ota_status_completed(self, username, devicename):
        deviceid = self._devices.get_deviceid(username, devicename)
        self._devices.set_ota_status_completed(deviceid)

    def set_ota_status_completed_by_deviceid(self, deviceid):
        self._devices.set_ota_status_completed(deviceid)


    def get_ota_statuses(self, username):
        return self._devices.get_ota_statuses(username)

    def get_ota_status(self, username, devicename):
        deviceid = self._devices.get_deviceid(username, devicename)
        return self._devices.get_ota_status(deviceid)

    def get_ota_status_by_deviceid(self, deviceid):
        return self._devices.get_ota_status(deviceid)


    def delete_ota_statuses(self, username):
        self._devices.delete_ota_statuses(username)


    ##########################################################
    # transactions
    ##########################################################

    def record_paypal_payment(self, username, payment_result, credits, prevcredits, newcredits):
        return self._transactions.record_paypal_payment(username, payment_result, credits, prevcredits, newcredits)

    def get_paypal_payments(self, username):
        return self._transactions.get_paypal_payments(username)

    def get_paypal_payment(self, username, payment_id):
        return self._transactions.get_paypal_payment(username, payment_id)

    def get_paypal_payment_by_transaction_id(self, username, transaction_id):
        return self._transactions.get_paypal_payment_by_transaction_id(username, transaction_id)

    def get_paypal_payment_by_paymentid(self, payment_id):
        return self._transactions.get_paypal_payment_by_paymentid(payment_id)



    def paypal_set_payerid(self, payment_id, payer_id):
        self._transactions.paypal_set_payerid(payment_id, payer_id)

    def paypal_get_payerid(self, payment_id):
        return self._transactions.paypal_get_payerid(payment_id)


    def transactions_paypal_set_payment(self, username, token, payment):
        return self._transactions.paypal_set_payment(username, token, payment)

    def transactions_paypal_execute_payment(self, username, payment):
        return self._transactions.paypal_execute_payment(username, payment)

    def transactions_paypal_verify_payment(self, username, payment):
        return self._transactions.paypal_verify_payment(username, payment)

    def transactions_paypal_get_payment(self, username, payment):
        return self._transactions.paypal_get_payment(username, payment)


    ##########################################################
    # subscriptions
    ##########################################################

    def get_subscription(self, username):
        return self._subscriptions.get_subscription(username)

    def set_subscription(self, username, credits):
        return self._subscriptions.set_subscription(username, credits)


    ##########################################################
    # idp token
    ##########################################################

    def get_idp_token(self, id):
        return self._idp.get_idp_token(id)

    def set_idp_token(self, id, token):
        self._idp.set_idp_token(id, token)

    def delete_idp_token(self, id):
        self._idp.delete_idp_token(id)


    def get_idp_code(self, id):
        return self._idp.get_idp_code(id)

    def set_idp_code(self, id, code):
        self._idp.set_idp_code(id, code)

    def delete_idp_code(self, id):
        self._idp.delete_idp_code(id)


    ##########################################################
    # users
    ##########################################################

    def get_cognito_client_id(self):
        return self._users.get_cognito_client_id()

    def get_registered_users(self):
        return self._users.get_registered_users()

    def find_user(self, username):
        return self._users.find_user(username)

    def get_username_by_phonenumber(self, phone_number):
        return self._users.get_username_by_phonenumber(phone_number)

    # find email should be avoided as several users can have the same email
    # due to the support for login via social accounts (Facebook, Google, Amazon)
    def find_email(self, email):
        return self._users.find_email(email)

    # if login via social account, it shall be treated as verified email
    def is_email_verified(self, username):
        return self._users.is_email_verified(username)

    def get_user_info(self, access_token):
        return self._users.get_user_info(access_token)

    def delete_user(self, username, access_token):
        return self._users.delete_user(username, access_token)

    def admin_delete_user(self, username):
        return self._users.admin_delete_user(username)

    def login(self, username, password):
        return self._users.login(username, password)

    def login_mfa(self, username, sessionkey, mfacode):
        return self._users.login_mfa(username, sessionkey, mfacode)

    def logout(self, token):
        return self._users.logout(token)

    def verify_token(self, username, token):
        return self._users.verify_token(username, token)

    def refresh_token(self, token):
        return self._users.refresh_token(token)

    def get_username_from_token(self, token):
        return self._users.get_username_from_token(token)

    def add_user(self, username, password, email, phonenumber, givenname, familyname):
        return self._users.add_user(username, password, email, phonenumber, givenname, familyname)

    def update_user(self, access_token, phonenumber, givenname, familyname):
        return self._users.update_user(access_token, phonenumber, givenname, familyname)

    def confirm_user(self, username, confirmationcode):
        return self._users.confirm_user(username, confirmationcode)

    def get_confirmationcode(self, username):
        return self._users.get_confirmationcode(username)

    def resend_confirmationcode(self, username):
        return self._users.resend_confirmationcode(username)

    def forgot_password(self, username):
        return self._users.forgot_password(username)

    def confirm_forgot_password(self, username, confirmation_code, new_password):
        return self._users.confirm_forgot_password(username, confirmation_code, new_password)

    def get_user_group(self, username):
        return self._users.get_user_group(username)

    def add_user_to_group(self, username):
        return self._users.add_user_to_group(username)

    def remove_user_from_group(self, username):
        return self._users.remove_user_from_group(username)

    def request_verify_phone_number(self, access_token):
        return self._users.request_verify_phone_number(access_token)

    def confirm_verify_phone_number(self, access_token, confirmation_code):
        return self._users.confirm_verify_phone_number(access_token, confirmation_code)

    def change_password(self, access_token, password, new_password):
        return self._users.change_password(access_token, password, new_password)

    def reset_user_password(self, username):
        return self._users.reset_user_password(username)

    def enable_mfa(self, access_token, enable):
        return self._users.enable_mfa(access_token, enable)

    def admin_enable_mfa(self, username, enable):
        return self._users.admin_enable_mfa(username, enable)

    def admin_link_provider_for_user(self, username, email, provider):
        return self._users.admin_link_provider_for_user(username, email, provider)

    def admin_disable_provider_for_user(self, username, provider):
        return self._users.admin_disable_provider_for_user(username, provider)


    ##########################################################
    # history
    ##########################################################

    def add_device_history(self, deviceid, topic, payload, direction):
        self._devices.add_device_history(deviceid, topic, payload, direction)

    def get_device_history(self, deviceid):
        return self._devices.get_device_history(deviceid)

    def delete_device_history(self, deviceid):
        return self._devices.delete_device_history(deviceid)

    def sort_by_timestamp(self, elem):
        return elem['timestamp']

    def sort_by_devicename(self, elem):
        return elem['devicename']

    def sort_by_groupname(self, elem):
        return elem['groupname']

    def get_user_history(self, username):
        user_histories = []
        devices = self._devices.get_registered_devices()
        if devices and devices.count():
            for device in devices.find({'username': username}):
                histories = self._devices.get_device_history(device["deviceid"])
                #print(histories)
                #for history in histories:
                #    history['timestamp'] = datetime.datetime.fromtimestamp(int(history['timestamp'])).strftime('%Y-%m-%d %H:%M:%S')
                if histories and len(histories) > 0:
                    user_histories += histories
        user_histories.sort(key=self.sort_by_timestamp, reverse=True)
        return user_histories

    def get_user_history_filtered(self, username, devicename, direction, topic, datebegin, dateend):
        filter_devices = {'username': username}
        if devicename is not None:
            filter_devices['deviceid'] = self._devices.get_deviceid(username, devicename)

        filter = {}
        if topic is not None:
            filter['topic'] = topic
        if direction is not None:
            filter['direction'] = direction
        if datebegin != 0 and dateend != 0:
            filter['timestamp'] = {'$gte': datebegin, '$lte': dateend}
        elif datebegin != 0:
            filter['timestamp'] = {"$gte": datebegin}
        #print(filter)

        user_histories = []
        devices = self._devices.get_registered_devices()
        if devices and devices.count():
            for device in devices.find(filter_devices):
                filter['deviceid'] = device['deviceid']
                histories = self._devices.get_device_history_filter(filter)
                #for history in histories:
                #    #print(history['timestamp'])
                #    #history['timestamp'] = datetime.datetime.fromtimestamp(int(history['timestamp'])).strftime('%Y-%m-%d %H:%M:%S')
                #    user_histories.append(history)
                user_histories += histories
                #print(len(histories))
        #print(len(user_histories))

        user_histories.sort(key=self.sort_by_timestamp, reverse=True)
        return user_histories


    ##########################################################
    # menos
    ##########################################################

    def add_menos_transaction(self, deviceid, recipient, message, type, source, sensorname, timestamp, condition, result):
        self._devices.add_menos_transaction(deviceid, recipient, message, type, source, sensorname, timestamp, condition, result)

    def delete_menos_transaction(self, deviceid):
        self._devices.delete_menos_transaction(deviceid)

    def get_menos_transaction(self, deviceid):
        return self._devices.get_menos_transaction(deviceid)

    def get_menos_transaction_filtered(self, deviceid, type, source, datebegin, dateend):
        return self._devices.get_menos_transaction_filtered(deviceid, type, source, datebegin, dateend)


    ##########################################################
    # notifications
    ##########################################################

    def update_device_notification(self, username, devicename, source, notification):
        deviceid = self._devices.get_deviceid(username, devicename)
        return self._devices.update_device_notification(deviceid, source, notification)

    def update_device_notification_with_notification_subclass(self, username, devicename, source, notification, notification_subclass):
        deviceid = self._devices.get_deviceid(username, devicename)
        return self._devices.update_device_notification_with_notification_subclass(deviceid, source, notification, notification_subclass)

    def delete_device_notification_sensor(self, username, devicename, source):
        deviceid = self._devices.get_deviceid(username, devicename)
        return self._devices.delete_device_notification_sensor(deviceid, source)

    def delete_device_notification(self, username, devicename):
        deviceid = self._devices.get_deviceid(username, devicename)
        return self._devices.delete_device_notification(deviceid)

    def get_device_notification(self, username, devicename, source):
        deviceid = self._devices.get_deviceid(username, devicename)
        return self._devices.get_device_notification(deviceid, source)

    def get_device_notification_with_notification_subclass(self, username, devicename, source):
        deviceid = self._devices.get_deviceid(username, devicename)
        return self._devices.get_device_notification_with_notification_subclass(deviceid, source)

    def get_device_notification_with_notification_subclass_by_deviceid(self, deviceid, source):
        return self._devices.get_device_notification_with_notification_subclass_by_deviceid(deviceid, source)

    def get_device_notification_by_deviceid(self, deviceid, source):
        return self._devices.get_device_notification_by_deviceid(deviceid, source)


    ##########################################################
    # configurations
    ##########################################################

    def update_device_peripheral_configuration(self, username, devicename, source, number, address, classid, subclassid, properties):
        return self._devices.update_device_peripheral_configuration(self._devices.get_deviceid(username, devicename), source, number, address, classid, subclassid, properties)

    def delete_device_peripheral_configuration(self, username, devicename, source, number, address):
        return self._devices.delete_device_peripheral_configuration(self._devices.get_deviceid(username, devicename), source, number, address)

    def delete_all_device_peripheral_configuration(self, username, devicename):
        return self._devices.delete_all_device_peripheral_configuration(self._devices.get_deviceid(username, devicename))

    def get_device_peripheral_configuration_by_deviceid(self, deviceid, source, number, address):
        return self._devices.get_device_peripheral_configuration(deviceid, source, number, address)

    def get_device_peripheral_configuration(self, username, devicename, source, number, address):
        return self._devices.get_device_peripheral_configuration(self._devices.get_deviceid(username, devicename), source, number, address)

    def get_all_device_peripheral_configuration(self, deviceid):
        return self._devices.get_all_device_peripheral_configuration(deviceid)

    def set_enable_device_peripheral_configuration(self, username, devicename, source, number, address, enabled):
        self._devices.set_enable_device_peripheral_configuration(self._devices.get_deviceid(username, devicename), source, number, address, enabled)


    ##########################################################
    # sensors
    ##########################################################

    def get_user_sensors_input(self, username):
        return self._devices.get_user_sensors_input(username)

    def get_all_device_sensors_by_deviceid(self, deviceid):
        return self._devices.get_all_device_sensors(deviceid)

    def get_all_device_sensors_enabled_input(self, username, devicename, source=None, number=None, sensorclass=None, sensorstatus=1, type="input"):
        return self._devices.get_all_device_sensors_enabled_input(self._devices.get_deviceid(username, devicename), source, number, sensorclass, sensorstatus, type)

    def get_all_device_sensors_by_deviceid(self, deviceid):
        return self._devices.get_all_device_sensors(deviceid)

    def get_all_device_sensors(self, username, devicename):
        return self._devices.get_all_device_sensors(self._devices.get_deviceid(username, devicename))

    def get_all_device_sensors_input_by_deviceid(self, deviceid):
        return self._devices.get_all_device_sensors_input(deviceid)

    def get_all_device_sensors_input(self, username, devicename):
        return self._devices.get_all_device_sensors_input(self._devices.get_deviceid(username, devicename))

    def get_all_sensors(self, username, devicename, source):
        return self._devices.get_all_sensors(self._devices.get_deviceid(username, devicename), source)

    def get_all_type_sensors(self, username, devicename, source, type):
        return self._devices.get_all_type_sensors(self._devices.get_deviceid(username, devicename), source, type)

    def get_sensors(self, username, devicename, source, number):
        return self._devices.get_sensors(self._devices.get_deviceid(username, devicename), source, number)

    def get_sensors_count(self, username, devicename, source, number):
        return len(self._devices.get_sensors(self._devices.get_deviceid(username, devicename), source, number))

    def get_sensors_enabled_input(self, username, devicename, source, number):
        return self._devices.get_sensors_enabled_input(self._devices.get_deviceid(username, devicename), source, number)

    def get_sensors_with_enabled(self, username, devicename, source, number):
        return self._devices.get_sensors_with_enabled(self._devices.get_deviceid(username, devicename), source, number)

    def add_sensor(self, username, devicename, source, number, sensorname, data):
        return self._devices.add_sensor(self._devices.get_deviceid(username, devicename), source, number, sensorname, data)

    def add_sensor_by_deviceid(self, deviceid, source, number, sensorname, data):
        return self._devices.add_sensor(deviceid, source, number, sensorname, data)

    def delete_device_sensors(self, username, devicename):
        self._devices.delete_device_sensors(self._devices.get_deviceid(username, devicename))

    def delete_device_sensor(self, username, devicename, sensorname):
        self._devices.delete_device_sensor(username, devicename, sensorname)

    def delete_sensor(self, username, devicename, source, number, sensorname):
        self._devices.delete_sensor(self._devices.get_deviceid(username, devicename), source, number, sensorname)

    def check_sensor(self, username, devicename, sensorname):
        return self._devices.check_sensor(self._devices.get_deviceid(username, devicename), sensorname)

    def check_sensor_by_deviceid(self, deviceid, sensorname):
        return self._devices.check_sensor(deviceid, sensorname)

    def get_sensor(self, username, devicename, source, number, sensorname):
        return self._devices.get_sensor(self._devices.get_deviceid(username, devicename), source, number, sensorname)

    def get_sensor_by_address(self, username, devicename, source, number, address):
        return self._devices.get_sensor_by_address(self._devices.get_deviceid(username, devicename), source, number, address)

    def disable_unconfigure_sensors(self, username, devicename):
        self._devices.disable_unconfigure_sensors(self._devices.get_deviceid(username, devicename))

    def disable_unconfigure_sensors_source(self, username, devicename, source, number):
        self._devices.disable_unconfigure_sensors_source(self._devices.get_deviceid(username, devicename), source, number)

    def set_enable_configure_sensor(self, username, devicename, source, number, sensorname, enabled, configured):
        self._devices.set_enable_configure_sensor(self._devices.get_deviceid(username, devicename), source, number, sensorname, enabled, configured)


    ##########################################################
    # sensor readings
    ##########################################################

    def add_sensor_reading(self, username, deviceid, source, address, sensor_readings):
        self._devices.update_sensor_reading(username, deviceid, source, address, sensor_readings)

    def delete_sensor_reading(self, username, devicename, source, address):
        deviceid = self._devices.get_deviceid(username, devicename)
        self._devices.delete_sensor_reading(deviceid, source, address)
        self._devices.delete_sensor_reading_dataset(deviceid, source, address)

    def delete_sensors_readings(self, username, devicename, source):
        deviceid = self._devices.get_deviceid(username, devicename)
        self._devices.delete_sensors_readings(deviceid, source)
        self._devices.delete_sensors_readings_dataset(deviceid, source)

    def delete_device_sensor_reading(self, username, devicename):
        deviceid = self._devices.get_deviceid(username, devicename)
        self._devices.delete_device_sensor_reading(deviceid)
        self._devices.delete_device_sensor_reading_dataset(deviceid)

    def delete_user_sensor_reading(self, username):
        self._devices.delete_user_sensor_reading(username)
        self._devices.delete_user_sensor_reading_dataset(username)

    def get_sensor_reading(self, username, devicename, source, address):
        return self._devices.get_sensor_reading_by_deviceid(self._devices.get_deviceid(username, devicename), source, address)

    def get_sensors_readings(self, username, devicename, source):
        return self._devices.get_sensors_readings_by_deviceid(self._devices.get_deviceid(username, devicename), source)

    def get_device_sensors_readings(self, username, devicename):
        return self._devices.get_device_sensors_readings_by_deviceid(self._devices.get_deviceid(username, devicename))

    def get_user_sensors_readings(self, username):
        return self._devices.get_user_sensors_readings(username)

    def get_sensor_reading_by_deviceid(self, deviceid, source, address):
        return self._devices.get_sensor_reading_by_deviceid(deviceid, source, address)

    # sensor readings datasets

    def add_sensor_reading_dataset(self, username, deviceid, source, address, value, subclass_value):
        self._devices.add_sensor_reading_dataset(username, deviceid, source, address, value, subclass_value)

    def get_sensor_reading_dataset(self, username, devicename, source, address):
        return self._devices.get_sensor_reading_dataset_by_deviceid(self._devices.get_deviceid(username, devicename), source, address)

    def get_sensor_reading_dataset_timebound(self, username, devicename, source, address, datebegin, dateend, period, maxpoints):
        return self._devices.get_sensor_reading_dataset_by_deviceid_timebound(self._devices.get_deviceid(username, devicename), source, address, datebegin, dateend, period, maxpoints)


    ##########################################################
    # mobile
    ##########################################################

    def add_mobile_device_token(self, username, devicetoken, service, accesstoken):
        self._devices.add_mobile_device_token(username, devicetoken, service, accesstoken)

    def update_mobile_device_token(self, accesstoken, new_accesstoken):
        self._devices.update_mobile_device_token(accesstoken, new_accesstoken)

    def delete_mobile_device_token(self, username, accesstoken):
        self._devices.delete_mobile_device_token(username, accesstoken)

    def delete_all_mobile_device_token(self, username):
        self._devices.delete_all_mobile_device_token(username)

    def get_mobile_device_token(self, username, accesstoken):
        return self._devices.get_mobile_device_token(username, accesstoken)

    def get_all_mobile_device_token(self, username):
        return self._devices.get_all_mobile_device_token(username)


    ##########################################################
    # device locaton
    ##########################################################

    def add_device_location(self, username, devicename, location):
        deviceid = self._devices.get_deviceid(username, devicename)
        self._devices.add_device_location(username, deviceid, location)

    def get_device_location(self, username, devicename):
        deviceid = self._devices.get_deviceid(username, devicename)
        return self._devices.get_device_location(deviceid)

    def get_devices_location(self, username):
        return self._devices.get_devices_location(username)

    def delete_device_location(self, username, devicename):
        deviceid = self._devices.get_deviceid(username, devicename)
        self._devices.delete_device_location(deviceid)

    def delete_devices_location(self, username):
        self._devices.delete_devices_location(username)


    ##########################################################
    # devices
    ##########################################################

    def display_devices(self, username):
        self._devices.display_devices(username)

    def get_registered_devices(self):
        return self._devices.get_registered_devices()

    def get_devices(self, username):
        return self._devices.get_devices(username)

    def get_devicenames(self, username):
        return self._devices.get_devicenames(username)

    def get_devices_with_filter(self, username, filter):
        return self._devices.get_devices_with_filter(username, filter)

    def add_device(self, username, devicename, uuid, serialnumber):
        # todo: verify uuid and serialnumber matches
        return self._devices.add_device(username, devicename, uuid, serialnumber)

    def delete_device(self, username, devicename):
        self._devices.delete_device(username, devicename)

    def find_device(self, username, devicename):
        return self._devices.find_device(username, devicename)

    def find_device_by_id(self, deviceid):
        return self._devices.find_device_by_id(deviceid)

    def get_device_cached_values(self, username, devicename):
        return self._devices.get_device_cached_values(username, devicename)

    def get_deviceid(self, username, devicename):
        return self._devices.get_deviceid(username, devicename)

    def add_device_heartbeat(self, deviceid):
        return self._devices.add_device_heartbeat(deviceid)

    def save_device_version(self, username, devicename, version):
        return self._devices.save_device_version(username, devicename, version)

    def update_devicename(self, username, devicename, new_devicename):
        self._devices.update_devicename(username, devicename, new_devicename)


    ##########################################################
    # devicegroups
    ##########################################################

    def add_devicegroup(self, username, groupname):
        self._devices.add_devicegroup(username, groupname)

    def delete_devicegroup(self, username, groupname):
        self._devices.delete_devicegroup(username, groupname)

    def get_devicegroup(self, username, groupname):
        return self._devices.get_devicegroup(username, groupname)

    def get_devicegroups(self, username):
        return self._devices.get_devicegroups(username)

    def add_device_to_devicegroup(self, username, groupname, devicename):
        return self._devices.add_device_to_devicegroup(username, groupname, devicename)

    def remove_device_from_devicegroup(self, username, groupname, devicename):
        self._devices.remove_device_from_devicegroup(username, groupname, devicename)

    def set_devices_to_devicegroup(self, username, groupname, devices):
        self._devices.set_devices_to_devicegroup(username, groupname, devices)

    def update_name_devicegroup(self, username, groupname, new_groupname):
        self._devices.update_name_devicegroup(username, groupname, new_groupname)


class database_utils:

    def __init__(self):
        pass

    def compute_token(self, timestamp, username, password, email, givenname, familyname):
        key = timestamp.encode('utf-8')
        message = (username + password + email + givenname + familyname).encode('utf-8')
        token = hmac.new(key, message, hashlib.sha1).hexdigest()
        return token

    def compute_deviceid(self, timestamp, username, devicename):
        key = timestamp.encode('utf-8')
        message = (username + devicename).encode('utf-8')
        deviceid = hmac.new(key, message, hashlib.sha1).hexdigest()
        return deviceid


class database_client_cognito:

    def __init__(self):
        self.client = None

    def initialize(self):
        self.client = cognito_client()


    ##########################################################
    # users
    ##########################################################

    def get_cognito_client_id(self):
        return self.client.get_cognito_client_id()

    def get_registered_users(self):
        (result, users) = self.client.admin_list_users()
        if not result:
            return None
        return users

    def find_user(self, username):
        (result, users) = self.client.admin_list_users()
        if result == False:
            return True
        if users:
            for user in users:
                if user["username"] == username:
                    return True
        return False

    def get_username_by_phonenumber(self, phone_number):
        (result, users) = self.client.admin_list_users()
        if result == False:
            return None
        if users:
            for user in users:
                if user.get("phone_number"):
                    # phone number must be verified
                    if user["phone_number"] == phone_number:
                        if user["phone_number_verified"]:
                            return user["username"]
        return None

    def is_email_verified(self, username):
        (result, users) = self.client.admin_list_users()
        if result == False:
            return True
        if users:
            for user in users:
                if user["username"] == username:
                    # if login via social account, status is EXTERNAL_PROVIDER
                    # EXTERNAL_PROVIDER shall be treated as verified email
                    if user["status"]=="CONFIRMED":
                        return True
                    elif user["status"]=="EXTERNAL_PROVIDER":
                        return True
                    break
        return False

    def find_email(self, email):
        (result, users) = self.client.admin_list_users()
        if result == False:
            return None
        if users:
            for user in users:
                if user["email"] == email:
                    return user["username"]
        return None

    def get_user_info(self, access_token):
        (result, users) = self.client.get_user(access_token)
        if result == False:
            return None
        #print(users)
        return users

    def delete_user(self, username, access_token):
        (result, response) = self.client.delete_user(username, access_token)
        return result

    def admin_delete_user(self, username):
        (result, response) = self.client.admin_delete_user(username)
        return result

    def login(self, username, password):
        (result, response) = self.client.login(username, password)
        if not result:
            return None, None, response
        if response.get('AuthenticationResult'):
            access_token = response['AuthenticationResult']['AccessToken']
            refresh_token = response['AuthenticationResult']['RefreshToken']
            id_token = response['AuthenticationResult']['IdToken']
        else:
            if response.get('ChallengeName'):
                #print(response)
                if response['ChallengeName'] == 'SMS_MFA':
                    refresh_token = response['Session']
                    id_token = 'MFARequiredException'
                    return None, refresh_token, id_token
            return None, None, None
        return access_token, refresh_token, id_token

    def login_mfa(self, username, sessionkey, mfacode):
        (result, response) = self.client.login_mfa(username, sessionkey, mfacode)
        if not result:
            return None, None, None
        access_token = response['AuthenticationResult']['AccessToken']
        refresh_token = response['AuthenticationResult']['RefreshToken']
        id_token = response['AuthenticationResult']['IdToken']
        return access_token, refresh_token, id_token

    def logout(self, token):
        (result, response) = self.client.logout(token)
        #print("cognito logout = {}".format(result))

    def refresh_token(self, token):
        (result, response) = self.client.refresh_token(token['refresh'])
        if result:
            new_token = {}
            new_token['access'] = response['AuthenticationResult']['AccessToken']
            new_token['refresh'] = token['refresh']
            new_token['id'] = response['AuthenticationResult']['IdToken']
            #print("Token refreshed! {} {}".format(result, response))
            return new_token
        else:
            print("Token refreshed ERROR!\r\n")
            # during stress test, it was found that refresh token fails for some reason
            # when it fails, try to call admin refresh token
            (result, response) = self.client.admin_refresh_token(token['refresh'])
            if result:
                new_token = {}
                new_token['access'] = response['AuthenticationResult']['AccessToken']
                new_token['refresh'] = token['refresh']
                new_token['id'] = response['AuthenticationResult']['IdToken']
                #print("Admin token refreshed! {} {}".format(result, response))
                return new_token
            else:
                print("Admin token refreshed ERROR!\r\n")
        return None

    def verify_token(self, username, token):
        result = self.client.verify_token(token['access'], username)
        if result == 2 and token.get("refresh"): # token expired
            print("Token expired!")
            (result2, response) = self.client.refresh_token(token['refresh'])
            if result2:
                new_token = {}
                new_token['access'] = response['AuthenticationResult']['AccessToken']
                new_token['refresh'] = token['refresh']
                new_token['id'] = response['AuthenticationResult']['IdToken']
                print("Token refreshed! {} {}".format(result, response))
                return 0, new_token
        elif result == 2: # fail or unexpected error
            return result, None
        elif result != 0: # fail or unexpected error
            print("Unexpected error! {}".format(result))
            return result, None
        return result, None

    def get_username_from_token(self, token):
        try:
            return self.client.get_username_from_token(token['access'])
        except:
            return None

    def get_confirmationcode(self, username):
        return None

    def resend_confirmationcode(self, username):
        (result, response) = self.client.resend_confirmation_code(username)
        return result

    def add_user(self, username, password, email, phonenumber, givenname, familyname):
        if phonenumber is None:
            (result, response) = self.client.sign_up(username, password, email=email, given_name=givenname, family_name=familyname)
        else:
            (result, response) = self.client.sign_up(username, password, email=email, phone_number=phonenumber, given_name=givenname, family_name=familyname)
        return result

    def update_user(self, access_token, phonenumber, givenname, familyname):
        if phonenumber is None:
            (result, response) = self.client.update_user(access_token, given_name=givenname, family_name=familyname)
        else:
            (result, response) = self.client.update_user(access_token, phone_number=phonenumber, given_name=givenname, family_name=familyname)
        return result

    def confirm_user(self, username, confirmationcode):
        (result, response) = self.client.confirm_sign_up(username, confirmationcode)
        return result

    def forgot_password(self, username):
        (result, response) = self.client.forgot_password(username)
        return result

    def confirm_forgot_password(self, username, confirmation_code, new_password):
        (result, response) = self.client.confirm_forgot_password(username, confirmation_code, new_password)
        return result

    def get_user_group(self, username):
        val = self.client.admin_list_groups_for_user(username)
        #print(val[1])
        return val[1]

    def add_user_to_group(self, username):
        groupname = 'PaidSubscribers'
        val = self.client.admin_add_user_to_group(username, groupname)
        val = self.client.admin_list_groups_for_user(username)
        #print(val[1])
        return val[1]

    def remove_user_from_group(self, username):
        groupname = 'PaidSubscribers'
        val = self.client.admin_remove_user_from_group(username, groupname)
        val = self.client.admin_list_groups_for_user(username)
        #print(val[1])
        return val[1]

    def request_verify_phone_number(self, access_token):
        (result, response) = self.client.request_verify_phone_number(access_token)
        return result

    def confirm_verify_phone_number(self, access_token, confirmation_code):
        (result, response) = self.client.confirm_verify_phone_number(access_token, confirmation_code)
        return result

    def change_password(self, access_token, password, new_password):
        (result, response) = self.client.change_password(access_token, password, new_password)
        return result

    def reset_user_password(self, username):
        (result, response) = self.client.admin_reset_user_password(username)
        return result

    def enable_mfa(self, access_token, enable):
        (result, response) = self.client.enable_mfa(access_token, enable)
        return result

    def admin_enable_mfa(self, username, enable):
        (result, response) = self.client.admin_enable_mfa(username, enable)
        return result

    def admin_link_provider_for_user(self, username, email, provider):
        (result, response) = self.client.admin_link_provider_for_user(username, email, provider)
        return result

    def admin_disable_provider_for_user(self, username, provider):
        (result, response) = self.client.admin_disable_provider_for_user(username, provider)
        return result


class database_client_mongodb:

    def __init__(self):
        self.client = None

    def initialize(self):
        #mongo_client = MongoClient(config.CONFIG_MONGODB_HOST, config.CONFIG_MONGODB_PORT, username=config.CONFIG_MONGODB_USERNAME, password=config.CONFIG_MONGODB_PASSWORD)
        mongo_client = MongoClient(config.CONFIG_MONGODB_HOST, config.CONFIG_MONGODB_PORT)
        self.client = mongo_client[config.CONFIG_MONGODB_DB]

        # different database for sensor dashboarding
        if "mongodb.net" in config.CONFIG_MONGODB_HOST2: 
            connection_string = "mongodb+srv://" + config.CONFIG_MONGODB_USERNAME + ":" + config.CONFIG_MONGODB_PASSWORD + "@" + config.CONFIG_MONGODB_HOST2 + "/" + config.CONFIG_MONGODB_DB + "?retryWrites=true&w=majority"
            mongo_client_sensor = MongoClient(connection_string)
            self.client_sensor = mongo_client_sensor[config.CONFIG_MONGODB_DB]
        else:
            self.client_sensor = self.client

        self.paypal = paypal_client()
        self.paypal.initialize()


    ##########################################################
    # ota firmware update
    ##########################################################

    def get_otaupdates_db(self):
        return self.client[config.CONFIG_MONGODB_TB_OTAUPDATES]

    def set_ota_status(self, username, deviceid, version, status):
        otaupdates = self.get_otaupdates_db();
        item = {}
        item['username'] = username
        item['deviceid'] = deviceid
        item['status']   = status
        item['version']  = version
        if status == "ongoing":
            item['timestart'] = int(time.time())
            item['timestamp'] = item['timestart']
        found = otaupdates.find_one({'deviceid': deviceid})
        if found is None:
            otaupdates.insert_one(item)
        else:
            #print("set_ota_status {}".format(status))
            #print(item)
            otaupdates.replace_one({'deviceid': deviceid}, item)
        return item

    def set_ota_status_completed(self, deviceid):
        otaupdates = self.get_otaupdates_db();
        item = {}
        item['deviceid'] = deviceid
        item['status']   = "completed"
        item['timestamp']  = int(time.time())
        found = otaupdates.find_one({'deviceid': deviceid})
        if found is None:
            #print("set_ota_status_completed xxx")
            #print(found)
            otaupdates.insert_one(item)
        else:
            #print("set_ota_status_completed")
            #print(found)
            item['username'] = found["username"]
            item['version'] = found["version"]
            item['timestart'] = found["timestart"]
            otaupdates.replace_one({'deviceid': deviceid}, item)
        return item


    def get_ota_status(self, deviceid):
        otaupdates = self.get_otaupdates_db();
        if otaupdates:
            for otaupdate in otaupdates.find({'deviceid': deviceid}):
                otaupdate.pop('_id')
                otaupdate.pop('username')
                return otaupdate
        return None

    def get_ota_statuses(self, username):
        otaupdates_list = []
        otaupdates = self.get_otaupdates_db();
        if otaupdates:
            for otaupdate in otaupdates.find({'username': username}):
                otaupdate.pop('_id')
                otaupdate.pop('username')
                otaupdates_list.append(otaupdate)
        return otaupdates_list

    def delete_ota_statuses(self, username):
        otaupdates = self.get_otaupdates_db()
        try:
            otaupdates.delete_many({'username': username})
        except:
            pass


    ##########################################################
    # transactions
    ##########################################################

    def get_paymentpayerid_db(self):
        return self.client[config.CONFIG_MONGODB_TB_PAYMENTPAYERIDS]

    def paypal_set_payerid(self, payment_id, payer_id):
        payerids = self.get_paymentpayerid_db()
        item = {}
        item['payment_id']     = payment_id
        item['payer_id']       = payer_id
        payerids.insert_one(item)

    def paypal_get_payerid(self, payment_id):
        payer = None
        payerids = self.get_paymentpayerid_db()
        if payerids:
            for payerid in payerids.find({'payment_id': payment_id}):
                payer = payerid["payer_id"]
                try:
                    payerids.delete_many({'payment_id': payment_id})
                except:
                    pass
                break
        return payer


    def get_paymenttransactions_db(self):
        return self.client[config.CONFIG_MONGODB_TB_PAYMENTTRANSACTIONS]

    def record_paypal_payment(self, username, payment_result, value, prevcredits, credits):
        transactions = self.get_paymenttransactions_db()
        item = {}
        item['username']       = username
        item['payment_id']     = self.paypal.get_payment_id(payment_result)
        item['payer_id']       = self.paypal.get_payer_id(payment_result)
        item['state']          = self.paypal.get_transaction_state(payment_result)

        item['id']             = self.paypal.get_transaction_id(payment_result)
        item['amount']         = self.paypal.get_transaction_amount(payment_result)
        item['value']          = value
        item['prevcredits']    = prevcredits
        item['credits']        = credits

        timestamp = self.paypal.get_transaction_time(payment_result)
        utc_time = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        item['timestamp'] = int((utc_time - datetime.datetime(1970, 1, 1)).total_seconds())

        transactions.insert_one(item)
        return item

    def get_paypal_payments(self, username):
        transactions_list = []
        transactions = self.get_paymenttransactions_db()
        if transactions:
            for transaction in transactions.find({'username': username}):
                transaction.pop('_id')
                #if isinstance(transaction['timestamp'], float)== True:
                #    transaction['timestamp'] = int(transaction['timestamp'])
                #    transactions.replace_one({'username': username, 'payment_id': transaction['payment_id']}, transaction)
                #transaction['value'] = transaction['credits']
                #if transaction.get('newcredits'):
                #    transaction['credits'] = transaction['newcredits']
                #    transaction.pop('newcredits')
                #else:
                #    transaction.pop('credits')
                #transactions.replace_one({'username': username, 'payment_id': transaction['payment_id']}, transaction)

                transaction.pop('username')
                transaction.pop('payment_id') # paymentid should be kept secret, to be used for accessing Paypal database only for backtracking purposes
                transaction.pop('payer_id')
                transaction.pop('state')
                transactions_list.append(transaction)
        return transactions_list

    def get_paypal_payment(self, username, payment_id):
        transactions = self.get_paymenttransactions_db()
        if transactions:
            for transaction in transactions.find({'username': username, 'payment_id': payment_id}):
                transaction.pop('_id')
                transaction.pop('username')
                transaction.pop('payment_id') # paymentid should be kept secret, to be used for accessing Paypal database only for backtracking purposes
                transaction.pop('payer_id')
                transaction.pop('state')
                return transaction
        return None

    def get_paypal_payment_by_paymentid(self, payment_id):
        transactions = self.get_paymenttransactions_db()
        if transactions:
            for transaction in transactions.find({'payment_id': payment_id}):
                transaction.pop('_id')
                transaction.pop('payment_id') # paymentid should be kept secret, to be used for accessing Paypal database only for backtracking purposes
                transaction.pop('state')
                return transaction
        return None

    def get_paypal_payment_by_transaction_id(self, username, transaction_id):
        transactions = self.get_paymenttransactions_db()
        if transactions:
            for transaction in transactions.find({'username': username, 'id': transaction_id}, {'payment_id': 1}):
                return transaction['payment_id']
        return None


    def paypal_set_payment(self, username, token, payment):
        return_url = payment['return_url']
        cancel_url = payment['cancel_url']
        item_price = payment['item_price']
        item_sku = payment['item_sku']
        item_quantity = config.CONFIG_TRANSACTION_QUANTITY
        item_currency = config.CONFIG_TRANSACTION_CURRENCY
        item_name = config.CONFIG_TRANSACTION_NAME
        item_description = config.CONFIG_TRANSACTION_DESCRIPTION

        payment_object = self.paypal.create_payment(return_url, cancel_url, item_price, item_currency, item_quantity, item_name, item_sku, item_description)
        #print(payment_object)
        (status, payment) = self.paypal.send_payment(payment_object)
        if not status:
            print("Payment creation failed! {}".format(payment.error))
            return
        approval_url = self.paypal.get_payment_link(payment)
        #print("\r\nPayment creation successful!\r\n")

        data = {
            "paymentId": payment["id"],
            "token": approval_url[approval_url.find("token=")+len("token="):],
            "create_time": payment["create_time"],
            "sku": item_sku,
        }
        #print(data)
        return approval_url, data["paymentId"], data["token"]

    def paypal_execute_payment(self, username, payment):
        payment_id = payment["paymentId"]
        payer_id = payment["PayerID"]

        result = self.paypal.execute_payment(payment_id, payer_id)
        if not result:
            print("Payment failed!")
            return False, None

        payment_result = self.paypal.fetch_payment(payment_id)
        status = self.paypal.get_payment_status(payment_result)
        if status != "approved":
            print("Payment not yet completed! {}".format(status))
            return False, None

        #print("Payment completed successfully!")
        #self.paypal.display_payment_result(payment_result)
        return True, payment_result

    def paypal_verify_payment(self, username, payment):
        payment_id = payment["paymentId"]
        if not payment_id:
            return False, 0

        payment_result = self.paypal.fetch_payment(payment_id)
        if not payment_result:
            return False, 0

        status = self.paypal.get_payment_status(payment_result)
        if status != "approved":
            print("Payment not yet completed! {}".format(status))
            return False, 0

        #print("Payment completed successfully!")
        #self.paypal.display_payment_result(payment_result)

        #print("\r\ninvoice")
        #invoice = self.paypal.get_invoice(self.paypal.get_cart_id(payment_result))
        #print(invoice)

        return True, self.paypal.get_transaction_amount(payment_result)

    def paypal_get_payment(self, username, payment):
        payment_id = payment["paymentId"]
        if not payment_id:
            print("xxxx")
            return None

        payment_result = self.paypal.fetch_payment(payment_id)
        if not payment_result:
            print("xx")
            return None

        return payment_result


    ##########################################################
    # subscription
    ##########################################################

    def get_subscription_db(self):
        return self.client[config.CONFIG_MONGODB_TB_SUBSCRIPTIONS]

    def get_subscription(self, username):
        found = False
        subscriptions = self.get_subscription_db()
        if subscriptions:
            if True: # For easy reset of default type and credits
                for subscription in subscriptions.find({'username':username}):
                    found = True
                    subscription.pop('_id')
                    # change credits type from string to int for backward compatibility
                    if isinstance(subscription['credits'], str) == True:
                        #print("credits is string")
                        subscription['credits'] = int(subscription['credits'])
                        self.client.subscriptions.replace_one({'username':username}, subscription)
                    subscription.pop('username')
                    return subscription

        if not found:
            subscription = {}
            subscription['username'] = username
            subscription['type'] = config.CONFIG_SUBSCRIPTION_TYPE
            subscription['credits'] = config.CONFIG_SUBSCRIPTION_CREDITS
            self.client.subscriptions.insert_one(subscription)
            subscription.pop('_id')
            subscription.pop('username')
            return subscription

        return None, None

    def set_subscription(self, username, credits):
        subscriptions = self.get_subscription_db()
        if subscriptions:
            if True: # For easy reset of default type and credits
                for subscription in subscriptions.find({'username': username}):
                    current_amount = int(subscription['credits'])
                    new_amount = int(subscription['credits']) + int(credits)
                    #print("current_amount={} new_amount={}".format(current_amount, new_amount))
                    subscription['type'] = config.CONFIG_SUBSCRIPTION_PAID_TYPE
                    subscription['credits'] = new_amount
                    self.client.subscriptions.replace_one({'username': username}, subscription)
                    subscription.pop('_id')
                    subscription.pop('username')
                    return subscription 
        return None


    ##########################################################
    # idp token
    ##########################################################

    def get_idp_token_db(self):
        return self.client[config.CONFIG_MONGODB_TB_IDPTOKENS]

    def get_idp_token(self, id):
        idptokens = self.get_idp_token_db()
        token = None
        if idptokens:
            for idptoken in idptokens.find({'id': id}):
                token = idptoken['token']
                self.delete_idp_token(id)
                break
        return token

    def set_idp_token(self, id, token):
        idptokens = self.get_idp_token_db()
        item = {}
        item['id'] = id
        item['token'] = token
        item['timestamp'] = int(time.time())
        idptokens.insert_one(item)

    def delete_idp_token(self, id):
        idptokens = self.get_idp_token_db()
        try:
            idptokens.delete_many({'id': id})
        except:
            pass


    def get_idp_code_db(self):
        return self.client[config.CONFIG_MONGODB_TB_IDPCODES]

    def get_idp_code(self, id):
        idpcodes = self.get_idp_code_db()
        code = None
        if idpcodes:
            for idpcode in idpcodes.find({'id': id}):
                code = idpcode['code']
                self.delete_idp_code(id)
                break
        return code

    def set_idp_code(self, id, code):
        idpcodes = self.get_idp_code_db()
        item = {}
        item['id'] = id
        item['code'] = code
        item['timestamp'] = int(time.time())
        idpcodes.insert_one(item)

    def delete_idp_code(self, id):
        idpcodes = self.get_idp_code_db()
        try:
            idpcodes.delete_many({'id': id})
        except:
            pass


    ##########################################################
    # users
    ##########################################################

    def get_registered_users(self):
        return self.client[config.CONFIG_MONGODB_TB_PROFILES]

    def display_users(self):
        users = self.get_registered_users()
        if users:
            for user in users.find({},{'username': 1, 'password':1, 'token':1}):
                print(user)

    def find_user(self, username):
        users = self.get_registered_users()
        if users:
            for user in users.find({'username': username},{'username': 1}):
                return True
        return False

    def find_email(self, email):
        users = self.get_registered_users()
        if users:
            for user in users.find({'email': email},{'email': 1, 'username':1}):
                return user['username']
        return None

    def get_user_info(self, access_token):
        return None

    def login(self, username, password):
        users = self.get_registered_users()
        if users:
            for user in users.find({'username': username, 'password': password},{'username': 1, 'password':1, 'token':1}):
                return user['token']
        return None

    def logout(self, token):
        pass

    def verify_token(self, username, token):
        users = self.get_registered_users()
        if users:
            for user in users.find({'username': username, 'token': token},{'username': 1, 'token':1}):
                return 0
        return 1

    def get_confirmationcode(self, username):
        users = self.get_registered_users()
        if users:
            for user in users.find({'username': username},{'username': 1, 'confirmationcode': 1}):
                return user['confirmationcode']
        return None

    def resend_confirmationcode(self, username):
        pass

    def delete_user(self, username):
        users = self.get_registered_users()
        if users:
            myquery = { 'username': username }
            users.delete_one(myquery)

    def add_user(self, username, password, email, givenname, familyname):
        timestamp = str(int(time.time()))
        token = database_utils().compute_token(timestamp, username, password, email, givenname, familyname)
        confirmationcode = ''.join(["%s" % random.randint(0, 9) for num in range(0, 6)])
        profile = {}
        profile['username']         = username
        profile['password']         = password
        profile['email']            = email
        profile['givenname']        = givenname
        profile['familyname']       = familyname
        profile['timestamp']        = timestamp
        profile['token']            = token
        profile['status']           = "UNCONFIRMED"
        profile['confirmationcode'] = confirmationcode
        #print('post={}'.format(profile))
        self.client.profiles.insert_one(profile)
        return True

    def confirm_user(self, username, confirmationcode):
        users = self.get_registered_users()
        if users:
            for user in users.find({'username': username},{'username': 1, 'password': 1, 'email': 1, 'givenname': 1, 'familyname': 1, 'timestamp': 1, 'token': 1, 'status': 1, 'confirmationcode': 1 }):
                #print(user)
                if user['status'] == "UNCONFIRMED":
                    if user['confirmationcode'] == confirmationcode:
                        user['status'] = "CONFIRMED"
                        users.replace_one({'username': username}, user)
                        return True
                elif user['status'] == "CONFIRMED":
                    return True
        return False

    def forgot_password(self, username):
        return False

    def confirm_forgot_password(self, username, confirmation_code, new_password):
        return False


    ##########################################################
    # history
    ##########################################################

    def get_history_document(self):
        return self.client[config.CONFIG_MONGODB_TB_HISTORY]

    def add_device_history(self, deviceid, topic, payload, direction):
        history = self.get_history_document();
        timestamp = int(time.time())
        item = {}
        item['timestamp'] = timestamp
        item['direction'] = direction
        item['deviceid'] = deviceid
        item['topic'] = topic
        item['payload'] = payload
        history.insert_one(item);

    def get_device_history(self, deviceid):
        history_list = []
        histories = self.get_history_document();
        if histories:
            for history in histories.find({'deviceid': deviceid}):
                #print(history["timestamp"])
                history.pop('_id')
                history_list.append(history)
        return history_list

    def get_device_history_filter(self, filter):
        history_list = []
        histories = self.get_history_document();
        if histories:
            #if filter.get("timestamp"):
            #    print("timestampXX {}".format(filter["timestamp"]))
            for history in histories.find(filter):
                #print(history["timestamp"])
                history.pop('_id')
                history_list.append(history)
        return history_list

    def delete_device_history(self, deviceid):
        history = self.get_history_document();
        try:
            history.delete_many({'deviceid': deviceid})
            #history.delete_one({'deviceid': deviceid, 'timestamp': timestamp })
        except:
            print("delete_device_history: Exception occurred")
            pass


    ##########################################################
    # menos
    ##########################################################

    def get_menos_document(self):
        return self.client[config.CONFIG_MONGODB_TB_MENOS]

    def add_menos_transaction(self, deviceid, recipient, message, type, source, sensorname, timestamp, condition, result):
        menos = self.get_menos_document()
        item = {}
        item['deviceid'] = deviceid
        item['timestamp'] = timestamp
        item['recipient'] = recipient
        item['messagelen'] = len(message)
        item['type'] = type
        item['source'] = source
        if sensorname is not None:
            item['sensorname'] = sensorname
        if condition is not None:
            item['condition'] = condition
        item['result'] = result
        menos.insert_one(item)

    def delete_menos_transaction(self, deviceid):
        menos = self.get_menos_document()
        try:
            menos.delete_many({'deviceid': deviceid})
        except:
            print("delete_menos_transaction: Exception occurred")
            pass

    def get_menos_transaction(self, deviceid):
        menos_list = []
        menos = self.get_menos_document()
        if menos and menos.count():
            for menos_item in menos.find({'deviceid': deviceid}):
                menos_item.pop('_id')
                menos_list.append(menos_item)
        return menos_list

    def get_menos_transaction_filtered(self, deviceid, type, source, datebegin, dateend):
        menos_list = []
        menos = self.get_menos_document()
        if menos and menos.count():

            filter = {}
            filter['deviceid'] = deviceid
            if type is not None:
                filter['type'] = type
            if source is not None:
                filter['source'] = source
            if datebegin != 0 and dateend != 0:
                filter['timestamp'] = {'$gte': datebegin, '$lte': dateend}
            elif datebegin != 0:
                filter['timestamp'] = {"$gte": datebegin}

            #print(filter)

            for menos_item in menos.find(filter):
                #print(menos_item["timestamp"])
                menos_item.pop('_id')
                menos_list.append(menos_item)

        return menos_list


    ##########################################################
    # notifications
    ##########################################################

    def get_notifications_document(self):
        return self.client[config.CONFIG_MONGODB_TB_NOTIFICATIONS]

    def update_device_notification(self, deviceid, source, notification):
        notifications = self.get_notifications_document();
        item = {}
        #item['username'] = username
        #item['devicename'] = devicename
        item['deviceid'] = deviceid
        item['source'] = source
        item['notification'] = notification
        #print("update_device_notification find_one")
        found = notifications.find_one({'deviceid': deviceid, 'source': source})
        if found is None:
            print("update_device_notification insert_one")
            #print(found)
            notifications.insert_one(item)
        else:
            print("update_device_notification replace_one")
            notifications.replace_one({'deviceid': deviceid, 'source': source}, item)
        return item

    def update_device_notification_with_notification_subclass(self, deviceid, source, notification, notification_subclass):
        notifications = self.get_notifications_document();
        item = {}
        #item['username'] = username
        #item['devicename'] = devicename
        item['deviceid'] = deviceid
        item['source'] = source
        item['notification'] = notification
        item['notification_subclass'] = notification_subclass
        #print("update_device_notification_with_notification_subclass find_one")
        found = notifications.find_one({'deviceid': deviceid, 'source': source})
        if found is None:
            print("update_device_notification_with_notification_subclass insert_one")
            #print(found)
            notifications.insert_one(item)
        else:
            print("update_device_notification_with_notification_subclass replace_one")
            notifications.replace_one({'deviceid': deviceid, 'source': source}, item)
        return item

    def delete_device_notification_sensor(self, deviceid, source):
        notifications = self.get_notifications_document();
        try:
            notifications.delete_many({'deviceid': deviceid, 'source': source})
        except:
            print("delete_device_notification_sensor: Exception occurred")
            pass

    def delete_device_notification(self, deviceid):
        notifications = self.get_notifications_document();
        try:
            notifications.delete_many({'deviceid': deviceid})
        except:
            print("delete_device_notification: Exception occurred")
            pass

    def get_device_notification(self, deviceid, source):
        notifications = self.get_notifications_document();
        if notifications:
            for notification in notifications.find({'deviceid': deviceid, 'source': source}):
                notification.pop('_id')
                #print(notification['notification'])
                return notification['notification']
        return None

    def get_device_notification_with_notification_subclass(self, deviceid, source):
        notifications = self.get_notifications_document();
        if notifications:
            for notification in notifications.find({'deviceid': deviceid, 'source': source}):
                notification.pop('_id')
                #print(notification['notification'])
                if notification.get('notification_subclass'):
                    return notification['notification'], notification['notification_subclass']
                else:
                    return notification['notification'], None
        return None, None

    def get_device_notification_with_notification_subclass_by_deviceid(self, deviceid, source):
        notifications = self.get_notifications_document();
        if notifications:
            for notification in notifications.find({'deviceid': deviceid, 'source': source}):
                notification.pop('_id')
                #print(notification['notification'])
                if notification.get('notification_subclass'):
                    return notification['notification'], notification['notification_subclass']
                else:
                    return notification['notification'], None
        return None, None

    def get_device_notification_by_deviceid(self, deviceid, source):
        notifications = self.get_notifications_document();
        if notifications:
            for notification in notifications.find({'deviceid': deviceid, 'source': source}):
                notification.pop('_id')
                #print(notification['notification'])
                return notification['notification']
        return None


    ##########################################################
    # configurations
    ##########################################################

    def get_configurations_document(self):
        return self.client[config.CONFIG_MONGODB_TB_CONFIGURATIONS]

    def update_device_peripheral_configuration(self, deviceid, source, number, address, classid, subclassid, properties):
        configurations = self.get_configurations_document()
        item = {}
        item['deviceid'] = deviceid
        item['source'] = source
        item['number'] = number
        if address is not None:
            item['address'] = address
        if classid is not None:
            item['class'] = classid
        if subclassid is not None:
            item['subclass'] = subclassid
        item['attributes'] = properties
        item['enabled'] = 0

        #print("update_device_peripheral_configuration find_one")
        if address is not None:
            found = configurations.find_one({'deviceid': deviceid, 'source': source, 'number': number, 'address': address})
            if found is None:
                configurations.insert_one(item)
            else:
                configurations.replace_one({'deviceid': deviceid, 'source': source, 'number': number, 'address': address}, item)
        else:
            found = configurations.find_one({'deviceid': deviceid, 'source': source, 'number': number})
            if found is None:
                configurations.insert_one(item)
            else:
                configurations.replace_one({'deviceid': deviceid, 'source': source, 'number': number}, item)

        return item

    def delete_device_peripheral_configuration(self, deviceid, source, number, address):
        configurations = self.get_configurations_document();
        try:
            if address is not None:
                configurations.delete_many({'deviceid': deviceid, 'source': source, 'number': number, 'address': address})
            else:
                configurations.delete_many({'deviceid': deviceid, 'source': source, 'number': number})
        except:
            print("delete_device_peripheral_configuration: Exception occurred")
            pass

    def delete_all_device_peripheral_configuration(self, deviceid):
        configurations = self.get_configurations_document();
        try:
            configurations.delete_many({'deviceid': deviceid})
        except:
            print("delete_all_device_peripheral_configuration: Exception occurred")
            pass

    def get_device_peripheral_configuration(self, deviceid, source, number, address):
        configurations = self.get_configurations_document()
        if configurations:
            if address is not None:
                for configuration in configurations.find({'deviceid': deviceid, 'source': source, 'number': number, 'address': address}):
                    configuration.pop('_id')
                    return configuration
            else:
                for configuration in configurations.find({'deviceid': deviceid, 'source': source, 'number': number}):
                    configuration.pop('_id')
                    return configuration
        return None

    def get_all_device_peripheral_configuration(self, deviceid):
        configurations_list = []
        configurations = self.get_configurations_document()
        if configurations:
            for configuration in configurations.find({'deviceid': deviceid}):
                configuration.pop('_id')
                configurations_list.append(configuration)
        return configurations_list

    def set_enable_device_peripheral_configuration(self, deviceid, source, number, address, enabled):
        configurations = self.get_configurations_document()
        if configurations:
            if address is not None:
                for configuration in configurations.find({'deviceid': deviceid, 'source': source, 'number': number, 'address': address}):
                    configuration.pop('_id')
                    duplicate = copy.deepcopy(configuration)
                    duplicate['enabled'] = enabled
                    configurations.replace_one(configuration, duplicate)
                    break
            else:
                for configuration in configurations.find({'deviceid': deviceid, 'source': source, 'number': number}):
                    configuration.pop('_id')
                    duplicate = copy.deepcopy(configuration)
                    duplicate['enabled'] = enabled
                    configurations.replace_one(configuration, duplicate)
                    break


    ##########################################################
    # sensors
    ##########################################################

    def get_sensors_document(self):
        return self.client[config.CONFIG_MONGODB_TB_I2CSENSORS]

    def get_user_sensors_input(self, username):
        sensor_list = []
        i2csensors = self.get_sensors_document();
        if i2csensors:
            for i2csensor in i2csensors.find({'username': username, 'type': 'input'}):
                i2csensor.pop('_id')
                if i2csensor.get('username'):
                    i2csensor.pop('username')
                sensor_list.append(i2csensor)
        return sensor_list

    def get_all_device_sensors_enabled_input(self, deviceid, source, number, sensorclass, sensorstatus, type):
        sensor_list = []
        i2csensors = self.get_sensors_document();
        if i2csensors:
            if deviceid and source and sensorclass and sensorstatus is not None:
                #print("1 2 3 4")
                # 1, 2, 3, 4
                for i2csensor in i2csensors.find({'type': type, 'deviceid': deviceid, 'source': source, 'number': number, 'class': sensorclass, 'enabled': sensorstatus}):
                    i2csensor.pop('_id')
                    if i2csensor.get('username'):
                        i2csensor.pop('username')
                    sensor_list.append(i2csensor)
                try:
                    for i2csensor in i2csensors.find({'type': type, 'deviceid': deviceid, 'source': source, 'number': number, 'subclass': sensorclass, 'enabled': sensorstatus}):
                        i2csensor.pop('_id')
                        if i2csensor.get('username'):
                            i2csensor.pop('username')
                        sensor_list.append(i2csensor)
                except:
                    pass

            elif deviceid and source and sensorclass:
                #print("1 2 3")
                # 1, 2, 3
                for i2csensor in i2csensors.find({'type': type, 'deviceid': deviceid, 'source': source, 'number': number, 'class': sensorclass}):
                    i2csensor.pop('_id')
                    if i2csensor.get('username'):
                        i2csensor.pop('username')
                    sensor_list.append(i2csensor)
                try:
                    for i2csensor in i2csensors.find({'type': type, 'deviceid': deviceid, 'source': source, 'number': number, 'subclass': sensorclass}):
                        i2csensor.pop('_id')
                        if i2csensor.get('username'):
                            i2csensor.pop('username')
                        sensor_list.append(i2csensor)
                except:
                    pass
            elif deviceid and source and sensorstatus is not None:
                #print("1 2 4")
                # 1, 2, 4
                for i2csensor in i2csensors.find({'type': type, 'deviceid': deviceid, 'source': source, 'number': number, 'enabled': sensorstatus}):
                    i2csensor.pop('_id')
                    if i2csensor.get('username'):
                        i2csensor.pop('username')
                    sensor_list.append(i2csensor)
            elif deviceid and sensorclass and sensorstatus is not None:
                #print("1 3 4")
                # 1, 3, 4
                for i2csensor in i2csensors.find({'type': type, 'deviceid': deviceid, 'class': sensorclass, 'enabled': sensorstatus}):
                    i2csensor.pop('_id')
                    if i2csensor.get('username'):
                        i2csensor.pop('username')
                    sensor_list.append(i2csensor)
                try:
                    for i2csensor in i2csensors.find({'type': type, 'deviceid': deviceid, 'subclass': sensorclass, 'enabled': sensorstatus}):
                        i2csensor.pop('_id')
                        if i2csensor.get('username'):
                            i2csensor.pop('username')
                        sensor_list.append(i2csensor)
                except:
                    pass
            elif source and sensorclass and sensorstatus is not None:
                #print("2 3 4")
                # 2, 3, 4
                for i2csensor in i2csensors.find({'type': type, 'source': source, 'number': number, 'class': sensorclass, 'enabled': sensorstatus}):
                    i2csensor.pop('_id')
                    if i2csensor.get('username'):
                        i2csensor.pop('username')
                    sensor_list.append(i2csensor)
                try:
                    for i2csensor in i2csensors.find({'type': type, 'source': source, 'number': number, 'subclass': sensorclass, 'enabled': sensorstatus}):
                        i2csensor.pop('_id')
                        if i2csensor.get('username'):
                            i2csensor.pop('username')
                        sensor_list.append(i2csensor)
                except:
                    pass

            elif deviceid and source:
                #print("1 2")
                # 1, 2
                for i2csensor in i2csensors.find({'type': type, 'deviceid': deviceid, 'source': source, 'number': number}):
                    i2csensor.pop('_id')
                    if i2csensor.get('username'):
                        i2csensor.pop('username')
                    sensor_list.append(i2csensor)
            elif deviceid and sensorclass:
                #print("1 3")
                # 1, 3
                for i2csensor in i2csensors.find({'type': type, 'deviceid': deviceid, 'class': sensorclass}):
                    i2csensor.pop('_id')
                    if i2csensor.get('username'):
                        i2csensor.pop('username')
                    sensor_list.append(i2csensor)
                try:
                    for i2csensor in i2csensors.find({'type': type, 'deviceid': deviceid, 'subclass': sensorclass}):
                        i2csensor.pop('_id')
                        if i2csensor.get('username'):
                            i2csensor.pop('username')
                        sensor_list.append(i2csensor)
                except:
                    pass
            elif deviceid and sensorstatus is not None:
                #print("1 4")
                # 1, 4
                for i2csensor in i2csensors.find({'type': type, 'deviceid': deviceid, 'enabled': sensorstatus}):
                    i2csensor.pop('_id')
                    if i2csensor.get('username'):
                        i2csensor.pop('username')
                    sensor_list.append(i2csensor)
            elif source and sensorclass:
                #print("2 3")
                # 2, 3
                for i2csensor in i2csensors.find({'type': type, 'source': source, 'number': number, 'class': sensorclass}):
                    i2csensor.pop('_id')
                    if i2csensor.get('username'):
                        i2csensor.pop('username')
                    sensor_list.append(i2csensor)
                try:
                    for i2csensor in i2csensors.find({'type': type, 'source': source, 'number': number, 'subclass': sensorclass}):
                        i2csensor.pop('_id')
                        if i2csensor.get('username'):
                            i2csensor.pop('username')
                        sensor_list.append(i2csensor)
                except:
                    pass
            elif source and sensorstatus is not None:
                #print("2 4")
                # 2, 4
                for i2csensor in i2csensors.find({'type': type, 'source': source, 'number': number, 'enabled': sensorstatus}):
                    i2csensor.pop('_id')
                    if i2csensor.get('username'):
                        i2csensor.pop('username')
                    sensor_list.append(i2csensor)
            elif sensorclass and sensorstatus:
                #print("3 4")
                # 3, 4
                for i2csensor in i2csensors.find({'type': type, 'class': sensorclass, 'enabled': sensorstatus}):
                    i2csensor.pop('_id')
                    if i2csensor.get('username'):
                        i2csensor.pop('username')
                    sensor_list.append(i2csensor)
                try:
                    for i2csensor in i2csensors.find({'type': type, 'subclass': sensorclass, 'enabled': sensorstatus}):
                        i2csensor.pop('_id')
                        if i2csensor.get('username'):
                            i2csensor.pop('username')
                        sensor_list.append(i2csensor)
                except:
                    pass

            elif deviceid is not None:
                #print("1")
                # 1
                for i2csensor in i2csensors.find({'type': type, 'deviceid': deviceid}):
                    i2csensor.pop('_id')
                    if i2csensor.get('username'):
                        i2csensor.pop('username')
                    sensor_list.append(i2csensor)
            elif source is not None:
                #print("2")
                # 2
                for i2csensor in i2csensors.find({'type': type, 'source': source, 'number': number}):
                    i2csensor.pop('_id')
                    if i2csensor.get('username'):
                        i2csensor.pop('username')
                    sensor_list.append(i2csensor)
            elif sensorclass is not None:
                #print("3")
                # 3
                for i2csensor in i2csensors.find({'type': type, 'class': sensorclass}):
                    i2csensor.pop('_id')
                    if i2csensor.get('username'):
                        i2csensor.pop('username')
                    sensor_list.append(i2csensor)
                try:
                    for i2csensor in i2csensors.find({'type': type, 'subclass': sensorclass}):
                        i2csensor.pop('_id')
                        if i2csensor.get('username'):
                            i2csensor.pop('username')
                        sensor_list.append(i2csensor)
                except:
                    pass
            elif sensorstatus is not None:
                #print("4")
                # 4
                for i2csensor in i2csensors.find({'type': type, 'enabled': sensorstatus}):
                    i2csensor.pop('_id')
                    if i2csensor.get('username'):
                        i2csensor.pop('username')
                    sensor_list.append(i2csensor)

            else:
                #print("X")
                # X
                for i2csensor in i2csensors.find({'type': type}):
                    i2csensor.pop('_id')
                    if i2csensor.get('username'):
                        i2csensor.pop('username')
                    sensor_list.append(i2csensor)

        return sensor_list

    def get_all_device_sensors(self, deviceid):
        sensor_list = []
        i2csensors = self.get_sensors_document();
        if i2csensors:
            for i2csensor in i2csensors.find({'deviceid': deviceid}):
                i2csensor.pop('_id')
                if i2csensor.get('username'):
                    i2csensor.pop('username')
                if i2csensor.get('devicename'):
                    i2csensor.pop('devicename')
                if i2csensor.get('deviceid'):
                    i2csensor.pop('deviceid')
                sensor_list.append(i2csensor)
        return sensor_list

    def get_all_device_sensors_input(self, deviceid):
        sensor_list = []
        i2csensors = self.get_sensors_document();
        if i2csensors:
            for i2csensor in i2csensors.find({'deviceid': deviceid, 'type': 'input'}):
                i2csensor.pop('_id')
                if i2csensor.get('username'):
                    i2csensor.pop('username')
                if i2csensor.get('devicename'):
                    i2csensor.pop('devicename')
                if i2csensor.get('deviceid'):
                    i2csensor.pop('deviceid')
                sensor_list.append(i2csensor)
        return sensor_list

    def get_all_sensors(self, deviceid, source):
        sensor_list = []
        i2csensors = self.get_sensors_document();
        if i2csensors:
            for i2csensor in i2csensors.find({'deviceid': deviceid, 'source': source}):
                i2csensor.pop('_id')
                if i2csensor.get('username'):
                    i2csensor.pop('username')
                if i2csensor.get('devicename'):
                    i2csensor.pop('devicename')
                if i2csensor.get('deviceid'):
                    i2csensor.pop('deviceid')
                sensor_list.append(i2csensor)
        return sensor_list

    def get_all_type_sensors(self, deviceid, source, type):
        sensor_list = []
        i2csensors = self.get_sensors_document();
        if i2csensors:
            for i2csensor in i2csensors.find({'deviceid': deviceid, 'source': source, 'type': type}):
                i2csensor.pop('_id')
                if i2csensor.get('username'):
                    i2csensor.pop('username')
                if i2csensor.get('devicename'):
                    i2csensor.pop('devicename')
                if i2csensor.get('deviceid'):
                    i2csensor.pop('deviceid')
                sensor_list.append(i2csensor)
        return sensor_list

    def get_sensors(self, deviceid, source, number):
        sensor_list = []
        i2csensors = self.get_sensors_document();
        if i2csensors:
            for i2csensor in i2csensors.find({'deviceid': deviceid, 'source': source, 'number': number}):
                i2csensor.pop('_id')
                #print(i2csensor)
                if i2csensor.get('enabled') is None and i2csensor.get('configured') is None:
                    #print("no enabled and no configured")
                    sensor = copy.deepcopy(i2csensor)
                    sensor['enabled'] = 0
                    sensor['configured'] = 0
                    i2csensors.replace_one(i2csensor, sensor)
                    if i2csensor.get('username'):
                        i2csensor.pop('username')
                    if i2csensor.get('devicename'):
                        i2csensor.pop('devicename')
                    if i2csensor.get('deviceid'):
                        i2csensor.pop('deviceid')
                    sensor_list.append(sensor)
                else:
                    if i2csensor.get('username'):
                        i2csensor.pop('username')
                    if i2csensor.get('devicename'):
                        i2csensor.pop('devicename')
                    if i2csensor.get('deviceid'):
                        i2csensor.pop('deviceid')
                    sensor_list.append(i2csensor)
        return sensor_list

    def get_sensors_enabled_input(self, deviceid, source, number):
        sensor_list = []
        i2csensors = self.get_sensors_document();
        if i2csensors:
            for i2csensor in i2csensors.find({'deviceid': deviceid, 'source': source, 'number': number, 'enabled': 1, 'type': 'input'}, {'sensorname': 1}):
                i2csensor.pop('_id')
                if i2csensor.get('username'):
                    i2csensor.pop('username')
                if i2csensor.get('devicename'):
                    i2csensor.pop('devicename')
                if i2csensor.get('deviceid'):
                    i2csensor.pop('deviceid')
                sensor_list.append(i2csensor)
        return sensor_list

    def get_sensors_with_enabled(self, deviceid, source, number):
        sensor_list = []
        i2csensors = self.get_sensors_document();
        if i2csensors:
            for i2csensor in i2csensors.find({'deviceid': deviceid, 'source': source, 'number': number}):
                #i2csensor['enabled'] = 0
                i2csensor.pop('_id')
                if i2csensor.get('username'):
                    i2csensor.pop('username')
                if i2csensor.get('devicename'):
                    i2csensor.pop('devicename')
                if i2csensor.get('deviceid'):
                    i2csensor.pop('deviceid')
                sensor_list.append(i2csensor)
        return sensor_list

    def add_sensor(self, deviceid, source, number, sensorname, data):
        i2csensors = self.get_sensors_document();
        timestamp = str(int(time.time()))
        device = {}
        #device['username']     = username
        #device['devicename']   = devicename
        device['deviceid']     = deviceid
        device['source']       = source
        device['number']       = number
        device['enabled']      = 0
        device['configured']   = 0
        device['sensorname']   = sensorname
        device_all = {}
        device_all.update(device)
        device_all.update(data)
        #print(device_all)
        i2csensors.insert_one(device_all)
        return True

    def delete_device_sensors(self, deviceid):
        i2csensors = self.get_sensors_document();
        try:
            i2csensors.delete_many({'deviceid': deviceid})
        except:
            print("delete_device_sensors: Exception occurred")
            pass

    def delete_device_sensor(self, username, devicename, sensorname):
        i2csensors = self.get_sensors_document();
        try:
            i2csensors.delete_many({'devicename': devicename, 'sensorname': sensorname})
        except:
            print("delete_device_sensors: Exception occurred")
            pass

    def delete_sensor(self, deviceid, source, number, sensorname):
        i2csensors = self.get_sensors_document();
        try:
            i2csensors.delete_many({'deviceid': deviceid, 'sensorname': sensorname})
        except:
            print("delete_sensor: Exception occurred")
            pass

    def check_sensor(self, deviceid, sensorname):
        i2csensors = self.get_sensors_document();
        if i2csensors:
            # Note: sensorname should be unique allthroughout the slots and accross I2C/ADC/1WIRE/TPROBE
            # so number and source should not be included
            for i2csensor in i2csensors.find({'deviceid': deviceid, 'sensorname': sensorname}):
                i2csensor.pop('_id')
                if i2csensor.get('username'):
                    i2csensor.pop('username')
                if i2csensor.get('devicename'):
                    i2csensor.pop('devicename')
                if i2csensor.get('deviceid'):
                    i2csensor.pop('deviceid')
                return i2csensor
        return None

    def get_sensor(self, deviceid, source, number, sensorname):
        i2csensors = self.get_sensors_document();
        if i2csensors:
            #for i2csensor in i2csensors.find({'deviceid': deviceid, 'sensorname': sensorname}):
            #    print(i2csensor)
            #print(username)
            #print(devicename)
            #print(source)
            #print(number)
            #print(sensorname)
            for i2csensor in i2csensors.find({'deviceid': deviceid, 'sensorname': sensorname, 'source': source, 'number': number}):
                i2csensor.pop('_id')
                if i2csensor.get('username'):
                    i2csensor.pop('username')
                if i2csensor.get('devicename'):
                    i2csensor.pop('devicename')
                if i2csensor.get('deviceid'):
                    i2csensor.pop('deviceid')
                #print(i2csensor)
                #print(len(i2csensor))
                return i2csensor
        return None

    def get_sensor_by_address(self, deviceid, source, number, address):
        i2csensors = self.get_sensors_document();
        if i2csensors:
            for i2csensor in i2csensors.find({'deviceid': deviceid, 'source': source, 'number': number, 'address': address}):
                i2csensor.pop('_id')
                if i2csensor.get('username'):
                    i2csensor.pop('username')
                if i2csensor.get('devicename'):
                    i2csensor.pop('devicename')
                if i2csensor.get('deviceid'):
                    i2csensor.pop('deviceid')
                return i2csensor
        return None

    def disable_unconfigure_sensors(self, deviceid):
        i2csensors = self.get_sensors_document();
        if i2csensors:
            for i2csensor in i2csensors.find({'deviceid': deviceid}):
                i2csensor.pop('_id')
                sensor = copy.deepcopy(i2csensor)
                sensor['enabled'] = 0
                sensor['configured'] = 0
                i2csensors.replace_one(i2csensor, sensor)

    def disable_unconfigure_sensors_source(self, deviceid, source, number):
        i2csensors = self.get_sensors_document();
        if i2csensors:
            for i2csensor in i2csensors.find({'deviceid': deviceid, 'source': source, 'number': number}):
                i2csensor.pop('_id')
                sensor = copy.deepcopy(i2csensor)
                sensor['enabled'] = 0
                sensor['configured'] = 0
                i2csensors.replace_one(i2csensor, sensor)

    def set_enable_configure_sensor(self, deviceid, source, number, sensorname, enabled, configured):
        i2csensors = self.get_sensors_document();
        if i2csensors:
            for i2csensor in i2csensors.find({'deviceid': deviceid, 'source': source, 'number': number, 'sensorname': sensorname}):
                i2csensor.pop('_id')
                sensor = copy.deepcopy(i2csensor)
                sensor['enabled'] = enabled
                sensor['configured'] = configured
                #print("xxx")
                #print(sensor)
                #print("yyy")
                i2csensors.replace_one(i2csensor, sensor)
                break


    ##########################################################
    # sensor readings
    ##########################################################

    def get_sensorreadings_document(self):
        #return self.client[config.CONFIG_MONGODB_TB_SENSORREADINGS]
        return self.client_sensor[config.CONFIG_MONGODB_TB_SENSORREADINGS]

    def update_sensor_reading(self, username, deviceid, source, address, sensor_readings):
        sensorreadings = self.get_sensorreadings_document();
        item = {}
        item['username'] = username
        item['deviceid'] = deviceid
        item['source'] = source
        if address is not None:
            item['address'] = address
        item['sensor_readings'] = sensor_readings

        if address is None:
            found = sensorreadings.find_one({'deviceid': deviceid, 'source': source})
            if found is None:
                #print("update_sensor_reading insert_one")
                #print(found)
                sensorreadings.insert_one(item)
            else:
                #print("update_sensor_reading replace_one")
                sensorreadings.replace_one({'deviceid': deviceid, 'source': source}, item)
        else:
            found = sensorreadings.find_one({'deviceid': deviceid, 'source': source, 'address': address})
            if found is None:
                #print("update_sensor_reading insert_one")
                #print(found)
                sensorreadings.insert_one(item)
            else:
                #print("update_sensor_reading replace_one")
                sensorreadings.replace_one({'deviceid': deviceid, 'source': source, 'address': address}, item)
        #print("update_sensor_reading")

    def delete_sensor_reading(self, deviceid, source, address):
        sensorreadings = self.get_sensorreadings_document();
        try:
            if address is None:
                sensorreadings.delete_many({'deviceid': deviceid, 'source': source})
            else:
                sensorreadings.delete_many({'deviceid': deviceid, 'source': source, 'address': address})
        except:
            print("delete_sensor_reading: Exception occurred")
            pass

    def delete_device_sensor_reading(self, deviceid):
        sensorreadings = self.get_sensorreadings_document();
        try:
            sensorreadings.delete_many({'deviceid': deviceid})
        except:
            print("delete_device_sensor_reading: Exception occurred")
            pass

    def delete_user_sensor_reading(self, username):
        sensorreadings = self.get_sensorreadings_document();
        try:
            sensorreadings.delete_many({'username': username})
        except:
            print("delete_user_sensor_reading: Exception occurred")
            pass

    def delete_sensors_readings(self, deviceid, source):
        sensorreadings = self.get_sensorreadings_document();
        try:
            sensorreadings.delete_many({'deviceid': deviceid, 'source': source})
        except:
            print("delete_sensors_readings: Exception occurred")
            pass

    def get_sensor_reading_by_deviceid(self, deviceid, source, address):
        sensorreadings = self.get_sensorreadings_document();
        if sensorreadings:
            if address is None:
                for sensorreading in sensorreadings.find({'deviceid': deviceid, 'source': source}):
                    sensorreading.pop('_id')
                    sensorreading.pop('username')
                    #print(sensorreading['sensor_readings'])
                    return sensorreading['sensor_readings']
            else:
                for sensorreading in sensorreadings.find({'deviceid': deviceid, 'source': source, 'address': address}):
                    sensorreading.pop('_id')
                    sensorreading.pop('username')
                    #print(sensorreading['sensor_readings'])
                    return sensorreading['sensor_readings']
        return None

    def get_sensors_readings_by_deviceid(self, deviceid, source):
        sensorreadings_list = []
        sensorreadings = self.get_sensorreadings_document();
        if sensorreadings:
            for sensorreading in sensorreadings.find({'deviceid': deviceid, 'source': source}):
                sensorreading.pop('_id')
                sensorreading.pop('username')
                sensorreadings_list.append(sensorreading['sensor_readings'])
        return sensorreadings_list

    def get_device_sensors_readings_by_deviceid(self, deviceid):
        sensorreadings_list = []
        sensorreadings = self.get_sensorreadings_document();
        if sensorreadings:
            for sensorreading in sensorreadings.find({'deviceid': deviceid}):
                sensorreading.pop('_id')
                sensorreading.pop('username')
                sensorreadings_list.append(sensorreading)
        return sensorreadings_list

    def get_user_sensors_readings(self, username):
        sensorreadings_list = []
        sensorreadings = self.get_sensorreadings_document();
        if sensorreadings:
            for sensorreading in sensorreadings.find({'username': username}):
                sensorreading.pop('_id')
                sensorreading.pop('username')
                sensorreadings_list.append(sensorreading)
        return sensorreadings_list


    ##########################################################
    # sensor readings dataset
    ##########################################################

    def get_sensorreadings_dataset_document(self):
        #return self.client[config.CONFIG_MONGODB_TB_SENSORREADINGS_DATASET]
        return self.client_sensor[config.CONFIG_MONGODB_TB_SENSORREADINGS_DATASET]

    def add_sensor_reading_dataset(self, username, deviceid, source, address, value, subclass_value):
        timestamp = str(int(time.time()))
        sensorreadings = self.get_sensorreadings_dataset_document();
        item = {}
        item['username'] = username
        item['deviceid'] = deviceid
        item['source'] = source
        if address is not None:
            item['address'] = address
        item['timestamp'] = timestamp
        item['value'] = value
        if subclass_value is not None:
            item['subclass_value'] = subclass_value

        if address is not None:
            readings = sensorreadings.find({'deviceid': deviceid, 'source': source, 'address': address})
        else:
            readings = sensorreadings.find({'deviceid': deviceid, 'source': source})
        if readings.count() >= config.CONFIG_MAX_DATASET:
            sensorreadings.delete_one(readings[0])
        sensorreadings.insert_one(item)
        #print("add_sensor_reading_dataset")

    def get_sensor_reading_dataset_by_deviceid(self, deviceid, source, address):
        # if sensor has a subclass data becomes  [[], [], ...]
        # if sensor has no subclass data becomes [[]]
        dataset  = {"labels": [], "data": []}
        sensorreadings = self.get_sensorreadings_dataset_document()
        if sensorreadings:
            if address is None:
                readings = sensorreadings.find({'deviceid': deviceid, 'source': source})
                for sensorreading in readings:
                    #print(sensorreading)
                    if sensorreading.get("value"):
                        if sensorreading.get("subclass_value"):
                            dataset["labels"].append(sensorreading["timestamp"])
                            if len(dataset["data"]) == 0:
                                dataset["data"].append([])
                                dataset["data"].append([])
                            dataset["data"][0].append(sensorreading["value"])
                            dataset["data"][1].append(sensorreading["subclass_value"])
                        else:
                            dataset["labels"].append(sensorreading["timestamp"])
                            if len(dataset["data"]) == 0:
                                dataset["data"].append([])
                            dataset["data"][0].append(sensorreading["value"])
            else:
                readings = sensorreadings.find({'deviceid': deviceid, 'source': source, 'address': address})
                for sensorreading in readings:
                    if sensorreading.get("value"):
                        if sensorreading.get("subclass_value"):
                            dataset["labels"].append(sensorreading["timestamp"])
                            if len(dataset["data"]) == 0:
                                dataset["data"].append([])
                                dataset["data"].append([])
                            dataset["data"][0].append(sensorreading["value"])
                            dataset["data"][1].append(sensorreading["subclass_value"])
                        else:
                            dataset["labels"].append(sensorreading["timestamp"])
                            if len(dataset["data"]) == 0:
                                dataset["data"].append([])
                            dataset["data"][0].append(sensorreading["value"])
        #print(dataset)
        return dataset

    def get_sensor_reading_dataset_by_deviceid_timebound(self, deviceid, source, address, datebegin, dateend, period, maxpoints):
        # if sensor has a subclass data becomes  [[], [], ...]
        # if sensor has no subclass data becomes [[]]
        dataset  = {"labels": [], "data": []}
        sensorreadings = self.get_sensorreadings_dataset_document()
        if sensorreadings:
            #print("begin:{} end:{}".format(datebegin, dateend))
            filter = {'deviceid': deviceid, 'source': source}
            filter['timestamp'] = {'$gte': datebegin, '$lt': dateend}
            if address is not None:
                filter['address'] = address
            readings = sensorreadings.find(filter)
            #print(readings.count())

            begin = datebegin
            end = begin+period
            if readings.count():
                if period == 5:
                    for reading in readings:
                        # handle case that device has no initial data or has gaps in between
                        while end < dateend:
                            if reading["timestamp"] < end:
                                break
                            dataset["labels"].append(begin)
                            if reading.get("subclass_value"):
                                if len(dataset["data"]) == 0:
                                    dataset["data"].append([])
                                    dataset["data"].append([])
                                dataset["data"][0].append(None)
                                dataset["data"][1].append(None)
                            else:
                                if len(dataset["data"]) == 0:
                                    dataset["data"].append([])
                                dataset["data"][0].append(None)
                            begin = end
                            end += period
                        if reading.get("value"):
                            if reading.get("subclass_value"):
                                dataset["labels"].append(reading["timestamp"])
                                if len(dataset["data"]) == 0:
                                    dataset["data"].append([])
                                    dataset["data"].append([])
                                dataset["data"][0].append(reading["value"])
                                dataset["data"][1].append(reading["subclass_value"])
                            else:
                                dataset["labels"].append(reading["timestamp"])
                                if len(dataset["data"]) == 0:
                                    dataset["data"].append([])
                                dataset["data"][0].append(reading["value"])
                            begin = end
                            end += period
                    # handle case that device got disconnected, no more data
                    while end < dateend:
                        dataset["labels"].append(begin)
                        if len(dataset["data"]) == 2:
                            if len(dataset["data"]) == 0:
                                dataset["data"].append([])
                                dataset["data"].append([])
                            dataset["data"][0].append(None)
                            dataset["data"][1].append(None)
                        else:
                            if len(dataset["data"]) == 0:
                                dataset["data"].append([])
                            dataset["data"][0].append(None)
                        begin = end
                        end += period
                else:
                    #dataset["labels_actual"] = []
                    #dataset["data_actual"] = []
                    dataset["low"] = []
                    dataset["high"] = []
                    points = []
                    points2 = []
                    for reading in readings:
                        if reading.get("value"):
                            if reading.get("subclass_value"):
                                #dataset["labels_actual"].append(reading["timestamp"])
                                #if len(dataset["data_actual"]) == 0:
                                #    dataset["data_actual"].append([])
                                #    dataset["data_actual"].append([])
                                #dataset["data_actual"][0].append(reading["value"])
                                #dataset["data_actual"][1].append(reading["subclass_value"])

                                if reading["timestamp"] < end:
                                    # add data to temporary array for averaging
                                    points.append(reading["value"])
                                    points2.append(reading["subclass_value"])
                                else:
                                    if len(dataset["data"]) == 0:
                                        dataset["data"].append([])
                                        dataset["low"].append([])
                                        dataset["high"].append([])
                                        dataset["data"].append([])
                                        dataset["low"].append([])
                                        dataset["high"].append([])

                                    # add label timestamp
                                    dataset["labels"].append(begin)

                                    # add data
                                    if len(points):
                                        # process data in temporary array for averaging, minum and maximum
                                        dataset["data"][0].append(round(statistics.mean(points), 1))
                                        dataset["low"][0].append(min(points))
                                        dataset["high"][0].append(max(points))
                                        points.clear()
                                        if len(points2):
                                            dataset["data"][1].append(round(statistics.mean(points2), 1))
                                            dataset["low"][1].append(min(points2))
                                            dataset["high"][1].append(max(points2))
                                            points2.clear()
                                    else:
                                        # handle no data
                                        dataset["data"][0].append(None)
                                        dataset["low"][0].append(None)
                                        dataset["high"][0].append(None)
                                        dataset["data"][1].append(None)
                                        dataset["low"][1].append(None)
                                        dataset["high"][1].append(None)

                                    begin = end
                                    end += period
                                    while end < dateend:
                                        if reading["timestamp"] < end:
                                            # add data to temporary array for averaging
                                            points.append(reading["value"])
                                            points2.append(reading["subclass_value"])
                                            break
                                        else:
                                            # add label timestamp
                                            dataset["labels"].append(begin)
                                            # handle no data
                                            dataset["data"][0].append(None)
                                            dataset["low"][0].append(None)
                                            dataset["high"][0].append(None)
                                            dataset["data"][1].append(None)
                                            dataset["low"][1].append(None)
                                            dataset["high"][1].append(None)
                                            # get the next period
                                            begin = end
                                            end += period

                            else:
                                #dataset["labels_actual"].append(reading["timestamp"])
                                #if len(dataset["data_actual"]) == 0:
                                #    dataset["data_actual"].append([])
                                #dataset["data_actual"][0].append(reading["value"])

                                if reading["timestamp"] < end:
                                    # add data to array for averaging
                                    points.append(reading["value"])
                                else:
                                    if len(dataset["data"]) == 0:
                                        dataset["data"].append([])
                                        dataset["low"].append([])
                                        dataset["high"].append([])

                                    # add label timestamp
                                    dataset["labels"].append(begin)

                                    # add data
                                    if len(points):
                                        # process data in temporary array for averaging, minum and maximum
                                        dataset["data"][0].append(round(statistics.mean(points), 1))
                                        dataset["low"][0].append(min(points))
                                        dataset["high"][0].append(max(points))
                                        points.clear()
                                    else:
                                        # handle no data
                                        dataset["data"][0].append(None)
                                        dataset["low"][0].append(None)
                                        dataset["high"][0].append(None)

                                    begin = end
                                    end += period
                                    while end < dateend:
                                        if reading["timestamp"] < end:
                                            # add data to temporary array for averaging
                                            points.append(reading["value"])
                                            break
                                        else:
                                            # add label timestamp
                                            dataset["labels"].append(begin)
                                            # handle no data
                                            dataset["data"][0].append(None)
                                            dataset["low"][0].append(None)
                                            dataset["high"][0].append(None)
                                            # get the next period
                                            begin = end
                                            end += period

                    # handle last element
                    if len(points):
                        dataset["labels"].append(begin)
                        dataset["data"][0].append(round(statistics.mean(points), 1))
                        dataset["low"][0].append(min(points))
                        dataset["high"][0].append(max(points))
                        begin = end
                        end += period
                    if len(points2):
                        dataset["data"][0].append(round(statistics.mean(points2), 1))
                        dataset["low"][0].append(min(points2))
                        dataset["high"][0].append(max(points2))
                    # handle case that device got disconnected, no more data
                    while end < dateend:
                        dataset["labels"].append(begin)
                        dataset["data"][0].append(None)
                        dataset["low"][0].append(None)
                        dataset["high"][0].append(None)
                        if len(dataset["data"]) == 2:
                            dataset["data"][0].append(None)
                            dataset["low"][0].append(None)
                            dataset["high"][0].append(None)
                        begin = end
                        end += period

            else:
                # handle no data
                if len(dataset["data"]) == 0:
                    dataset["data"].append([])
                while end < dateend:
                    dataset["labels"].append(begin)
                    dataset["data"][0].append(None)
                    begin = end
                    end += period

#        print(dataset["data_actual"][0][:9])
#        print(dataset["data"][0][:3])
#        print(dataset["low"][0][:3])
#        print(dataset["high"][0][:3])
#        print(len(dataset["data_actual"][0]))
#        print(len(dataset["labels"]))
#        print(len(dataset["data"][0]))
#        print(len(dataset["low"][0]))
#        print(len(dataset["high"][0]))
        return dataset

    def delete_sensor_reading_dataset(self, deviceid, source, address):
        sensorreadings = self.get_sensorreadings_dataset_document()
        try:
            if address is None:
                sensorreadings.delete_many({'deviceid': deviceid, 'source': source})
            else:
                sensorreadings.delete_many({'deviceid': deviceid, 'source': source, 'address': address})
        except:
            print("delete_sensor_reading_dataset: Exception occurred")
            pass

    def delete_device_sensor_reading_dataset(self, deviceid):
        sensorreadings = self.get_sensorreadings_dataset_document()
        try:
            sensorreadings.delete_many({'deviceid': deviceid})
        except:
            print("delete_device_sensor_reading_dataset: Exception occurred")
            pass

    def delete_user_sensor_reading_dataset(self, username):
        sensorreadings = self.get_sensorreadings_dataset_document()
        try:
            sensorreadings.delete_many({'username': username})
        except:
            print("delete_user_sensor_reading_dataset: Exception occurred")
            pass

    def delete_sensors_readings_dataset(self, deviceid, source):
        sensorreadings = self.get_sensorreadings_dataset_document()
        try:
            sensorreadings.delete_many({'deviceid': deviceid, 'source': source})
        except:
            print("delete_sensors_readings_dataset: Exception occurred")
            pass



    ##########################################################
    # mobile device tokens
    ##########################################################

    def get_mobile_devicetokens_document(self):
        return self.client[config.CONFIG_MONGODB_TB_DEVICETOKENS]

    def add_mobile_device_token(self, username, devicetoken, service, accesstoken):
        devicetokens = self.get_mobile_devicetokens_document()
        item = {}
        item['username'] = username
        item['devicetoken'] = devicetoken
        item['service'] = service
        item['accesstoken'] = accesstoken
        found = devicetokens.find_one({'username': username, 'devicetoken': devicetoken, 'service': service})
        #print(found)
        if found is None:
            #print("insert_one")
            devicetokens.insert_one(item)
        else:
            #print("replace_one")
            devicetokens.replace_one({'username': username, 'devicetoken': devicetoken, 'service': service}, item)

    def update_mobile_device_token(self, accesstoken, new_accesstoken):
        devicetokens = self.get_mobile_devicetokens_document()
        found = devicetokens.find_one({'accesstoken': accesstoken})
        if found is not None:
            replacement = copy.deepcopy(found)
            replacement['accesstoken'] = new_accesstoken
            devicetokens.replace_one(found, replacement)

    def delete_mobile_device_token(self, username, accesstoken):
        devicetokens = self.get_mobile_devicetokens_document()
        try:
            devicetokens.delete_one({'username': username, 'accesstoken': accesstoken})
        except:
            print("delete_mobile_device_token: Exception occurred")
            pass

    def delete_all_mobile_device_token(self, username):
        devicetokens = self.get_mobile_devicetokens_document()
        if devicetokens:
            try:
                devicetokens.delete_many({'username': username})
            except:
                print("delete_all_mobile_device_token: Exception occurred")
                pass

    def get_mobile_device_token(self, username, accesstoken):
        devicetokens_list = []
        devicetokens = self.get_mobile_devicetokens_document()
        if devicetokens:
            for devicetoken in devicetokens.find({'username': username, 'accesstoken': accesstoken}):
                devicetoken.pop('_id')
                devicetokens_list.append(devicetoken)
        return devicetokens_list

    def get_all_mobile_device_token(self, username):
        devicetokens_list = []
        devicetokens = self.get_mobile_devicetokens_document()
        if devicetokens:
            for devicetoken in devicetokens.find({'username': username}):
                devicetoken.pop('_id')
                devicetokens_list.append(devicetoken)
        return devicetokens_list


    ##########################################################
    # device location
    ##########################################################

    def get_device_location_document(self):
        return self.client[config.CONFIG_MONGODB_TB_DEVICELOCATION]

    def add_device_location(self, username, deviceid, location):
        devicelocations = self.get_device_location_document()
        item = {}
        item['username'] = username
        item['deviceid'] = deviceid
        item['location'] = location
        found = devicelocations.find_one({'deviceid': deviceid})
        if found is None:
            devicelocations.insert_one(item)
        else:
            devicelocations.replace_one({'deviceid': deviceid}, item)

    def get_device_location(self, deviceid):
        devicelocations = self.get_device_location_document()
        if devicelocations:
            for devicelocation in devicelocations.find({'deviceid': deviceid}):
                return devicelocation["location"]
        return None

    def get_devices_location(self, username):
        location_list = []
        devicelocations = self.get_device_location_document()
        if devicelocations:
            for devicelocation in devicelocations.find({'username': username}):
                devicelocation.pop('_id')
                devicelocation.pop('username')
                location_list.append(devicelocation)
        return location_list

    def delete_device_location(self, deviceid):
        devicelocations = self.get_device_location_document()
        if devicelocations:
            try:
                devicelocations.delete_one({ 'deviceid': deviceid })
            except:
                print("delete_device_location: Exception occurred")

    def delete_devices_location(self, username):
        devicelocations = self.get_device_location_document()
        if devicelocations:
            try:
                devicelocations.delete_many({ 'username': username })
            except:
                print("delete_devices_location: Exception occurred")


    ##########################################################
    # devices
    ##########################################################

    def get_registered_devices(self):
        return self.client[config.CONFIG_MONGODB_TB_DEVICES]

    def display_devices(self, username):
        devices = self.get_registered_devices()
        if devices:
            for device in devices.find({'username': username},{'username': 1, 'devicename':1, 'deviceid': 1, 'serialnumber':1, 'timestamp':1, 'heartbeat': 1, 'version': 1}):
                print(device)

    def get_devices(self, username):
        device_list = []
        devices = self.get_registered_devices()
        if devices and devices.count():
            for device in devices.find({'username': username},{'devicename':1, 'deviceid': 1, 'serialnumber':1, 'timestamp':1, 'heartbeat':1, 'version': 1}):
                device.pop('_id')
                device_list.append(device)
        return device_list
        #devices = self.get_registered_devices()
        #return list(devices.find({'username': username},{'devicename':1, 'deviceid': 1, 'serialnumber':1, 'timestamp':1, 'heartbeat':1, 'version': 1}))

    def get_devicenames(self, username):
        device_list = []
        devices = self.get_registered_devices()
        if devices and devices.count():
            for device in devices.find({'username': username},{'devicename':1}):
                device.pop('_id')
                device_list.append(device)
        return device_list
        #devices = self.get_registered_devices()
        #return list(devices.find({'username': username},{'devicename':1, 'deviceid': 1, 'serialnumber':1, 'timestamp':1, 'heartbeat':1, 'version': 1}))

    def get_devices_with_filter(self, username, filter):
        device_list = []
        devices = self.get_registered_devices()
        if devices and devices.count():
            filter_lo = filter.lower()
            for device in devices.find({'username': username},{'devicename':1, 'deviceid': 1, 'serialnumber':1, 'timestamp':1, 'heartbeat':1, 'version': 1}):
                device.pop('_id')
                if filter_lo in device["devicename"].lower():
                    # check the device name
                    device_list.append(device)
                elif filter_lo in device["deviceid"].lower():
                    # check the device id
                    device_list.append(device)
                else:
                    # check the sensors of the device
                    sensors = self.get_sensors_document();
                    if sensors and sensors.count():
                        for sensor in sensors.find({'username': username, 'devicename': device['devicename']}):
                            if filter_lo in sensor["sensorname"].lower():
                                # check the sensor name
                                device_list.append(device)
                                break
                            elif filter_lo in sensor["manufacturer"].lower():
                                # check the sensor manufacturer
                                device_list.append(device)
                                break
                            elif filter_lo in sensor["model"].lower():
                                # check the sensor model
                                device_list.append(device)
                                break
                            elif filter_lo in sensor["class"].lower():
                                # check the sensor class
                                device_list.append(device)
                                break
        return device_list

    def add_device(self, username, devicename, deviceid, serialnumber):
        timestamp = str(int(time.time()))
        device = {}
        device['username']     = username
        device['devicename']   = devicename
        device['deviceid']     = deviceid
        device['serialnumber'] = serialnumber
        device['timestamp']    = timestamp
        self.client.devices.insert_one(device)
        return True

    def delete_device(self, username, devicename):
        devices = self.get_registered_devices()
        if devices:
            devices.delete_one({ 'username': username, 'devicename': devicename })

    # a user cannot register the same device name
    def find_device(self, username, devicename):
        devices = self.get_registered_devices()
        if devices:
            for device in devices.find({'username': username, 'devicename': devicename},{'devicename':1, 'deviceid': 1, 'serialnumber':1, 'timestamp':1, 'heartbeat':1, 'version': 1}):
                device.pop('_id')
                return device
        return None

    # a user cannot register a device if it is already registered by another user
    def find_device_by_id(self, deviceid):
        devices = self.get_registered_devices()
        if devices:
            for device in devices.find({'deviceid': deviceid},{'username': 1, 'devicename':1, 'deviceid': 1, 'serialnumber':1, 'timestamp':1, 'heartbeat':1, 'version': 1}):
                device.pop('_id')
                return device
        return None

    def get_device_cached_values(self, username, devicename):
        devices = self.get_registered_devices()
        if devices:
            for device in devices.find({'username': username, 'devicename': devicename},{'heartbeat':1, 'version': 1}):
                device.pop('_id')
                return device
        return None

    def get_deviceid(self, username, devicename):
        devices = self.get_registered_devices()
        if devices:
            for device in devices.find({'username': username, 'devicename': devicename},{'deviceid': 1}):
                return device['deviceid']
        return None

    def add_device_heartbeat(self, deviceid):
        devices = self.get_registered_devices()
        if devices:
            for device in devices.find({'deviceid': deviceid}):
                new_device = copy.deepcopy(device)
                new_device['heartbeat'] = str(int(time.time()))
                devices.replace_one(device, new_device)
                return device['heartbeat']
        return None

    def save_device_version(self, username, devicename, version):
        devices = self.get_registered_devices()
        if devices:
            for device in devices.find({'username': username, 'devicename': devicename}):
                new_device = copy.deepcopy(device)
                new_device['version'] = version
                devices.replace_one(device, new_device)
                return device['version']
        return None

    def update_devicename(self, username, devicename, new_devicename):
        devices = self.get_registered_devices()
        if devices:
            for device in devices.find({'username': username, 'devicename': devicename}):
                device.pop('_id')
                new_device = copy.deepcopy(device)
                new_device['devicename'] = new_devicename
                devices.replace_one(device, new_device)
                break


    ##########################################################
    # devicegroups
    ##########################################################

    def sort_by_groupname(self, elem):
        return elem['groupname']

    def get_registered_devicegroups(self):
        return self.client[config.CONFIG_MONGODB_TB_DEVICEGROUPS]

    def add_devicegroup(self, username, groupname):
        devicegroups = self.get_registered_devicegroups()
        timestamp = time.time()
        item = {}
        item['username'] = username
        item['groupname'] = groupname
        item['groupid'] = "devgrp" + str(timestamp)
        item['timestamp'] = int(timestamp)
        item['devices'] = []
        devicegroups.insert_one(item)
        return True

    def delete_devicegroup(self, username, groupname):
        devicegroups = self.get_registered_devicegroups()
        if devicegroups:
            try:
                devicegroups.delete_one({ 'username': username, 'groupname': groupname })
            except:
                print("delete_devicegroup: Exception occurred")

    def get_devicegroup(self, username, groupname):
        devicegroups = self.get_registered_devicegroups()
        if devicegroups:
            for devicegroup in devicegroups.find({ 'username': username, 'groupname': groupname }):
                devicegroup.pop('_id')
                devicegroup.pop('groupid')
                devicegroup.pop('username')
                return devicegroup
        return None

    def get_devicegroups(self, username):
        devicegroups_list = []
        devicegroups = self.get_registered_devicegroups()
        if devicegroups and devicegroups.count():
            for devicegroup in devicegroups.find({'username': username}):
                devicegroup.pop('_id')
                devicegroup.pop('groupid')
                devicegroup.pop('username')
                devicegroups_list.append(devicegroup)
        devicegroups_list.sort(key=self.sort_by_groupname)
        return devicegroups_list

    def add_device_to_devicegroup(self, username, groupname, devicename):
        devicegroups = self.get_registered_devicegroups()
        if devicegroups and devicegroups.count():
            for devicegroup in devicegroups.find({ 'username': username, 'groupname': groupname }):
                print("{} {}".format(devicename, devicegroup['devices']))
                if devicename not in devicegroup['devices']:
                    new_devicegroup = copy.deepcopy(devicegroup)
                    new_devicegroup['devices'].append(devicename)
                    new_devicegroup['devices'].sort()
                    devicegroups.replace_one(devicegroup, new_devicegroup)
                    return True
                else:
                    return False
        return False

    def remove_device_from_devicegroup(self, username, groupname, devicename):
        devicegroups = self.get_registered_devicegroups()
        if devicegroups and devicegroups.count():
            for devicegroup in devicegroups.find({ 'username': username, 'groupname': groupname }):
                if devicename in devicegroup['devices']:
                    new_devicegroup = copy.deepcopy(devicegroup)
                    new_devicegroup['devices'].remove(devicename)
                    devicegroups.replace_one(devicegroup, new_devicegroup)
                break

    def set_devices_to_devicegroup(self, username, groupname, devices):
        devicegroups = self.get_registered_devicegroups()
        if devicegroups and devicegroups.count():
            for devicegroup in devicegroups.find({ 'username': username, 'groupname': groupname }):
                new_devicegroup = copy.deepcopy(devicegroup)
                new_devicegroup['devices'] = devices
                devicegroups.replace_one(devicegroup, new_devicegroup)
                break

    def update_name_devicegroup(self, username, groupname, new_groupname):
        devicegroups = self.get_registered_devicegroups()
        if devicegroups:
            for devicegroup in devicegroups.find({'username': username, 'groupname': groupname}):
                devicegroup.pop('_id')
                new_devicegroup= copy.deepcopy(devicegroup)
                new_devicegroup['groupname'] = new_groupname
                devicegroups.replace_one(devicegroup, new_devicegroup)
                break


class database_client_postgresql:

    def __init__(self):
        self.client = None

    def initialize(self):
        #self.client = psycopg2.connect("dbname={} user=postgres password=1234".format(config.CONFIG_POSTGRESQL_DB))
        pass


class database_viewer:

    def __init__(self):
        self.client = database_client()
        self.client.initialize()

    def epoch_to_datetime(self, epoch):
        return datetime.datetime.fromtimestamp(int(epoch)).strftime('%Y-%m-%d %H:%M:%S')

    def show(self):
        users = self.client.get_registered_users()
        if users:
            if not self.client.is_using_cognito:
                for user in users.find({},{'username': 1, 'password': 1, 'email': 1, 'givenname': 1, 'familyname': 1, 'timestamp': 1, 'token': 1, 'status': 1, 'confirmationcode': 1}):
                    print("USERNAME   : {}".format(user["username"]))
                    print("PASSWORD   : {}".format(user["password"]))
                    print("EMAIL      : {}".format(user["email"]))
                    print("GIVENNAME  : {}".format(user["givenname"]))
                    print("FAMILYNAME : {}".format(user["familyname"]))
                    print("timestamp  : {}".format(self.epoch_to_datetime(user["timestamp"])))
                    print("token      : {}".format(user["token"]))
                    print("status     : {}".format(user["status"]))
                    print("confirmationcode : {}".format(user["confirmationcode"]))
                    print("devices    :")
                    devices = self.client.get_registered_devices()
                    if devices and devices.count():
                        for device in devices.find():
                            if device['username'] == user["username"]:
                                print("\r\n    DEVICENAME    : {}".format(device["devicename"]))
                                print("        deviceid      : {}".format(device["deviceid"]))
                                if device.get("serialnumber"):
                                    print("        serialnumber  : {}".format(device["serialnumber"]))
                                print("        timestamp : {}".format(self.epoch_to_datetime(device["timestamp"])))
                    print("")
            else:
                for user in users:
                    print("USERNAME     : {}".format(user["username"]))
                    print("EMAIL        : {}".format(user["email"]))
                    print("GIVENNAME    : {}".format(user["given_name"]))
                    print("FAMILYNAME   : {}".format(user["family_name"]))
                    print("creationdate : {}".format(user["creationdate"]))
                    print("modifieddate : {}".format(user["modifieddate"]))
                    print("enabled      : {}".format(user["enabled"]))
                    print("status       : {}".format(user["status"]))
                    print("devices      :")
                    devices = self.client.get_registered_devices()
                    if devices and devices.count():
                        for device in devices.find({'username': user["username"]}):
                            print("\r\n    DEVICENAME    : {}".format(device["devicename"]))
                            print("        deviceid  : {}".format(device["deviceid"]))
                            if device.get("serialnumber"):
                                print("        serialnumber  : {}".format(device["serialnumber"]))
                            print("        timestamp : {}".format(self.epoch_to_datetime(device["timestamp"])))
                            print("histories")
                            histories = self.client.get_device_history(device["deviceid"])
                            for history in histories:
                                #print(history)
                                #print(history["deviceid"])
                                print("        {}".format(history["topic"]))
                                print("        {}".format(history["payload"]))
                                print("        {}".format(history["direction"]))
                                print("        {}".format(history["timestamp"]))
                                print("")
                    print("")


    def reset(self):
        users = self.client.get_registered_users()
        for user in users:
            devices = self.client.get_registered_devices()
            if devices:
                for device in devices.find({'username': user["username"]},{'username': 1, 'devicename':1, 'deviceid': 1}):
                    histories = self.client.get_device_history(device["deviceid"])
                    for history in histories:
                        self.client.delete_device_history(device['deviceid'])
                    self.client.delete_device(device['username'], device["devicename"])
                    print("Deleted device {}".format(device["devicename"]))
            #self.client.delete_user(user["username"])
            #print("Deleted user {}".format(user["username"]))


