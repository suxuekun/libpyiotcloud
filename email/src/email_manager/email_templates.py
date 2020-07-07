class email_templates:

	def construct_invoice_message(self, name, payment):

		message =  "Hi {},\r\n\r\n\r\n".format(name)

		message += "A Paypal payment of {} USD for {} credits was processed successfully.\r\n".format(payment["amount"], payment["value"])
		message += "To confirm your Paypal transaction, visit the Paypal website and check the transaction ID: {}.\r\n\r\n".format(payment["id"])

		message += "If unauthorised, please contact customer support.\r\n\r\n"

		message += "\r\nBest Regards,\r\n"
		message += "Bridgetek Pte. Ltd.\r\n"
		return message

	def construct_invitation_organization_message(self, orgname, orgowner):

		message =  "Hi,\r\n\r\n\r\n"

		message += "You have been invited to join the {} organization by {}.\r\n".format(orgname, orgowner)
		message += "This allows you to manage, operate, monitor or view IoT gateway devices of your organization based on assigned roles and permissions.\r\n\r\n"

		message += "Please download the Bridgetek IoT Portal mobile app or visit the website:\r\n".format(CONFIG_USE_APIURL)
		message += "- Android app at Google Play\r\n"
		message += "- iOS app at Apple App Store\r\n"
		message += "- Website at https://{}\r\n".format(CONFIG_USE_APIURL)
		message += "If you don't have an account yet, sign up for an account then go to the Organization page to accept the invitation.\r\n\r\n"

		message += "\r\nBest Regards,\r\n"
		message += "Bridgetek Pte. Ltd.\r\n"
		return message

	def construct_usage_notice_message(self, deviceid, menos_type, subscription):

		message =  "Hi,\r\n\r\n\r\n"

		message += "One of your devices with UUID {} has consumed all its {} allocation.\r\n\r\n".format(deviceid, menos_type)

		message += "Below is usage summary of this device.\r\n"
		message += "- sms: {}/{} points\r\n".format(subscription["current"]["sms"], subscription["current"]["plan"]["sms"])
		message += "- email: {}/{}\r\n".format(subscription["current"]["email"], subscription["current"]["plan"]["email"])
		message += "- notification: {}/{}\r\n".format(subscription["current"]["notification"], subscription["current"]["plan"]["notification"])
		message += "- storage: {}/{} GB\r\n".format(subscription["current"]["storage"], subscription["current"]["plan"]["storage"])

		message += "\r\n\r\nBest Regards,\r\n"
		message += "Bridgetek Pte. Ltd.\r\n"
		return message

	def construct_sensordata_download_link_message(self, name, url, devicename, deviceid):
		message =  "Hi {},\r\n\r\n\r\n".format(name)

		message += "Sensor data for device {} with UUID {} is now available.\r\n".format(devicename, deviceid)
		message += "Click the link below to download.\r\n\r\n"
		message += url
		message += "\r\n\r\n"

		message += "\r\nBest Regards,\r\n"
		message += "Bridgetek Pte. Ltd.\r\n"
		return message
