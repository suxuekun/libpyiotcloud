from pymongo import MongoClient
from web_server_config import config



class database_client:

	def __init__(self):
		self.client = None

	def initialize(self):
		mongo_client = MongoClient(config.CONFIG_DB_HOST, config.CONFIG_DB_PORT)
		self.client = mongo_client['iotcloud-database']


	def compute_secret(self, timestamp, username, password):
		key = timestamp.encode('utf-8')
		message = (username + password).encode('utf-8')
		secret = hmac.new(key, message, hashlib.sha1).hexdigest()
		return secret

	def display_users(self):
		users = self.client['profiles']
		if users:
			for user in users.find({},{'username': 1, 'password':1, 'secret':1}):
				print(user)

	def find_user(self, username):
		users = self.client['profiles']
		if users:
			for user in users.find({},{'username': 1}):
				#print(user)
				if user['username'] == username:
					return True
		return False

	def check_password(self, username, password):
		users = self.client['profiles']
		if users:
			for user in users.find({},{'username': 1, 'password':1}):
				#print(user)
				if user['username'] == username and user['password'] == password:
					return True
		return False

	def get_secret(self, username):
		users = self.client['profiles']
		if users:
			for user in users.find({},{'username': 1, 'secret': 1}):
				#print(user)
				if user['username'] == username:
					return user['secret']
		return None

	def check_secret(self, username, secret):
		users = self.client['profiles']
		if users:
			for user in users.find({},{'username': 1, 'secret':1}):
				#print(user)
				if user['username'] == username and user['secret'] == secret:
					return True
		return False

	def delete_user(self, username):
		users = self.client['profiles']
		if users:
			myquery = { 'username': username }
			users.delete_one(myquery)

	def add_user(self, username, password):
		timestamp = str(int(time.time()))
		secret = compute_secret(timestamp, username, password)
		profile = {}
		profile['username']  = username
		profile['password']  = password
		profile['timestamp'] = timestamp
		profile['secret']    = secret
		#print('post={}'.format(profile))
		self.client.profiles.insert_one(profile)


	def compute_deviceid(self, timestamp, username, devicename):
		key = timestamp.encode('utf-8')
		message = (username + devicename).encode('utf-8')
		secret = hmac.new(key, message, hashlib.sha1).hexdigest()
		return secret

	def display_devices(self, username):
		devices = self.client['devices']
		if devices:
			for device in devices.find({},{'username': 1, 'devicename':1, 'deviceid': 1, 'timestamp':1, 'cert':1, 'pkey':1}):
				if device['username'] == username:
					print(device)

	def get_devices(self, username):
		device_list = []
		devices = self.client['devices']
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
		deviceid = compute_deviceid(timestamp, username, devicename)
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
		devices = self.client['devices']
		if devices:
			myquery = { 'username': username, 'devicename': devicename }
			devices.delete_one(myquery)

	def find_device(self, username, devicename):
		devices = self.client['devices']
		if devices:
			for device in devices.find({},{'username': 1, 'devicename': 1}):
				#print(user)
				if device['username'] == username and device['devicename'] == devicename:
					return True
		return False

	def get_deviceid(self, username, devicename):
		devices = self.client['devices']
		if devices:
			for device in devices.find({},{'username': 1, 'devicename': 1, 'deviceid': 1}):
				#print(user)
				if device['username'] == username and device['devicename'] == devicename:
					return device['deviceid']
		return None