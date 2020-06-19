import boto3
import json
import jwt
import os



class s3_client:

	def __init__(self, passcode):
		self.passcode = jwt.decode(passcode, os.path.basename(__file__), algorithm='HS256')

	def __get_client(self):
		return boto3.Session(
			aws_access_key_id=self.passcode["access"],
			aws_secret_access_key=self.passcode["secret"],
			region_name=self.passcode["region"]).client('s3')

	def __get_result(self, response):
		return True if response["ResponseMetadata"]["HTTPStatusCode"] == 200 else False


	def __get_file(self, filename, raw=False):
		try:
			response = self.__get_client().get_object(Bucket=self.passcode["bucket"], Key=filename)
		except Exception as e:
			print("exception")
			print(e)
			return (False, None)

		if raw:
			raw_bytes = response['Body'].read()
			#print(raw_bytes)
			return (True, raw_bytes)

		json_string = response['Body'].read().decode("utf-8")
		if json_string is None:
			return (False, None)
		#print(json_string)
		json_obj = json.loads(json_string)
		#print(json_obj)

		return (self.__get_result(response), json_obj)

	def __create_file(self, file, body=None, acl='public-read'):
		try:
			if body is None:
				self.__get_client().put_object(Bucket=self.passcode["bucket"], ACL=acl, Key=file)
			else:
				self.__get_client().put_object(Bucket=self.passcode["bucket"], ACL=acl, Key=file, Body=body)
			return True
		except Exception as e:
			print("exception")
			print(e)
		return False


	def get_firmware(self, filename):
		if not filename.startswith("firmware/"):
			return self.__get_file("firmware/" + filename, raw=True)
		return self.__get_file(filename, raw=True)

	def get_device_firmware_updates(self):
		return self.__get_file(self.passcode["file_firmwareupdates"])

	def update_device_firmware_updates(self, json_string, firmware_bin_contents, firmware_bin_path):
		result = self.__create_file("firmware/" + firmware_bin_path, body=firmware_bin_contents)
		if not result:
			return result
		return self.__create_file(self.passcode["file_firmwareupdates"], body=json_string.encode("utf-8"), acl='public-read-write')



