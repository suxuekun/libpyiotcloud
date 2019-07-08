import http.client
import ssl
import json
import time
from client_config import config



###################################################################################
# Initialize context
###################################################################################

def initialize_http_connection():
	if config.CONFIG_USE_TLS:
		if True:
			context = ssl._create_unverified_context()
		else:
			context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
			context.verify_mode = ssl.CERT_REQUIRED
			context.load_cert_chain(config.CONFIG_TLS_CERT, config.CONFIG_TLS_PKEY)
			#context.load_verify_locations(
			#	config.CONFIG_TLS_CERT, config.CONFIG_TLS_CERT, config.CONFIG_TLS_PKEY)
			#context.check_hostname = False
		conn = http.client.HTTPSConnection(config.CONFIG_HOST, config.CONFIG_TLS_PORT, context=context)
	else:
		conn = http.client.HTTPConnection(config.CONFIG_HOST, config.CONFIG_PORT)
	return conn



###################################################################################
# Send HTTP request
###################################################################################

def request(conn, req_type, req_api, params, headers):
	try:
		if headers:
			conn.request(req_type, req_api, params, headers)
		else:
			conn.request(req_type, req_api, params)
		return True
	except:
		print("REQ: Could not communicate with WEBSERVER! {}".format(""))
	return False

def response(conn):
	try:
		r1 = conn.getresponse()
		if r1.status == 200:
			#print("response = {} {} [{}]".format(r1.status, r1.reason, r1.length))
			if r1.length:
				data = r1.read(r1.length)
			return data.decode("utf-8")
		else:
			print("RES: Could not communicate with DEVICE! {}".format(r1.status))
			return None
	except:
		print("RES: Could not communicate with DEVICE! {}".format(""))
	return None

def get_default_headers():
	headers = {"Content-type": "application/json", "Accept": "text/plain"}
	return headers



###################################################################################
# REST APIs
###################################################################################

def signup(conn, username, password, email, givenname, familyname):
	print("\r\nsignup {} {}".format(username, password, email, givenname, familyname))
	headers = get_default_headers()
	params = {}
	params['username'] = username
	params['password'] = password
	params['email'] = email
	params['givenname'] = givenname
	params['familyname'] = familyname
	params = json.dumps(params)
	request(conn, "POST", "/signup", params, headers)
	status = response(conn)
	return status

def confirm_signup(conn, username, confirmation_code):
	print("\r\nconfirm_signup {} {}".format(username, confirmation_code))
	headers = get_default_headers()
	params = {}
	params['username'] = username
	params['confirmationcode'] = confirmation_code
	params = json.dumps(params)
	request(conn, "POST", "/confirm_signup", params, headers)
	status = response(conn)
	return status

def login(conn, username, password):
	print("\r\nlogin {} {}".format(username, password))
	headers = get_default_headers()
	params = {}
	params['username'] = username
	params['password'] = password
	params = json.dumps(params)
	request(conn, "POST", "/login", params, headers)
	token = response(conn)
	token = json.loads(token)
	return token['token']

######################################################
def get_default_params(username, token, devicename):
	params = {}
	params['username'] = username
	params['token'] = token
	params['devicename'] = devicename
	return params

def get_default_params_ex(username, token, devicename):
	params = {}
	params['username'] = username
	params['token'] = token
	params['devicename'] = devicename
	return params

######################################################
def get_device_list(conn, username, token):
	print("\r\nget_device_list {} {}".format(username, token))
	headers = get_default_headers()
	params = {}
	params['username'] = username
	params['token'] = token
	params = json.dumps(params)
	request(conn, "GET", "/get_device_list", params, headers)
	devices = response(conn)
	return devices

def register_device(conn, username, token, devicename):
	print("\r\nregister_device {} {} {}".format(username, token, devicename))
	headers = get_default_headers()
	params = get_default_params(username, token, devicename)
	params = json.dumps(params)
	request(conn, "POST", "/register_device", params, headers)
	certificates = response(conn)
	return certificates

def unregister_device(conn, username, token, devicename):
	print("\r\nunregister_device {} {}".format(username, token, devicename))
	headers = get_default_headers()
	params = get_default_params(username, token, devicename)
	params = json.dumps(params)
	request(conn, "POST", "/unregister_device", params, headers)
	certificates = response(conn)
	return certificates

######################################################
def get_gpio(conn, username, token, devicename, number):
	print("\r\nget_gpio {} {} {}".format(username, devicename, number))
	headers = get_default_headers()
	params = get_default_params(username, token, devicename)
	params['number'] = number
	params = json.dumps(params)
	request(conn, "GET", "/get_gpio", params, headers)
	value = response(conn)
	value = json.loads(value)
	return int(value['value'])

