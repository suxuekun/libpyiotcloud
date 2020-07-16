class email_templates:

	def add_header(self, name):
		if name:
			message =  "Hi {},\r\n\r\n\r\n".format(name)
		else:
			message =  "Hi,\r\n\r\n\r\n"
		return message

	def add_footer(self):
		message = "\r\nBest Regards,\r\n"
		message += "Bridgetek Pte. Ltd.\r\n"
		return message


	def construct_invoice_message(self, name, payment):

		message = self.add_header(name)

		message += "A Paypal payment of {} USD for {} credits was processed successfully.\r\n".format(payment["amount"], payment["value"])
		message += "To confirm your Paypal transaction, visit the Paypal website and check the transaction ID: {}.\r\n\r\n".format(payment["id"])

		message += "If unauthorised, please contact customer support.\r\n\r\n"

		message += self.add_footer()
		return message

	def construct_invitation_organization_message(self, orgname, orgowner):

		message = self.add_header(None)

		message += "You have been invited to join the {} organization by {}.\r\n".format(orgname, orgowner)
		message += "This allows you to manage, operate, monitor or view IoT gateway devices of your organization based on assigned roles and permissions.\r\n\r\n"

		message += "Please download the Bridgetek IoT Portal mobile app or visit the website:\r\n".format(CONFIG_USE_APIURL)
		message += "- Android app at Google Play\r\n"
		message += "- iOS app at Apple App Store\r\n"
		message += "- Website at https://{}\r\n".format(CONFIG_USE_APIURL)
		message += "If you don't have an account yet, sign up for an account then go to the Organization page to accept the invitation.\r\n\r\n"

		message += self.add_footer()
		return message

	def construct_usage_notice_message(self, deviceid, menos_type, subscription):

		message = self.add_header(None)

		message += "One of your devices with UUID {} has consumed all its {} allocation.\r\n\r\n".format(deviceid, menos_type)

		message += "Below is usage summary of this device.\r\n"
		message += "- sms: {}/{} points\r\n".format(subscription["current"]["sms"], subscription["current"]["plan"]["sms"])
		message += "- email: {}/{}\r\n".format(subscription["current"]["email"], subscription["current"]["plan"]["email"])
		message += "- notification: {}/{}\r\n".format(subscription["current"]["notification"], subscription["current"]["plan"]["notification"])
		message += "- storage: {}/{} GB\r\n".format(subscription["current"]["storage"], subscription["current"]["plan"]["storage"])

		message += self.add_footer()
		return message

	def construct_sensordata_download_link_message(self, name, url, devicename, deviceid):

		message = self.add_header(name)

		message += "Sensor data for device {} with UUID {} is now available.\r\n".format(devicename, deviceid)
		message += "Click the link below to download.\r\n\r\n"
		message += url
		message += "\r\n\r\n"

		message += self.add_footer()
		return message

	def construct_device_registration_message(self, deviceid, serialnumber):

		message = self.add_header(None)

		message += "You have successfully registered your IoT Gateway device.\r\n"
		message += "- Device UUID: {}\r\n".format(deviceid)
		message += "- Serial Number: {}\r\n\r\n".format(serialnumber)

		message += "Your device has been automatically subscribed to the Free plan subscription.\r\n"
		message += "To learn more of the subscription plan benefits, refer to the Subscription page in your Android or IOS app.\r\n"
		message += "\r\n\r\n"

		message += self.add_footer()
		return message

	def construct_device_unregistration_message(self, deviceid, serialnumber):

		message = self.add_header(None)

		message += "You have successfully unregistered your IoT Gateway device.\r\n"
		message += "- Device UUID: {}\r\n".format(deviceid)
		message += "- Serial Number: {}\r\n\r\n".format(serialnumber)

		message += "Your device has been automatically unsubscribed from its existing subscription plan.\r\n"
		message += "\r\n\r\n"

		message += self.add_footer()
		return message

	def construct_account_creation_message(self, name=None):

		message = self.add_header(name)

		message += "You have successfully created an account in IoT Portal.\r\n"
		message += "\r\n"

		message += self.add_footer()
		return message

	def construct_account_deletion_message(self, name=None):

		message = self.add_header(name)

		message += "You have successfully deleted your account in IoT Portal.\r\n"
		message += "\r\n"

		message += self.add_footer()
		return message

