from OpenSSL import crypto
import random
import time



###################################################################################
CONFIG_CERT_DIRECTORY  = "cert/"
CONFIG_ROOTCA_CERT     = "rootca.pem"
CONFIG_ROOTCA_KEY      = "rootca_pkey.pem"
CONFIG_CERT_YEARS      = 1
CONFIG_CERT_COUNTRY    = "SG"
CONFIG_CERT_STATE      = "Singapore"
CONFIG_CERT_CITY       = "Paya Lebar"
CONFIG_CERT_COMPANY    = "Bridgetek Pte Ltd"
CONFIG_CERT_DEPARTMENT = "Engineering"
CONFIG_CERT_EMAIL      = "support.emea@brtchip.com"
###################################################################################



class certificate_generator:

	def __init__(self):

		# Root CA certificate
		st_cert=open(self.getca(), 'rt').read()
		self.ca_cert=crypto.load_certificate(crypto.FILETYPE_PEM, st_cert)

		# Root CA private key
		st_key=open(CONFIG_CERT_DIRECTORY + CONFIG_ROOTCA_KEY, 'rt').read()
		self.ca_key=crypto.load_privatekey(crypto.FILETYPE_PEM, st_key)
		self.ca_subj = self.ca_cert.get_subject()

	def generate(self, device_id):

		# Device client certificate
		client_key = crypto.PKey()
		client_key.generate_key(crypto.TYPE_RSA, 2048)
		client_cert = crypto.X509()
		client_cert.set_version(0)
		client_cert.set_serial_number(random.getrandbits(8*9))
		client_subj = client_cert.get_subject()
		client_cert.set_issuer(self.ca_subj)
		client_cert.set_pubkey(client_key)
		client_cert.gmtime_adj_notBefore(0)
		client_cert.gmtime_adj_notAfter(CONFIG_CERT_YEARS*365*24*60*60)
		client_cert.get_subject().C = CONFIG_CERT_COUNTRY
		client_cert.get_subject().ST = CONFIG_CERT_STATE
		client_cert.get_subject().L = CONFIG_CERT_CITY
		client_cert.get_subject().O = CONFIG_CERT_COMPANY
		client_cert.get_subject().OU = CONFIG_CERT_DEPARTMENT
		client_cert.get_subject().CN = device_id
		client_cert.sign(self.ca_key, 'sha256')

		# Get epoch time as timestamp
		timestamp = str(int(time.time()))

		# Save certificate
		filename_cert = CONFIG_CERT_DIRECTORY + device_id + "_" + timestamp + "_cert.pem"
		with open(filename_cert, "wt") as f:
			f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, client_cert).decode("utf-8"))

		# Save private key
		filename_pkey = CONFIG_CERT_DIRECTORY + device_id + "_" + timestamp + "_pkey.pem"
		with open(filename_pkey, "wt") as f:
			f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, client_key).decode("utf-8"))

		return filename_cert, filename_pkey

	def getca(self):
		return CONFIG_CERT_DIRECTORY + CONFIG_ROOTCA_CERT

	def test(self):
		device_id = "mydevice"
		cert = certificate_generator()
		filename_cert, filename_pkey = cert.generate(device_id)
		print(filename_cert)
		print(filename_pkey)