def set_gpio(conn, username, token, devicename, number, value):
	print("\r\nset_gpio {} {} {} {}".format(username, devicename, number, value))
	headers = get_default_headers()
	params = get_default_params(username, token, devicename)
	params['number'] = number
	params['value'] = value
	params = json.dumps(params)
	request(conn, "POST", "/set_gpio", params, headers)
	response(conn)

######################################################
def get_rtc(conn, username, token, devicename):
	print("\r\nget_rtc {}".format(devicename))
	headers = get_default_headers()
	params = get_default_params(username, token, devicename)
	params = json.dumps(params)
	request(conn, "GET", "/get_rtc", params, headers)
	value = response(conn)
	value = json.loads(value)
	return int(value['value'])

def set_rtc(conn, username, token, devicename, epoch):
	print("\r\nset_rtc {} {}".format(devicename, epoch))
	headers = get_default_headers()
	params = get_default_params(username, token, devicename)
	params['value'] = epoch
	params = json.dumps(params)
	request(conn, "POST", "/set_rtc", params, headers)
	response(conn)

######################################################
def get_status(conn, username, token, devicename):
	print("\r\nget_status {}".format(devicename))
	headers = get_default_headers()
	params = get_default_params(username, token, devicename)
	params = json.dumps(params)
	if request(conn, "GET", "/get_status", params, headers):
		status = response(conn)
		if status:
			status = json.loads(status)
			return status['status']
		else:
			return "Not running"
	else:
		return "Unknown"
def restart_device(conn, username, token, devicename):
	print("\r\nrestart_device {}".format(devicename))
	headers = get_default_headers()
	params = get_default_params(username, token, devicename)
	params['status'] = 'restart'
	params = json.dumps(params)
	request(conn, "POST", "/set_status", params, headers)
	status = response(conn)
	status = json.loads(status)
	return status['status']

######################################################
def get_mac(conn, username, token, devicename):
	print("\r\nget_mac {}".format(devicename))
	headers = get_default_headers()
	params = get_default_params(username, token, devicename)
	params = json.dumps(params)
	request(conn, "GET", "/get_mac", params, headers)
	value = response(conn)
	value = json.loads(value)
	return value['value']

def set_mac(conn, username, token, devicename, mac):
	print("\r\nset_mac {} {}".format(devicename, mac))
	headers = get_default_headers()
	params = get_default_params(username, token, devicename)
	params['value'] = mac
	params = json.dumps(params)
	request(conn, "POST", "/set_mac", params, headers)
	value = response(conn)
	value = json.loads(value)
	return value['value']

######################################################
def get_ip(conn, username, token, devicename):
	print("\r\nget_ip {}".format(devicename))
	headers = get_default_headers()
	params = get_default_params(username, token, devicename)
	params = json.dumps(params)
	request(conn, "GET", "/get_ip", params, headers)
	value = response(conn)
	value = json.loads(value)
	return value['value']

def get_subnet(conn, username, token, devicename):
	print("\r\nget_subnet {}".format(devicename))
	headers = get_default_headers()
	params = get_default_params(username, token, devicename)
	params = json.dumps(params)
	request(conn, "GET", "/get_subnet", params, headers)
	value = response(conn)
	value = json.loads(value)
	return value['value']

def get_gateway(conn, username, token, devicename):
	print("\r\nget_gateway {}".format(devicename))
	headers = get_default_headers()
	params = get_default_params(username, token, devicename)
	params = json.dumps(params)
	request(conn, "GET", "/get_gateway", params, headers)
	value = response(conn)
	value = json.loads(value)
	return value['value']

######################################################
def write_uart(conn, username, token, devicename, data):
	print("\r\nwrite_uart {} {}".format(devicename, data))
	headers = get_default_headers()
	params = get_default_params(username, token, devicename)
	params['data'] = data
	params = json.dumps(params)
	request(conn, "POST", "/write_uart", params, headers)
	data = response(conn)
	data = json.loads(data)
	return data['data']

######################################################
def get_index(conn):
	headers = None
	params = None
	request(conn, "GET", "/", params, headers)




