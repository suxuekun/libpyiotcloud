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
		self.file_sensordevices    = config.CONFIG_FILE_SENSOR_DEVICES
		self.file_firmwareupdates  = config.CONFIG_FILE_FIRMWARE_UPDATES

	def __get_client(self):
		return boto3.Session(
			aws_access_key_id=self.aws_access_key_id,
			aws_secret_access_key=self.aws_secret_access_key,
			region_name=self.region).client('s3')

	def __get_result(self, response):
		return True if response["ResponseMetadata"]["HTTPStatusCode"] == 200 else False


	def __get_file(self, filename):
		try:
			response = self.__get_client().get_object(Bucket=self.bucket, Key=filename)
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


	def get_supported_i2c_devices(self):
		return self.__get_file(self.file_i2cdevices)

	def get_supported_sensor_devices(self):
		return self.__get_file(self.file_sensordevices)

	def get_device_firmware_updates(self):
		return self.__get_file(self.file_firmwareupdates)

