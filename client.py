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
		#context.load_verify_locations(CONFIG_HTTP_TLS_CERT, CONFIG_HTTP_TLS_CERT, CONFIG_HTTP_TLS_PKEY)
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

def register_device(conn, device_name):
	print("\r\nregister_device {}".format(device_name))
	headers = get_default_headers()
	params = {}
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

def get_gpio(conn, device_name, number):
	print("\r\nget_gpio {} {}".format(device_name, number))
	headers = get_default_headers()
	params = {}
	params['device_name'] = device_name
	params['number'] = number
	params = json.dumps(params)
	request(conn, "GET", "/get_gpio", params, headers)
	value = response(conn)
	value = json.loads(value)
	return int(value['value'])

def set_gpio(conn, device_name, number, value):
	print("\r\nset_gpio {} {} {}".format(device_name, number, value))
	headers = get_default_headers()
	params = {}
	params['device_name'] = device_name
	params['number'] = number
	params['value'] = value
	params = json.dumps(params)
	request(conn, "POST", "/set_gpio", params, headers)
	response(conn)

def get_rtc(conn, device_name):
	print("\r\nget_rtc {}".format(device_name))
	headers = get_default_headers()
	params = {}
	params['device_name'] = device_name
	params = json.dumps(params)
	request(conn, "GET", "/get_rtc", params, headers)
	value = response(conn)
	value = json.loads(value)
	return int(value['value'])

def set_rtc(conn, device_name, epoch):
	print("\r\nset_rtc {} {}".format(device_name, epoch))
	headers = get_default_headers()
	params = {}
	params['device_name'] = device_name
	params['value'] = epoch
	params = json.dumps(params)
	request(conn, "POST", "/set_rtc", params, headers)
	response(conn)

def get_status(conn, device_name):
	print("\r\nget_status {}".format(device_name))
	headers = get_default_headers()
	params = {}
	params['device_name'] = device_name
	params = json.dumps(params)
	request(conn, "GET", "/get_status", params, headers)
	status = response(conn)
	status = json.loads(status)
	return status['status']

def restart_device(conn, device_name):
	print("\r\nrestart_device {}".format(device_name))
	headers = get_default_headers()
	params = {}
	params['device_name'] = device_name
	params['status'] = 'restart'
	params = json.dumps(params)
	request(conn, "POST", "/set_status", params, headers)
	status = response(conn)
	status = json.loads(status)
	return status['status']

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

	device_name = "ft900device1"

	if True:
		start_time = time.time()
		certificates = register_device(conn, device_name)
		elapsed_time = time.time() - start_time
		print(elapsed_time)
		print(certificates)
		#unregister_device(conn, device_name)

	if True:
		start_time = time.time()
		value = get_gpio(conn, device_name, 12)
		elapsed_time = time.time() - start_time
		print(elapsed_time)

		start_time = time.time()
		set_gpio(conn, device_name, 12, 0)
		elapsed_time = time.time() - start_time
		print(elapsed_time)

		start_time = time.time()
		value = get_gpio(conn, device_name, 12)
		elapsed_time = time.time() - start_time
		print(elapsed_time)

		start_time = time.time()
		set_gpio(conn, device_name, 12, 1)
		elapsed_time = time.time() - start_time
		print(elapsed_time)

		start_time = time.time()
		value = get_gpio(conn, device_name, 12)
		elapsed_time = time.time() - start_time
		print(elapsed_time)

	if True:
		start_time = time.time()
		epoch = get_rtc(conn, device_name)
		elapsed_time = time.time() - start_time
		print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch)))
		
		epoch = int(time.time())
		start_time = time.time()
		set_rtc(conn, device_name, epoch)
		elapsed_time = time.time() - start_time
		
		start_time = time.time()
		epoch = get_rtc(conn, device_name)
		elapsed_time = time.time() - start_time
		print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch)))
	
	if True:
		status = get_status(conn, device_name)
		print(status)
		status = restart_device(conn, device_name)
		print(status)


if __name__ == '__main__':
	main()