def test(conn, username, token, devicename):

	print("\r\nTesting {} {} {}".format(username, token, devicename))

	######################################################
	# Test get_status
	if True:
		status = get_status(conn, username, token, devicename)
		if status == "Not running" or status == "Unknown":
			return

	######################################################
	# Test write_uart
	if True:
		data = "Hello World!"
		data = write_uart(conn, username, token, devicename, data)
		print(data)

	######################################################
	# Test get_gpio and set_gpio
	if True:
		start_time = time.time()
		value = get_gpio(conn, username, token, devicename, 12)
		elapsed_time = time.time() - start_time
		print(elapsed_time)

		start_time = time.time()
		set_gpio(conn, username, token, devicename, 12, 0)
		elapsed_time = time.time() - start_time
		print(elapsed_time)

		start_time = time.time()
		value = get_gpio(conn, username, token, devicename, 12)
		elapsed_time = time.time() - start_time
		print(elapsed_time)

		start_time = time.time()
		set_gpio(conn, username, token, devicename, 12, 1)
		elapsed_time = time.time() - start_time
		print(elapsed_time)

		start_time = time.time()
		value = get_gpio(conn, username, token, devicename, 12)
		elapsed_time = time.time() - start_time
		print(elapsed_time)


	######################################################
	# Test get_rtc and set_rtc
	if True:
		start_time = time.time()
		epoch = get_rtc(conn, username, token, devicename)
		elapsed_time = time.time() - start_time
		print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch)))
		
		epoch = int(time.time())
		start_time = time.time()
		set_rtc(conn, username, token, devicename, epoch)
		elapsed_time = time.time() - start_time
		
		start_time = time.time()
		epoch = get_rtc(conn, username, token, devicename)
		elapsed_time = time.time() - start_time
		print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch)))


	######################################################
	# Test get_mac, get_ip, get_subnet, get_gateway
	if True:
		mac = get_mac(conn, username, token, devicename)
		print(mac)

		ip = get_ip(conn, username, token, devicename)
		print(ip)

		subnet = get_subnet(conn, username, token, devicename)
		print(subnet)

		gateway = get_gateway(conn, username, token, devicename)
		print(gateway)


	######################################################
	# Test restart_device
	if True:
		status = restart_device(conn, username, token, devicename)
		print(status)


###################################################################################
# Demo REST APIs
###################################################################################

def main():

	conn = initialize_http_connection()


	username = "richmondu"
	password = "P@$$w0rd"
	email = "richmond.umagat@yahoo.com"
	givenname = "Richmond"
	familyname = "Umagat"


	#####################################################
	# Test user registration
	#####################################################

	use_cognito = True

	if use_cognito:
		if False:
			status = signup(conn, username, password, email, givenname, familyname)
			print(status)
			status = json.loads(status)
			if status["status"] != "OK":
				return
			print("Check email for the confirmation code!")

		if False:
			confirmation_code = "952525"
			status = confirm_signup(conn, username, confirmation_code)
			print(status)

		if True:
			token = login(conn, username, password)
			print("token = {}".format(token))
	else:
		if True:
			status = signup(conn, username, password, email, givenname, familyname)
			print(status)
			status = json.loads(status)
			if status["status"] == "OK":
				confirmation_code = status["confirmationcode"]

				status = confirm_signup(conn, username, confirmation_code)
				print(status)

			token = login(conn, username, password)
			print("token = {}".format(token))



	#####################################################
	# Test device list
	#####################################################

	if True:
		devices = get_device_list(conn, username, token)
		print(devices)
		devices = json.loads(devices)
		if devices["status"] != "OK":
			return
		devices = devices["devices"]

	#####################################################
	# Test device register
	#####################################################

	if False:
		devicename = "ft900device1"
		certificates = register_device(conn, username, token, devicename)
		print(certificates)

		devicename = "ft900device2"
		certificates = register_device(conn, username, token, devicename)
		print(certificates)

		devices = get_device_list(conn, username, token)
		devices = json.loads(devices)
		if devices["status"] != "OK":
			return
		devices = devices["devices"]


	#####################################################
	# Test device APIs
	#####################################################

	if True:
		for device in devices:
			devicename = device["devicename"]
			test(conn, username, token, devicename)

#		devicename = "ft900device1"
#		test(conn, username, token, devicename)
#		devicename = "ft900device2"
#		test(conn, username, token, devicename)


	#####################################################
	# Test device unregister
	#####################################################
	
	if False:
		devicename = "ft900device1"
		certificates = unregister_device(conn, username, token, devicename)
		print(certificates)

		devicename = "ft900device2"
		certificates = unregister_device(conn, username, token, devicename)
		print(certificates)

		devices = get_device_list(conn, username, token)
		print(devices)



if __name__ == '__main__':
	main()
