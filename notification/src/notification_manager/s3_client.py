import boto3
import json
from aws_config import config
import urllib.parse



class s3_client:

	def __init__(self):
		self.aws_access_key_id     = config.CONFIG_ACCESS_KEY
		self.aws_secret_access_key = config.CONFIG_SECRET_KEY
		self.region                = config.CONFIG_S3_REGION
		self.bucket                = config.CONFIG_S3_BUCKET

	def __print_json(self, json_object, is_json=True, label=None):
		if is_json:
			json_formatted_str = json.dumps(json_object, indent=2)
		else: 
			json_formatted_str = json_object
		if label is None:
			print(json_formatted_str)
		else:
			print("{}\r\n{}".format(label, json_formatted_str))

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
			raw_bytes = response['Body'].read().decode("utf-8")
			#print(raw_bytes)
			return (True, raw_bytes)

		json_string = response['Body'].read().decode("utf-8")
		if json_string is None:
			return (False, None)
		#print(json_string)
		json_obj = json.loads(json_string)
		#print(json_obj)

		return (self.__get_result(response), json_obj)

	def __list_objects(self):
		try:
			bucket = self.__get_client().list_objects(Bucket=self.bucket)
			for key in bucket["Contents"]:
				print(key["Key"])
		except Exception as e:
			print("exception")
			print(e)
			return (False, None)

	def __is_file_exist(self, file):
		try:
			bucket = self.__get_client().list_objects(Bucket=self.bucket)
			for key in bucket["Contents"]:
				if key["Key"] == file:
					#print(key)
					return True
		except Exception as e:
			print("exception")
			print(e)
		return False

	def __create_file(self, file, body=None):
		try:
			if body is None:
				self.__get_client().put_object(Bucket=self.bucket, ACL='public-read', Key=file)
			else:
				self.__get_client().put_object(Bucket=self.bucket, ACL='public-read', Key=file, Body=body)
			return True
		except Exception as e:
			print("exception")
			print(e)
		return False

	def __get_filename(self, username, deviceid):
		return "menos/storage/" + username + "/" + deviceid + ".log"


	def append_to_file(self, username, deviceid, contents):
		#print("\r\n{} {} {}".format(username, deviceid, contents))

		file = self.__get_filename(username, deviceid)

		# check if file exists
		result = self.__is_file_exist(file)
		if not result:
			result = self.__create_file(file)
		if result:
			# retrieve the file contents as string
			result, contents_current = self.__get_file(file, True)
			if result:
				# rewrite the file
				body = contents + "\r\n" + contents_current
				result = self.__create_file(file, body.encode("utf-8"))

		if not result:
			return None

		return urllib.parse.quote(file)
