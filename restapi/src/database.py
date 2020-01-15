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


    def initialize(self):
        self._users.initialize()
        self._devices.initialize()

    def is_using_cognito(self):
        return self.use_cognito



    ##########################################################
    # transactions
    ##########################################################

    def transactions_paypal_set_payment(self, username, token, payment):
        return self._transactions.paypal_set_payment(username, token, payment)

    def transactions_paypal_execute_payment(self, username, token, payment):
        return self._transactions.paypal_execute_payment(username, token, payment)

    def transactions_paypal_verify_payment(self, username, token, payment):
        return self._transactions.paypal_verify_payment(username, token, payment)


    ##########################################################
    # subscriptions
    ##########################################################

    def get_subscription(self, username):
        return self._subscriptions.get_subscription(username)

    def set_subscription(self, username, credits):
        return self._subscriptions.set_subscription(username, credits)


    ##########################################################
    # users
    ##########################################################

    def get_registered_users(self):
        return self._users.get_registered_users()

    def find_user(self, username):
        return self._users.find_user(username)

    def find_email(self, email):
        return self._users.find_email(email)

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

    def logout(self, token):
        return self._users.logout(token)

    def verify_token(self, username, token):
        return self._users.verify_token(username, token)

    def refresh_token(self, username, token):
        return self._users.refresh_token(username, token)

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


    ##########################################################
    # history
    ##########################################################

    def add_device_history(self, deviceid, topic, payload, direction):
        devices = self.get_registered_devices()
        if devices:
            for device in devices.find({'deviceid': deviceid},{'devicename':1, 'deviceid': 1}):
                self._devices.add_device_history(device['devicename'], deviceid, topic, payload, direction)
                return

    def get_device_history(self, deviceid):
        return self._devices.get_device_history(deviceid)

    def delete_device_history(self, deviceid):
        return self._devices.delete_device_history(deviceid)

    def sort_user_history(self, elem):
        return elem['timestamp']

    def get_user_history(self, username):
        user_histories = []
        devices = self._devices.get_registered_devices()
        if devices and devices.count():
            for device in devices.find({'username': username}):
                histories = self._devices.get_device_history(device["deviceid"])
                #print(histories)
                for history in histories:
                    history['timestamp'] = datetime.datetime.fromtimestamp(int(history['timestamp'])).strftime('%Y-%m-%d %H:%M:%S')
                if histories and len(histories) > 0:
                    user_histories += histories
        user_histories.sort(key=self.sort_user_history, reverse=True)
        return user_histories

    def get_user_history_filtered(self, username, devicename, direction, topic, datebegin, dateend):
        filter_devices = {'username': username}
        if devicename is not None:
            filter_devices['devicename'] = devicename

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
                for history in histories:
                    #print(history['timestamp'])
                    history['timestamp'] = datetime.datetime.fromtimestamp(int(history['timestamp'])).strftime('%Y-%m-%d %H:%M:%S')
                    user_histories.append(history)
                #print(len(histories))
        #print(len(user_histories))

        user_histories.sort(key=self.sort_user_history, reverse=True)
        return user_histories


    ##########################################################
    # notifications
    ##########################################################

    def add_device_notification(self, username, devicename, source, notification):
        deviceid = self._devices.get_deviceid(username, devicename)
        return self._devices.add_device_notification(username, devicename, deviceid, source, notification)

    def update_device_notification(self, username, devicename, source, notification):
        deviceid = self._devices.get_deviceid(username, devicename)
        return self._devices.update_device_notification(username, devicename, deviceid, source, notification)

    def delete_device_notification(self, username, devicename):
        return self._devices.delete_device_notification(username, devicename)

    def get_device_notification(self, username, devicename, source):
        return self._devices.get_device_notification(username, devicename, source)

    def get_device_notification_by_deviceid(self, deviceid, source):
        return self._devices.get_device_notification_by_deviceid(deviceid, source)


    ##########################################################
    # sensors
    ##########################################################

    def get_all_sensors(self, username, devicename, source):
        return self._devices.get_all_sensors(username, devicename, source)

    def get_all_type_sensors(self, username, devicename, source, type):
        return self._devices.get_all_type_sensors(username, devicename, source, type)

    def get_sensors(self, username, devicename, source, number):
        return self._devices.get_sensors(username, devicename, source, number)

    def get_sensors_count(self, username, devicename, source, number):
        return len(self._devices.get_sensors(username, devicename, source, number))

    def get_sensors_enabled_input(self, username, devicename, source, number):
        return self._devices.get_sensors_enabled_input(username, devicename, source, number)

    def get_sensors_with_enabled(self, username, devicename, source, number):
        return self._devices.get_sensors_with_enabled(username, devicename, source, number)

    def add_sensor(self, username, devicename, source, number, sensorname, data):
        return self._devices.add_sensor(username, devicename, source, number, sensorname, data)

    def delete_sensor(self, username, devicename, source, number, sensorname):
        self._devices.delete_sensor(username, devicename, source, number, sensorname)

    def check_sensor(self, username, devicename, sensorname):
        return self._devices.check_sensor(username, devicename, sensorname)

    def get_sensor(self, username, devicename, source, number, sensorname):
        return self._devices.get_sensor(username, devicename, source, number, sensorname)

    def get_sensor_by_address(self, username, devicename, source, number, address):
        return self._devices.get_sensor_by_address(username, devicename, source, number, address)

    def disable_unconfigure_sensors(self, username, devicename):
        self._devices.disable_unconfigure_sensors(username, devicename)

    def disable_unconfigure_sensors_source(self, username, devicename, source, number):
        self._devices.disable_unconfigure_sensors_source(username, devicename, source, number)

    def set_enable_configure_sensor(self, username, devicename, source, number, sensorname, enabled, configured):
        self._devices.set_enable_configure_sensor(username, devicename, source, number, sensorname, enabled, configured)


    ##########################################################
    # sensor readings
    ##########################################################

    def add_sensor_reading(self, deviceid, source, address, sensor_readings):
        self._devices.update_sensor_reading(deviceid, source, address, sensor_readings)

    def delete_sensor_reading(self, username, devicename, source, address):
        self._devices.delete_sensor_reading(self._devices.get_deviceid(username, devicename), source, address)

    def delete_sensors_readings(self, username, devicename, source):
        self._devices.delete_sensors_readings(self._devices.get_deviceid(username, devicename), source)

    def get_sensor_reading(self, username, devicename, source, address):
        return self._devices.get_sensor_reading_by_deviceid(self._devices.get_deviceid(username, devicename), source, address)

    def get_sensors_readings(self, username, devicename, source):
        return self._devices.get_sensors_readings_by_deviceid(self._devices.get_deviceid(username, devicename), source)

    def get_sensor_reading_by_deviceid(self, deviceid, source, address):
        return self._devices.get_sensor_reading_by_deviceid(deviceid, source, address)


    ##########################################################
    # devices
    ##########################################################

    def display_devices(self, username):
        self._devices.display_devices(username)

    def get_registered_devices(self):
        return self._devices.get_registered_devices()

    def get_devices(self, username):
        return self._devices.get_devices(username)

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

    def is_email_verified(self, username):
        (result, users) = self.client.admin_list_users()
        if result == False:
            return True
        if users:
            for user in users:
                if user["username"] == username:
                    return user["status"]=="CONFIRMED"
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
            return None, None, None
        access_token = response['AuthenticationResult']['AccessToken']
        refresh_token = response['AuthenticationResult']['RefreshToken']
        id_token = response['AuthenticationResult']['IdToken']
        return access_token, refresh_token, id_token

    def logout(self, token):
        (result, response) = self.client.logout(token)
        #print("cognito logout = {}".format(result))

    def refresh_token(self, username, token):
        (result, response) = self.client.refresh_token(token['refresh'])
        if result:
            new_token = {}
            new_token['access'] = response['AuthenticationResult']['AccessToken']
            new_token['refresh'] = token['refresh']
            new_token['id'] = response['AuthenticationResult']['IdToken']
            print("Token refreshed! {} {}".format(result, response))
            return new_token
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
        elif result != 0: # fail or unexpected error
            print("Unexpected error! {}".format(result))
            return result, None
        return result, None

    def get_username_from_token(self, token):
        username = self.client.get_username_from_token(token['access'])
        return username

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


