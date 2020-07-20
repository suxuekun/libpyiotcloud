import time
import hmac
import hashlib
import datetime
import random
import copy
from history_config import config
from pymongo import MongoClient
#from web_server_cognito_client import cognito_client



class database_models:

    MONGODB    = 0
    AWSCOGNITO = 1
    POSTGRESQL = 2



##########################################################
# USER database   : AWS Cognito or MongoDB or PostgreSQL
# DEVICE database : MongoDB or PostgreSQL
##########################################################
class database_client:

    def __init__(self, model_users=database_models.MONGODB, model_devices=database_models.MONGODB, host=config.CONFIG_MONGODB_HOST, port=config.CONFIG_MONGODB_PORT):
        self.use_cognito = True if model_users==database_models.AWSCOGNITO else False

        # user database
        #if model_users == database_models.AWSCOGNITO:
        #    self._users = database_client_cognito()
        #elif model_users == database_models.MONGODB:
        #    self._users = database_client_mongodb()
        #elif model_users == database_models.POSTGRESQL:
        #    self._users = database_client_postgresql()

        # device database
        if model_devices == database_models.MONGODB:
            self._devices = database_client_mongodb(host, port)
        elif model_devices == database_models.POSTGRESQL:
            self._devices = database_client_postgresql()

    def initialize(self):
        #self._users.initialize()
        self._devices.initialize()

    def is_using_cognito(self):
        return self.use_cognito


    ##########################################################
    # users
    ##########################################################

    def get_registered_users(self):
        return self._users.get_registered_users()

    def find_user(self, username):
        return self._users.find_user(username)

    def find_email(self, email):
        return self._users.find_email(email)

    def get_user_info(self, access_token):
        return self._users.get_user_info(access_token)

    def login(self, username, password):
        return self._users.login(username, password)

    def logout(self, token):
        return self._users.logout(token)

    def verify_token(self, username, token):
        return self._users.verify_token(username, token)

    def delete_user(self, username):
        self._users.delete_user(username)

    def add_user(self, username, password, email, givenname, familyname):
        return self._users.add_user(username, password, email, givenname, familyname)

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


    ##########################################################
    # history
    ##########################################################

    def add_device_history(self, deviceid, topic, payload, direction):
        self._devices.add_device_history(None, deviceid, topic, payload, direction)

    def get_device_history(self, deviceid):
        return self._devices.get_device_history(deviceid)

    def sort_user_history(self, elem):
        return elem['timestamp']


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
    # sensor readings
    ##########################################################

    def add_sensor_reading(self, deviceid, source, address, sensor_readings):
        self._devices.update_sensor_reading(deviceid, source, address, sensor_readings)

    def delete_sensor_reading(self, username, devicename, source, address):
        self._devices.delete_sensor_reading(self._devices.get_deviceid(username, devicename), source, address)

    def get_sensor_reading(self, username, devicename, source, address):
        return self._devices.get_sensor_reading_by_deviceid(self._devices.get_deviceid(username, devicename), source, address)

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

    def add_device(self, username, devicename, cert, pkey):
        return self._devices.add_device(username, devicename, cert, pkey)

    def delete_device(self, username, devicename):
        self._devices.delete_device(username, devicename)

    def find_device(self, username, devicename):
        return self._devices.find_device(username, devicename)

    def get_deviceid(self, username, devicename):
        return self._devices.get_deviceid(username, devicename)

    def add_device_heartbeat(self, deviceid):
        return self._devices.add_device_heartbeat(deviceid)


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
        self.access_token = None


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

    def login(self, username, password):
        (result, response) = self.client.login(username, password)
        if not result:
            return None
        self.access_token = response['AuthenticationResult']['AccessToken']
        return self.access_token

    def logout(self, token):
        (result, response) = self.client.logout(token)
        print("cognito logout = {}".format(result))

    def verify_token(self, username, token):
        valid = self.client.verify_token(token, username)
        return valid

    def get_confirmationcode(self, username):
        return None

    def resend_confirmationcode(self, username):
        (result, response) = self.client.resend_confirmation_code(username)
        return result

    def delete_user(self, username):
        pass

    def add_user(self, username, password, email, givenname, familyname):
        (result, response) = self.client.sign_up(username, password, email=email, given_name=givenname, family_name=familyname)
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
        print(val[1])
        return val[1]

    def add_user_to_group(self, username):
        groupname = 'PaidSubscribers'
        val = self.client.admin_add_user_to_group(username, groupname)
        val = self.client.admin_list_groups_for_user(username)
        print(val[1])
        return val[1]

    def remove_user_from_group(self, username):
        groupname = 'PaidSubscribers'
        val = self.client.admin_remove_user_from_group(username, groupname)
        val = self.client.admin_list_groups_for_user(username)
        print(val[1])
        return val[1]


