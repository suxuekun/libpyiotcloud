import redis
from rest_api_config import config





###################################################################################
# Some configurations
###################################################################################

IDP_CODE              = "idp:id:code"
IDP_CODE_EXPIRY       = 3600

PAYPAL_PAYERID        = "paypal:paymentid:payerid"
PAYPAL_PAYERID_EXPIRY = 3600



class redis_client:

	def __init__(self):
		pass

	def initialize(self):
		print("initialize")
		self.client = redis.Redis(config.CONFIG_REDIS_HOST, config.CONFIG_REDIS_PORT, 0, charset="utf-8", decode_responses=True)
		print(self.client)


	#
	# idp code for social idp login via facebook, google, amazon
	#

	def idp_set_code(self, id, code):
		print("idp_set_code")
		self.client.setex("{}:{}".format(IDP_CODE, id), IDP_CODE_EXPIRY, code)

	def idp_get_code(self, id):
		print("idp_get_code")
		return self.client.get("{}:{}".format(IDP_CODE, id))

	def idp_del_code(self, id):
		self.client.delete("{}:{}".format(IDP_CODE, id))


	#
	# paypal payerid
	#

	def paypal_set_payerid(self, paymentid, payerid):
		self.client.setex("{}:{}".format(PAYPAL_PAYERID, paymentid), PAYPAL_PAYERID_EXPIRY, payerid)

	def paypal_get_payerid(self, paymentid):
		return self.client.get("{}:{}".format(PAYPAL_PAYERID, paymentid))

	def paypal_del_payerid(self, paymentid):
		self.client.delete("{}:{}".format(PAYPAL_PAYERID, paymentid))


	#
	# tester
	#

	def test(self):
		print(self.idp_get_code("1234"))
		self.idp_set_code("1234", "lkjlkjsladsd")
		print(self.idp_get_code("1234"))
		self.idp_del_code("1234")
		print(self.idp_get_code("1234"))

		print(self.paypal_get_payerid("1234"))
		self.paypal_set_payerid("1234", "lkjlkjsladsd")
		print(self.paypal_get_payerid("1234"))
		self.paypal_del_payerid("1234")
		print(self.paypal_get_payerid("1234"))


#g_redis_client = redis_client()
#g_redis_client.initialize()
#g_redis_client.test()
