import boto3
import json
from download_config import config



class s3_client:

	def __init__(self):
		self.aws_access_key_id     = config.CONFIG_ACCESS_KEY
		self.aws_secret_access_key = config.CONFIG_SECRET_KEY
		self.region                = config.CONFIG_REGION
		self.bucket                = config.CONFIG_BUCKET

	def __get_client(self):
		return boto3.Session(
			aws_access_key_id=self.aws_access_key_id,
			aws_secret_access_key=self.aws_secret_access_key,
			region_name=self.region).client('s3')

	def __get_result(self, response):
		return True if response["ResponseMetadata"]["HTTPStatusCode"] == 200 else False


	def __get_file(self, filename, raw=False):
		try:
			response = self.__get_client().get_object(Bucket=self.bucket, Key=filename)
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
				self.__get_client().put_object(Bucket=self.bucket, ACL=acl, Key=file)
			else:
				self.__get_client().put_object(Bucket=self.bucket, ACL=acl, Key=file, Body=body)
			return True
		except Exception as e:
			print("exception")
			print(e)
		return False

	def upload_sensordata_zipfile(self, filename, contents):
		result = self.__create_file("sensordata/" + filename, body=contents, acl='public-read-write')
		if not result:
			return None
		return "https://ft900-iot-portal.s3.amazonaws.com/sensordata/" + filename



