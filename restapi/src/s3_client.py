import boto3
import json
from s3_config import config



class s3_client:

	def __init__(self):
		self.aws_access_key_id     = config.CONFIG_ACCESS_KEY
		self.aws_secret_access_key = config.CONFIG_SECRET_KEY
		self.region                = config.CONFIG_REGION
		self.bucket                = config.CONFIG_BUCKET
		self.file_i2cdevices       = config.CONFIG_FILE_I2C_DEVICES

	def __get_client(self):
		return boto3.Session(
			aws_access_key_id=self.aws_access_key_id,
			aws_secret_access_key=self.aws_secret_access_key,
			region_name=self.region).client('s3')

	def __get_result(self, response):
		return True if response["ResponseMetadata"]["HTTPStatusCode"] == 200 else False



	def get_supported_i2c_devices(self):
		try:
			response = self.__get_client().get_object(Bucket=self.bucket, Key=self.file_i2cdevices)
			#print(response)
		except Exception as e:
			print("exception")
			print(e)
			return (False, None)

		json_string = response['Body'].read().decode("utf-8")
		if json_string is None:
			return (False, None)
		#print(json_string)
		json_obj = json.loads(json_string)
		#print(json_obj)

		return (self.__get_result(response), json_obj)
