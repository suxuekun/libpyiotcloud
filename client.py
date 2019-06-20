import http.client
import ssl
import json
import time



###################################################################################
# HTTP configurations
###################################################################################

CONFIG_HTTP_HOST     = "localhost"
CONFIG_HTTP_PORT     = 443
CONFIG_HTTP_TLS_CERT = "cert/ft900device1_cert.pem"
CONFIG_HTTP_TLS_PKEY = "cert/ft900device1_pkey.pem"



###################################################################################
# Initialize context
###################################################################################

def initialize_context():
	if True:
		context = ssl._create_unverified_context()
	else:
		context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
		context.verify_mode = ssl.CERT_REQUIRED
		context.load_cert_chain(CONFIG_HTTP_TLS_CERT, CONFIG_HTTP_TLS_PKEY)
		#context.load_verify_locations(
		#	CONFIG_HTTP_TLS_CERT, CONFIG_HTTP_TLS_CERT, CONFIG_HTTP_TLS_PKEY)
		#context.check_hostname = False
	return context



###################################################################################
# Send HTTP request
###################################################################################

def request(conn, req_type, req_api, params, headers):
	if headers:
		conn.request(req_type, req_api, params, headers)
	else:
		conn.request(req_type, req_api, params)

def response(conn):
	r1 = conn.getresponse()
	#print("response = {} {} [{}]".format(r1.status, r1.reason, r1.length))
	if r1.length:
		data = r1.read(r1.length)
	return data.decode("utf-8")

def get_default_headers():
	headers = {"Content-type": "application/json", "Accept": "text/plain"}
	return headers



###################################################################################
# REST APIs
###################################################################################

######################################################
def register_device(conn, customer_id, device_name):
	print("\r\nregister_device {}".format(device_name))
	headers = get_default_headers()
	params = {}
	params['customer_id'] = customer_id
	params['device_name'] = device_name
	params = json.dumps(params)
	request(conn, "POST", "/register_device", params, headers)
	certificates = response(conn)
	return certificates

def unregister_device(conn, device_name):
	print("\r\nunregister_device {}".format(device_name))
	headers = get_default_headers()
	params = {}
	params['device_name'] = device_name
	params = json.dumps(params)
	request(conn, "POST", "/unregister_device", params, headers)

######################################################
def get_gpio(conn, customer_id, device_name, number):
	print("\r\nget_gpio {} {} {}".format(customer_id, device_name, number))
	headers = get_default_headers()
	params = {}
	params['customer_id'] = customer_id
	params['device_name'] = device_name
	params['number'] = number
	params = json.dumps(params)
	request(conn, "GET", "/get_gpio", params, headers)
	value = response(conn)
	value = json.loads(value)
	return int(value['value'])

def set_gpio(conn, customer_id, device_name, number, value):
	print("\r\nset_gpio {} {} {} {}".format(customer_id, device_name, number, value))
	headers = get_default_headers()
	params = {}
	params['customer_id'] = customer_id
	params['device_name'] = device_name
	params['number'] = number
	params['value'] = value
	params = json.dumps(params)
	request(conn, "POST", "/set_gpio", params, headers)
	response(conn)

######################################################
def get_rtc(conn, customer_id, device_name):
	print("\r\nget_rtc {}".format(device_name))
	headers = get_default_headers()
	params = {}
	params['customer_id'] = customer_id
	params['device_name'] = device_name
	params = json.dumps(params)
	request(conn, "GET", "/get_rtc", params, headers)
	value = response(conn)
	value = json.loads(value)
	return int(value['value'])

def set_rtc(conn, customer_id, device_name, epoch):
	print("\r\nset_rtc {} {}".format(device_name, epoch))
	headers = get_default_headers()
	params = {}
	params['customer_id'] = customer_id
	params['device_name'] = device_name
	params['value'] = epoch
	params = json.dumps(params)
	request(conn, "POST", "/set_rtc", params, headers)
	response(conn)

######################################################
def get_status(conn, customer_id, device_name):
	print("\r\nget_status {}".format(device_name))
	headers = get_default_headers()
	params = {}
	params['customer_id'] = customer_id
	params['device_name'] = device_name
	params = json.dumps(params)
	request(conn, "GET", "/get_status", params, headers)
	status = response(conn)
	status = json.loads(status)
	return status['status']

def restart_device(conn, customer_id, device_name):
	print("\r\nrestart_device {}".format(device_name))
	headers = get_default_headers()
	params = {}
	params['customer_id'] = customer_id
	params['device_name'] = device_name
	params['status'] = 'restart'
	params = json.dumps(params)
	request(conn, "POST", "/set_status", params, headers)
	status = response(conn)
	status = json.loads(status)
	return status['status']

