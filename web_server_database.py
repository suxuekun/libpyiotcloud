import time
import hmac
import hashlib
import datetime
import random
from web_server_config import config
from pymongo import MongoClient # MongoDB
#import psycopg2                # PostgreSQL
from web_server_cognito_client import cognito_client



class database_models:

    MONGODB    = 0
    POSTGRESQL = 1



class database_client:

    def __init__(self, model=database_models.MONGODB):
        self.use_cognito = True
        if model == database_models.MONGODB:
            self._base = database_client_mongodb()
            if self.use_cognito:
                self._users = database_client_cognito()
        elif model == database_models.POSTGRESQL:
            self._base = database_client_postgresql()

    def initialize(self):
        self._base.initialize()
        if self.use_cognito:
            self._users.initialize()

    def is_using_cognito(self):
        return self.use_cognito


    ###################################################
    # users
    ###################################################

    def get_registered_users(self):
        if self.use_cognito:
            return self._users.get_registered_users()
        return self._base.get_registered_users()

    def find_user(self, username):
        if self.use_cognito:
            return self._users.find_user(username)
        return self._base.find_user(username)

    def login(self, username, password):
        if self.use_cognito:
            return self._users.login(username, password)
        return self._base.login(username, password)

    def verify_token(self, username, token):
        if self.use_cognito:
            return self._users.verify_token(username, token)
        return self._base.verify_token(username, token)

    def delete_user(self, username):
        if self.use_cognito:
            self._users.delete_user(username)
        self._base.delete_user(username)

    def add_user(self, username, password, email, givenname, familyname):
        if self.use_cognito:
            return self._users.add_user(username, password, email, givenname, familyname)
        return self._base.add_user(username, password, email, givenname, familyname)

    def confirm_user(self, username, confirmationcode):
        if self.use_cognito:
            return self._users.confirm_user(username, confirmationcode)
        return self._base.confirm_user(username, confirmationcode)

    def get_confirmationcode(self, username):
        if self.use_cognito:
            return self._users.get_confirmationcode(username)
        return self._base.get_confirmationcode(username)


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


    ###################################################
    # users
    ###################################################

    def get_registered_users(self):
        print("\r\nadmin_list_users")
        (result, users) = self.client.admin_list_users()
        print(result)
        if not result:
            return None
        return users

    def find_user(self, username):
        print("\r\nadmin_list_users")
        (result, users) = self.client.admin_list_users()
        print(result)
        if result == False:
            return True
        if users:
            for user in users:
                if user["username"] == username:
                    print("username: {} found!".format(username))
                    return True
        print("username: {} NOT found!".format(username))
        return False

    def login(self, username, password):
        print("\r\nlogin")
        (result, response) = self.client.login(username, password)
        print(result)
        if not result:
            return None
        self.access_token = response['AuthenticationResult']['AccessToken']
        print(self.access_token)
        return self.access_token

    def verify_token(self, username, token):
        print("\r\nverify_token")
        valid = self.client.verify_token(token, username)
        print("token is {}!".format("valid" if valid else "invalid"))
        return valid

    def get_confirmationcode(self, username):
        return None

    def delete_user(self, username):
        pass

    def add_user(self, username, password, email, givenname, familyname):
        print("\r\nsign_up")
        (result, response) = self.client.sign_up(username, password, email=email, given_name=givenname, family_name=familyname)
        print(result)
        return result

    def confirm_user(self, username, confirmationcode):
        print("\r\nconfirm_sign_up")
        (result, response) = self.client.confirm_sign_up(username, confirmationcode)
        print(result)
        return result


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

    def login(self, username, password):
        users = self.get_registered_users()
        if users:
            for user in users.find({},{'username': 1, 'password':1, 'token':1}):
                if user['username'] == username and user['password'] == password:
                    return user['token']
        return None

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
        #self.client = psycopg2.connect("dbname={} user=postgres password=1234".format(config.CONFIG_POSTGRESQL_DB))
        pass


class database_viewer:

    def __init__(self, model=database_models.MONGODB):
        self.client = database_client(model)
        self.client.initialize()

    def epoch_to_datetime(self, epoch):
        return datetime.datetime.fromtimestamp(int(epoch)).strftime('%Y-%m-%d %H:%M:%S')

    def show(self):
        users = self.client.get_registered_users()
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
                if devices:
                    for device in devices.find({},{'username': 1, 'devicename':1, 'deviceid': 1, 'timestamp':1, 'cert':1, 'pkey':1}):
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
                if devices:
                    for device in devices.find({},{'username': 1, 'devicename':1, 'deviceid': 1, 'timestamp':1, 'cert':1, 'pkey':1}):
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


    def reset(self):
        users = self.client.get_registered_users()
        for user in users.find({},{'username': 1}):
            devices = self.client.get_registered_devices()
            if devices:
                for device in devices.find({},{'username': 1, 'devicename':1}):
                    if device['username'] == user["username"]:
                        self.client.delete_device(device['username'], device["devicename"])
                        print("Deleted device {}".format(device["devicename"]))
            self.client.delete_user(user["username"])
            print("Deleted user {}".format(user["username"]))