class database_client_mongodb:

    def __init__(self, host, port):
        self.client = None
        self.host = host
        self.port = port

    def initialize(self):
        #mongo_client = MongoClient(self.host, self.port, username=config.CONFIG_MONGODB_USERNAME, password=config.CONFIG_MONGODB_PASSWORD)
        mongo_client = MongoClient(self.host, self.port)
        self.client = mongo_client[config.CONFIG_MONGODB_DB]
        self.client_packethistory = mongo_client[config.CONFIG_MONGODB_PACKETHISTORY_DB]


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
            for user in users.find({},{'username': 1}):
                #print(user)
                if user['username'] == username:
                    return True
        return False

    def find_email(self, email):
        users = self.get_registered_users()
        if users:
            for user in users.find({},{'email': 1}):
                #print(user)
                if user['email'] == email:
                    return user['username']
        return None

    def get_user_info(self, access_token):
        return None

    def login(self, username, password):
        users = self.get_registered_users()
        if users:
            for user in users.find({},{'username': 1, 'password':1, 'token':1}):
                if user['username'] == username and user['password'] == password:
                    return user['token']
        return None

    def logout(self, token):
        pass

    def verify_token(self, username, token):
        users = self.get_registered_users()
        if users:
            for user in users.find({},{'username': 1, 'token':1}):
                #print(user)
                if user['username'] == username and user['token'] == token:
                    return True
        return False

    def get_confirmationcode(self, username):
        users = self.get_registered_users()
        if users:
            for user in users.find({},{'username': 1, 'confirmationcode': 1}):
                #print(user)
                if user['username'] == username:
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
            for user in users.find({},{'username': 1, 'password': 1, 'email': 1, 'givenname': 1, 'familyname': 1, 'timestamp': 1, 'token': 1, 'status': 1, 'confirmationcode': 1 }):
                if user['username'] == username:
                    print(user)
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

    def get_history_document(self, deviceid):
        # separate collection per device
        return self.client_packethistory["{}_{}".format(config.CONFIG_MONGODB_TB_HISTORY, deviceid)]
        # one collection for all devices
        #return self.client[config.CONFIG_MONGODB_TB_HISTORY]

    def add_device_history(self, devicename, deviceid, topic, payload, direction):
        history = self.get_history_document(deviceid)
        timestamp = int(time.time())
        item = {}
        item['timestamp'] = timestamp
        item['direction'] = direction
        item['topic'] = topic
        item['payload'] = payload
        history.insert_one(item);

        # limit device history to CONFIG_MAX_HISTORY_PER_DEVICE for each devices
        if config.CONFIG_ENABLE_MAX_HISTORY:
            collectioname = "{}_{}".format(config.CONFIG_MONGODB_TB_HISTORY, deviceid)
            try:
                count = self.client_packethistory.command("collstats", collectioname)["count"]
            except:
                count = 0
            while count > config.CONFIG_MAX_HISTORY_PER_DEVICE:
                history.delete_one({})
                count -= 1

    def get_device_history(self, deviceid):
        history_list = []
        histories = self.get_history_document(deviceid)
        if histories:
            for history in histories.find({}):
                history.pop('_id')
                history_list.append(history)
        return history_list


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
            #print("update_device_notification insert_one")
            #print(found)
            notifications.insert_one(item)
        else:
            #print("update_device_notification replace_one")
            notifications.replace_one({'username': username, 'devicename': devicename, 'deviceid': deviceid, 'source': source}, item)

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
    # sensor readings
    ##########################################################

    def get_sensorreadings_document(self):
        return self.client[config.CONFIG_MONGODB_TB_SENSORREADINGS]

    def update_sensor_reading(self, deviceid, source, address, sensor_readings):
        sensorreadings = self.get_sensorreadings_document();
        item = {}
        item['deviceid'] = deviceid
        item['source'] = source
        item['address'] = address
        item['sensor_readings'] = sensor_readings
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
            sensorreadings.delete_many({'deviceid': deviceid, 'source': source, 'address': address})
        except:
            print("delete_sensor_reading: Exception occurred")
            pass

    def get_sensor_reading_by_deviceid(self, deviceid, source, address):
        sensorreadings = self.get_sensorreadings_document();
        if sensorreadings:
            for sensorreading in sensorreadings.find({'deviceid': deviceid, 'source': source, 'address': address}):
                sensorreading.pop('_id')
                #print(sensorreading['sensor_readings'])
                return sensorreading['sensor_readings']
        return None


    ##########################################################
    # devices
    ##########################################################

    def get_registered_devices(self):
        return self.client[config.CONFIG_MONGODB_TB_DEVICES]

    def display_devices(self, username):
        devices = self.get_registered_devices()
        if devices:
            for device in devices.find({},{'username': 1, 'devicename':1, 'deviceid': 1, 'timestamp':1, 'cert':1, 'pkey':1}):
                if device['username'] == username:
                    print(device)

    def get_devices(self, username):
        device_list = []
        devices = self.get_registered_devices()
        if devices and devices.count():
            for device in devices.find({'username': username},{'username': 1, 'devicename':1, 'deviceid': 1, 'timestamp':1, 'cert':1, 'pkey':1}):
                if device['username'] == username:
                    device.pop('username')
                    device.pop('timestamp')
                    device.pop('_id')
                    device_list.append(device)
                    #device_list.append(str(device))
        return device_list

    def add_device(self, username, devicename, cert, pkey):
        timestamp = int(time.time())
        deviceid = database_utils().compute_deviceid(timestamp, username, devicename)
        device = {}
        device['username']   = username
        device['devicename'] = devicename
        device['deviceid']   = deviceid
        device['timestamp']  = timestamp
        device['cert']       = cert
        device['pkey']       = pkey
        #print('post={}'.format(device))
        self.client.devices.insert_one(device)
        return deviceid

    def delete_device(self, username, devicename):
        devices = self.get_registered_devices()
        if devices:
            myquery = { 'username': username, 'devicename': devicename }
            devices.delete_one(myquery)

    def find_device(self, username, devicename):
        devices = self.get_registered_devices()
        if devices:
            for device in devices.find({},{'username': 1, 'devicename': 1, 'deviceid': 1, 'cert':1, 'pkey':1}):
                #print(user)
                if device['username'] == username and device['devicename'] == devicename:
                    device.pop('username')
                    device.pop('_id')
                    return device
        return None

    def get_deviceid(self, username, devicename):
        devices = self.get_registered_devices()
        if devices:
            for device in devices.find({},{'username': 1, 'devicename': 1, 'deviceid': 1}):
                #print(user)
                if device['username'] == username and device['devicename'] == devicename:
                    return device['deviceid']
        return None

    def add_device_heartbeat(self, deviceid):
        devices = self.get_registered_devices()
        if devices:
            for device in devices.find({'deviceid': deviceid}):
                new_device = copy.deepcopy(device)
                new_device['heartbeat'] = int(time.time())
                devices.replace_one(device, new_device)
                return new_device['heartbeat']
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
                                print("        deviceid  : {}".format(device["deviceid"]))
                                print("        timestamp : {}".format(self.epoch_to_datetime(device["timestamp"])))
                                if False:
                                    print("        cert      : {}...".format(device["cert"][28:68]))
                                    print("        pkey      : {}...".format(device["pkey"][28:68]))
                                else:
                                    print("        cert      : \r\n{}".format(device["cert"]))
                                    print("        pkey      : \r\n{}".format(device["pkey"]))
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
                            if device['username'] == user["username"]:
                                print("\r\n    DEVICENAME    : {}".format(device["devicename"]))
                                print("        deviceid  : {}".format(device["deviceid"]))
                                print("        timestamp : {}".format(self.epoch_to_datetime(device["timestamp"])))
                                if False:
                                    print("        cert      : {}...".format(device["cert"][28:68]))
                                    print("        pkey      : {}...".format(device["pkey"][28:68]))
                                else:
                                    print("        cert      : \r\n{}".format(device["cert"]))
                                    print("        pkey      : \r\n{}".format(device["pkey"]))
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
                for device in devices.find({},{'username': 1, 'devicename':1}):
                    if device['username'] == user["username"]:
                        self.client.delete_device(device['username'], device["devicename"])
                        print("Deleted device {}".format(device["devicename"]))
            self.client.delete_user(user["username"])
            print("Deleted user {}".format(user["username"]))


