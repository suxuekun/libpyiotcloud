import time
import hmac
import hashlib
import datetime
from web_server_config import config
from pymongo import MongoClient # MongoDB
import psycopg2                 # PostgreSQL



class database_models:

    MONGODB    = 0
    POSTGRESQL = 1



class database_client:

    def __init__(self, model=database_models.MONGODB):
        if model == database_models.MONGODB:
            self._base = database_client_mongodb()
        elif model == database_models.POSTGRESQL:
            self._base = database_client_postgresql()

    def initialize(self):
        self._base.initialize()


    ###################################################
    # users
    ###################################################

    def display_users(self):
        self._base.display_users()

    def get_registered_users(self):
        return self._base.get_registered_users()

    def find_user(self, username):
        return self._base.find_user(username)

    def check_password(self, username, password):
        return self._base.check_password(username, password)

    def get_secret(self, username):
        return self._base.get_secret(username)

    def check_secret(self, username, secret):
        return self._base.check_secret(username, secret)

    def delete_user(self, username):
        self._base.delete_user(username)

    def add_user(self, username, password):
        self._base.add_user(username, password)


    ###################################################
    # devices
    ###################################################

    def display_devices(self, username):
        self._base.display_devices(username)

    def get_registered_devices(self):
        return self._base.get_registered_devices()

    def get_devices(self, username):
        return self._base.get_devices(username)

    def add_device(self, username, devicename, cert, pkey):
        return self._base.add_device(username, devicename, cert, pkey)

    def delete_device(self, username, devicename):
        self._base.delete_device(username, devicename)

    def find_device(self, username, devicename):
        return self._base.find_device(username, devicename)

    def get_deviceid(self, username, devicename):
        return self._base.get_deviceid(username, devicename)


class database_utils:

    def __init__(self):
        pass

    def compute_secret(self, timestamp, username, password):
        key = timestamp.encode('utf-8')
        message = (username + password).encode('utf-8')
        secret = hmac.new(key, message, hashlib.sha1).hexdigest()
        return secret

    def compute_deviceid(self, timestamp, username, devicename):
        key = timestamp.encode('utf-8')
        message = (username + devicename).encode('utf-8')
        deviceid = hmac.new(key, message, hashlib.sha1).hexdigest()
        return deviceid


class database_client_mongodb:

    def __init__(self):
        self.client = None

    def initialize(self):
        mongo_client = MongoClient(config.CONFIG_MONGODB_HOST, config.CONFIG_MONGODB_PORT)
        self.client = mongo_client[config.CONFIG_MONGODB_DB]


    ###################################################
    # users
    ###################################################

    def get_registered_users(self):
        return self.client[config.CONFIG_MONGODB_TB_PROFILES]

    def display_users(self):
        users = self.get_registered_users()
        if users:
            for user in users.find({},{'username': 1, 'password':1, 'secret':1}):
                print(user)

    def find_user(self, username):
        users = self.get_registered_users()
        if users:
            for user in users.find({},{'username': 1}):
                #print(user)
                if user['username'] == username:
                    return True
        return False

    def check_password(self, username, password):
        users = self.get_registered_users()
        if users:
            for user in users.find({},{'username': 1, 'password':1}):
                #print(user)
                if user['username'] == username and user['password'] == password:
                    return True
        return False

    def get_secret(self, username):
        users = self.get_registered_users()
        if users:
            for user in users.find({},{'username': 1, 'secret': 1}):
                #print(user)
                if user['username'] == username:
                    return user['secret']
        return None

    def check_secret(self, username, secret):
        users = self.get_registered_users()
        if users:
            for user in users.find({},{'username': 1, 'secret':1}):
                #print(user)
                if user['username'] == username and user['secret'] == secret:
                    return True
        return False

    def delete_user(self, username):
        users = self.get_registered_users()
        if users:
            myquery = { 'username': username }
            users.delete_one(myquery)

    def add_user(self, username, password):
        timestamp = str(int(time.time()))
        secret = database_utils().compute_secret(timestamp, username, password)
        profile = {}
        profile['username']  = username
        profile['password']  = password
        profile['timestamp'] = timestamp
        profile['secret']    = secret
        #print('post={}'.format(profile))
        self.client.profiles.insert_one(profile)


    ###################################################
    # devices
    ###################################################

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
        if devices:
            for device in devices.find({},{'username': 1, 'devicename':1, 'deviceid': 1, 'timestamp':1, 'cert':1, 'pkey':1}):
                if device['username'] == username:
                    device.pop('username')
                    device.pop('timestamp')
                    device.pop('_id')
                    device_list.append(device)
        return device_list

    def add_device(self, username, devicename, cert, pkey):
        timestamp = str(int(time.time()))
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
            for device in devices.find({},{'username': 1, 'devicename': 1}):
                #print(user)
                if device['username'] == username and device['devicename'] == devicename:
                    return True
        return False

    def get_deviceid(self, username, devicename):
        devices = self.get_registered_devices()
        if devices:
            for device in devices.find({},{'username': 1, 'devicename': 1, 'deviceid': 1}):
                #print(user)
                if device['username'] == username and device['devicename'] == devicename:
                    return device['deviceid']
        return None


class database_client_postgresql:

    def __init__(self):
        self.client = None

    def initialize(self):
        self.client = psycopg2.connect("dbname={} user=postgres password=1234".format(config.CONFIG_POSTGRESQL_DB))


class database_viewer:

    def __init__(self, model=database_models.MONGODB):
        self.client = database_client(model)
        self.client.initialize()

    def epoch_to_datetime(self, epoch):
        return datetime.datetime.fromtimestamp(int(epoch)).strftime('%Y-%m-%d %H:%M:%S')

    def show(self):
        users = self.client.get_registered_users()
        for user in users.find({},{'username': 1, 'password': 1, 'timestamp': 1, 'secret': 1}):
            print("USERNAME : {}".format(user["username"]))
            print("PASSWORD : {}".format(user["password"]))
            print("timestamp: {}".format(self.epoch_to_datetime(user["timestamp"])))
            print("secret   : {}".format(user["secret"]))
            print("devices  :")
            devices = self.client.get_registered_devices()
            if devices:
                for device in devices.find({},{'username': 1, 'devicename':1, 'deviceid': 1, 'timestamp':1, 'cert':1, 'pkey':1}):
                    if device['username'] == user["username"]:
                        print("    DEVICENAME    : {}".format(device["devicename"]))
                        print("        deviceid  : {}".format(device["deviceid"]))
                        print("        timestamp : {}".format(self.epoch_to_datetime(device["timestamp"])))
                        if True:
                            print("        cert      : {}...".format(device["cert"][28:68]))
                            print("        pkey      : {}...".format(device["pkey"][28:68]))
                        else:
                            print("        cert      : {}".format(device["cert"]))
                            print("        pkey      : {}".format(device["pkey"]))