######################################################
def get_mac(conn, customer_id, device_name):
	print("\r\nget_mac {}".format(device_name))
	headers = get_default_headers()
	params = {}
	params['customer_id'] = customer_id
	params['device_name'] = device_name
	params = json.dumps(params)
	request(conn, "GET", "/get_mac", params, headers)
	value = response(conn)
	value = json.loads(value)
	return value['value']

def set_mac(conn, customer_id, device_name, mac):
	print("\r\nset_mac {} {}".format(device_name, mac))
	headers = get_default_headers()
	params = {}
	params['customer_id'] = customer_id
	params['device_name'] = device_name
	params['value'] = mac
	params = json.dumps(params)
	request(conn, "POST", "/set_mac", params, headers)
	value = response(conn)
	value = json.loads(value)
	return value['value']

######################################################
def get_ip(conn, customer_id, device_name):
	print("\r\nget_ip {}".format(device_name))
	headers = get_default_headers()
	params = {}
	params['customer_id'] = customer_id
	params['device_name'] = device_name
	params = json.dumps(params)
	request(conn, "GET", "/get_ip", params, headers)
	value = response(conn)
	value = json.loads(value)
	return value['value']

def get_subnet(conn, customer_id, device_name):
	print("\r\nget_subnet {}".format(device_name))
	headers = get_default_headers()
	params = {}
	params['customer_id'] = customer_id
	params['device_name'] = device_name
	params = json.dumps(params)
	request(conn, "GET", "/get_subnet", params, headers)
	value = response(conn)
	value = json.loads(value)
	return value['value']

def get_gateway(conn, customer_id, device_name):
	print("\r\nget_gateway {}".format(device_name))
	headers = get_default_headers()
	params = {}
	params['customer_id'] = customer_id
	params['device_name'] = device_name
	params = json.dumps(params)
	request(conn, "GET", "/get_gateway", params, headers)
	value = response(conn)
	value = json.loads(value)
	return value['value']

######################################################
def get_index(conn):
	headers = None
	params = None
	request(conn, "GET", "/", params, headers)



###################################################################################
# Demo REST APIs
###################################################################################

def main():

	conn = http.client.HTTPSConnection(
		CONFIG_HTTP_HOST, 
		CONFIG_HTTP_PORT, 
		context=initialize_context())

	customer_id = "richmond_umagat@brtchip_com"
	device_name = "ft900device1"


	######################################################
	# Test register_device
	if True:
		start_time = time.time()
		certificates = register_device(conn, customer_id, device_name)
		elapsed_time = time.time() - start_time
		print(elapsed_time)
		print(certificates)
		#unregister_device(conn, device_name)


	######################################################
	# Test get_gpio and set_gpio
	if True:
		start_time = time.time()
		value = get_gpio(conn, customer_id, device_name, 12)
		elapsed_time = time.time() - start_time
		print(elapsed_time)

		start_time = time.time()
		set_gpio(conn, customer_id, device_name, 12, 0)
		elapsed_time = time.time() - start_time
		print(elapsed_time)

		start_time = time.time()
		value = get_gpio(conn, customer_id, device_name, 12)
		elapsed_time = time.time() - start_time
		print(elapsed_time)

		start_time = time.time()
		set_gpio(conn, customer_id, device_name, 12, 1)
		elapsed_time = time.time() - start_time
		print(elapsed_time)

		start_time = time.time()
		value = get_gpio(conn, customer_id, device_name, 12)
		elapsed_time = time.time() - start_time
		print(elapsed_time)


	######################################################
	# Test get_rtc and set_rtc
	if True:
		start_time = time.time()
		epoch = get_rtc(conn, customer_id, device_name)
		elapsed_time = time.time() - start_time
		print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch)))
		
		epoch = int(time.time())
		start_time = time.time()
		set_rtc(conn, customer_id, device_name, epoch)
		elapsed_time = time.time() - start_time
		
		start_time = time.time()
		epoch = get_rtc(conn, customer_id, device_name)
		elapsed_time = time.time() - start_time
		print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch)))


	######################################################
	# Test get_mac, get_ip, get_subnet, get_gateway
	if True:
		mac = get_mac(conn, customer_id, device_name)
		print(mac)

		ip = get_ip(conn, customer_id, device_name)
		print(ip)

		subnet = get_subnet(conn, customer_id, device_name)
		print(subnet)

		gateway = get_gateway(conn, customer_id, device_name)
		print(gateway)

		#mac = "00:11:22:33:44:55"
		#mac = set_mac(conn, device_name, mac)
		#print(mac)
		#time.sleep(3)
		#status = restart_device(conn, device_name)
		#print(status)


	######################################################
	# Test get_status and restart_device
	if True:
		status = get_status(conn, customer_id, device_name)
		print(status)
		status = restart_device(conn, customer_id, device_name)
		print(status)


if __name__ == '__main__':
	main()