class database_client_mongodb:

    def __init__(self):
        self.client = None

    def initialize(self):
        mongo_client = MongoClient(config.CONFIG_MONGODB_HOST, config.CONFIG_MONGODB_PORT)
        self.client = mongo_client[config.CONFIG_MONGODB_DB]
        self.paypal = paypal_client()
        self.paypal.initialize()


    ##########################################################
    # transaction
    ##########################################################

    def get_subscription_db(self):
        return self.client[config.CONFIG_MONGODB_TB_TRANSACTIONS]

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

    def paypal_execute_payment(self, username, token, payment):
        payment_id = payment["paymentId"]
        payer_id = payment["PayerID"]
        payment_token = payment["token"]

        result = self.paypal.execute_payment(payment_id, payer_id)
        if not result:
            print("Payment failed!")
            return False

        payment_result = self.paypal.fetch_payment(payment_id)
        status = self.paypal.get_payment_status(payment_result)
        if status != "approved":
            print("Payment not yet completed! {}".format(status))
            return False

        print("Payment completed successfully!")
        self.paypal.display_payment_result(payment_result)
        return True

    def paypal_verify_payment(self, username, token, payment):
        payment_id = payment["paymentId"]
        if not payment_id:
            return False

        payment_result = self.paypal.fetch_payment(payment_id)
        if not payment_result:
            return False

        status = self.paypal.get_payment_status(payment_result)
        if status != "approved":
            print("Payment not yet completed! {}".format(status))
            return False

        #print("Payment completed successfully!")
        self.paypal.display_payment_result(payment_result)
        return True


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
                for subscription in subscriptions.find({'username':username},{'username': 1, 'type': 1, 'credits': 1}):
                    found = True
                    subscription.pop('_id')
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
                for subscription in subscriptions.find({'username': username},{'username': 1, 'type': 1, 'credits': 1}):
                    current_amount = int(subscription['credits'])
                    new_amount = int(subscription['credits']) + int(credits)
                    #print("current_amount={} new_amount={}".format(current_amount, new_amount))
                    subscription['type'] = config.CONFIG_SUBSCRIPTION_PAID_TYPE
                    subscription['credits'] = str(new_amount)
                    self.client.subscriptions.replace_one({'username': username}, subscription)
                    subscription.pop('_id')
                    subscription.pop('username')
                    return subscription 
        return None


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

    def add_device_history(self, devicename, deviceid, topic, payload, direction):
        history = self.get_history_document();
        timestamp = int(time.time())
        item = {}
        item['timestamp'] = timestamp
        item['direction'] = direction
        item['deviceid'] = deviceid
        item['devicename'] = devicename
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
    # notifications
    ##########################################################

    def get_notifications_document(self):
        return self.client[config.CONFIG_MONGODB_TB_NOTIFICATIONS]

    def add_device_notification(self, username, devicename, deviceid, source, notification):
        notifications = self.get_notifications_document();
        item = {}
        item['username'] = username
        item['devicename'] = devicename
        item['deviceid'] = deviceid
        item['source'] = source
        item['notification'] = notification
        notifications.insert_one(item)
        return item

    def update_device_notification(self, username, devicename, deviceid, source, notification):
        notifications = self.get_notifications_document();
        item = {}
        item['username'] = username
        item['devicename'] = devicename
        item['deviceid'] = deviceid
        item['source'] = source
        item['notification'] = notification
        #print("update_device_notification find_one")
        found = notifications.find_one({'username': username, 'devicename': devicename, 'source': source})
        if found is None:
            print("update_device_notification insert_one")
            #print(found)
            notifications.insert_one(item)
        else:
            print("update_device_notification replace_one")
            notifications.replace_one({'username': username, 'devicename': devicename, 'source': source}, item)
        return item

    def delete_device_notification(self, username, devicename):
        notifications = self.get_notifications_document();
        try:
            notifications.delete_many({'username': username, 'devicename': devicename})
        except:
            print("delete_device_notification: Exception occurred")
            pass

    def get_device_notification(self, username, devicename, source):
        notifications = self.get_notifications_document();
        if notifications:
            for notification in notifications.find({'username': username, 'devicename': devicename, 'source': source}):
                notification.pop('_id')
                #print(notification['notification'])
                return notification['notification']
        return None

    def get_device_notification_by_deviceid(self, deviceid, source):
        notifications = self.get_notifications_document();
        if notifications:
            for notification in notifications.find({'deviceid': deviceid, 'source': source}):
                notification.pop('_id')
                #print(notification['notification'])
                return notification['notification']
        return None


    ##########################################################
    # sensors
    ##########################################################

    def get_sensors_document(self):
        return self.client[config.CONFIG_MONGODB_TB_I2CSENSORS]

    def get_all_sensors(self, username, devicename, source):
        sensor_list = []
        i2csensors = self.get_sensors_document();
        if i2csensors:
            for i2csensor in i2csensors.find({'username': username, 'devicename': devicename, 'source': source}):
                i2csensor.pop('_id')
                i2csensor.pop('username')
                sensor_list.append(i2csensor)
        return sensor_list

    def get_all_type_sensors(self, username, devicename, source, type):
        sensor_list = []
        i2csensors = self.get_sensors_document();
        if i2csensors:
            for i2csensor in i2csensors.find({'username': username, 'devicename': devicename, 'source': source, 'type': type}):
                i2csensor.pop('_id')
                i2csensor.pop('username')
                sensor_list.append(i2csensor)
        return sensor_list

    def get_sensors(self, username, devicename, source, number):
        sensor_list = []
        i2csensors = self.get_sensors_document();
        if i2csensors:
            for i2csensor in i2csensors.find({'username': username, 'devicename': devicename, 'source': source, 'number': number}):
                i2csensor.pop('_id')
                #print(i2csensor)
                if i2csensor.get('enabled') is None and i2csensor.get('configured') is None:
                    #print("no enabled and no configured")
                    sensor = copy.deepcopy(i2csensor)
                    sensor['enabled'] = 0
                    sensor['configured'] = 0
                    i2csensors.replace_one(i2csensor, sensor)
                    sensor.pop('username')
                    sensor_list.append(sensor)
                else:
                    i2csensor.pop('username')
                    sensor_list.append(i2csensor)
        return sensor_list

    def get_sensors_enabled_input(self, username, devicename, source, number):
        sensor_list = []
        i2csensors = self.get_sensors_document();
        if i2csensors:
            for i2csensor in i2csensors.find({'username': username, 'devicename': devicename, 'source': source, 'number': number, 'enabled': 1, 'type': 'input'}, {'sensorname': 1}):
                i2csensor.pop('_id')
                sensor_list.append(i2csensor)
        return sensor_list

    def get_sensors_with_enabled(self, username, devicename, source, number):
        sensor_list = []
        i2csensors = self.get_sensors_document();
        if i2csensors:
            for i2csensor in i2csensors.find({'username': username, 'devicename': devicename, 'source': source, 'number': number}):
                #i2csensor['enabled'] = 0
                i2csensor.pop('_id')
                i2csensor.pop('username')
                sensor_list.append(i2csensor)
        return sensor_list

    def add_sensor(self, username, devicename, source, number, sensorname, data):
        i2csensors = self.get_sensors_document();
        timestamp = str(int(time.time()))
        device = {}
        device['username']     = username
        device['devicename']   = devicename
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

    def delete_sensor(self, username, devicename, source, number, sensorname):
        i2csensors = self.get_sensors_document();
        try:
            i2csensors.delete_many({'username': username, 'devicename': devicename, 'source': source, 'number': number, 'sensorname': sensorname})
        except:
            print("delete_sensor: Exception occurred")
            pass

    def check_sensor(self, username, devicename, sensorname):
        i2csensors = self.get_sensors_document();
        if i2csensors:
            # Note: sensorname should be unique allthroughout the slots and accross I2C/ADC/1WIRE/TPROBE
            # so number and source should not be included
            for i2csensor in i2csensors.find({'username': username, 'devicename': devicename, 'sensorname': sensorname}):
                i2csensor.pop('_id')
                i2csensor.pop('username')
                return i2csensor
        return None

    def get_sensor(self, username, devicename, source, number, sensorname):
        i2csensors = self.get_sensors_document();
        if i2csensors:
            for i2csensor in i2csensors.find({'username': username, 'devicename': devicename, 'sensorname': sensorname, 'source': source, 'number': number}):
                i2csensor.pop('_id')
                i2csensor.pop('username')
                #print(i2csensor)
                #print(len(i2csensor))
                return i2csensor
        return None

    def get_sensor_by_address(self, username, devicename, source, number, address):
        i2csensors = self.get_sensors_document();
        if i2csensors:
            for i2csensor in i2csensors.find({'username': username, 'devicename': devicename, 'source': source, 'number': number, 'address': address}):
                i2csensor.pop('_id')
                i2csensor.pop('username')
                return i2csensor
        return None

    def disable_unconfigure_sensors(self, username, devicename):
        i2csensors = self.get_sensors_document();
        if i2csensors:
            for i2csensor in i2csensors.find({'username': username, 'devicename': devicename}):
                i2csensor.pop('_id')
                sensor = copy.deepcopy(i2csensor)
                sensor['enabled'] = 0
                sensor['configured'] = 0
                i2csensors.replace_one(i2csensor, sensor)

    def disable_unconfigure_sensors_source(self, username, devicename, source, number):
        i2csensors = self.get_sensors_document();
        if i2csensors:
            for i2csensor in i2csensors.find({'username': username, 'devicename': devicename, 'source': source, 'number': number}):
                i2csensor.pop('_id')
                sensor = copy.deepcopy(i2csensor)
                sensor['enabled'] = 0
                sensor['configured'] = 0
                i2csensors.replace_one(i2csensor, sensor)

    def set_enable_configure_sensor(self, username, devicename, source, number, sensorname, enabled, configured):
        i2csensors = self.get_sensors_document();
        if i2csensors:
            for i2csensor in i2csensors.find({'username': username, 'devicename': devicename, 'source': source, 'number': number, 'sensorname': sensorname}):
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
        return self.client[config.CONFIG_MONGODB_TB_SENSORREADINGS]

    def update_sensor_reading(self, deviceid, source, address, sensor_readings):
        sensorreadings = self.get_sensorreadings_document();
        item = {}
        item['deviceid'] = deviceid
        item['source'] = source
        if address is not None:
            item['address'] = address
        item['sensor_readings'] = sensor_readings

        if address is None:
            #print("update_sensor_reading find_one")
            found = sensorreadings.find_one({'deviceid': deviceid, 'source': source})
            if found is None:
                #print("update_sensor_reading insert_one")
                #print(found)
                sensorreadings.insert_one(item)
            else:
                #print("update_sensor_reading replace_one")
                sensorreadings.replace_one({'deviceid': deviceid, 'source': source}, item)
        else:
            #print("update_sensor_reading find_one")
            found = sensorreadings.find_one({'deviceid': deviceid, 'source': source, 'address': address})
            if found is None:
                #print("update_sensor_reading insert_one")
                #print(found)
                sensorreadings.insert_one(item)
            else:
                #print("update_sensor_reading replace_one")
                sensorreadings.replace_one({'deviceid': deviceid, 'source': source, 'address': address}, item)

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
                    #print(sensorreading['sensor_readings'])
                    return sensorreading['sensor_readings']
            else:
                for sensorreading in sensorreadings.find({'deviceid': deviceid, 'source': source, 'address': address}):
                    sensorreading.pop('_id')
                    #print(sensorreading['sensor_readings'])
                    return sensorreading['sensor_readings']
        return None

    def get_sensors_readings_by_deviceid(self, deviceid, source):
        sensorreadings_list = []
        sensorreadings = self.get_sensorreadings_document();
        if sensorreadings:
            for sensorreading in sensorreadings.find({'deviceid': deviceid, 'source': source}):
                sensorreading.pop('_id')
                sensorreadings_list.append(sensorreading['sensor_readings'])
        return sensorreadings_list


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

    def get_devices_with_filter(self, username, filter):
        device_list = []
        devices = self.get_registered_devices()
        if devices and devices.count():
            filter_lo = filter.lower()
            for device in devices.find({'username': username},{'devicename':1, 'deviceid': 1, 'serialnumber':1, 'timestamp':1, 'heartbeat':1, 'version': 1}):
                device.pop('_id')
                if filter_lo in device["devicename"].lower():
                    device_list.append(device)
                elif filter_lo in device["deviceid"].lower():
                    device_list.append(device)
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
            for device in devices.find({'deviceid': deviceid},{'username': 1, 'devicename': 1, 'deviceid': 1, 'serialnumber':1, 'timestamp': 1, 'heartbeat': 1, 'version': 1}):
                if device.get('heartbeat'):
                    device['heartbeat'] = str(int(time.time()))
                    devices.replace_one({'deviceid': deviceid}, device)
                else:
                    #print('add_device_heartbeat no heartbeat')
                    device['heartbeat'] = str(int(time.time()))
                    devices.replace_one({'deviceid': deviceid}, device)
                return device['heartbeat']
        return None

    def save_device_version(self, username, devicename, version):
        devices = self.get_registered_devices()
        if devices:
            for device in devices.find({'username': username, 'devicename': devicename},{'username': 1, 'devicename': 1, 'deviceid': 1, 'serialnumber':1, 'timestamp': 1, 'heartbeat': 1, 'version': 1}):
                if device.get('version'):
                    device['version'] = version
                    devices.replace_one({'username': username, 'devicename': devicename}, device)
                else:
                    #print('save_device_version no version')
                    device['version'] = version
                    devices.replace_one({'username': username, 'devicename': devicename}, device)
                return device['version']
        return None


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


