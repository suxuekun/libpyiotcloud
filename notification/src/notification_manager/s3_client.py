import boto3
import json
import csv
from aws_config import config
import urllib.parse



class s3_client:

	def __init__(self):
		self.aws_access_key_id     = config.CONFIG_ACCESS_KEY
		self.aws_secret_access_key = config.CONFIG_SECRET_KEY
		self.region                = config.CONFIG_S3_REGION
		self.bucket                = config.CONFIG_S3_BUCKET
		self.sms_country_points    = config.CONFIG_S3_FILE_SMS_COUNTRY_POINTS

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


	def __read_file_csv_to_json(self, filename):

		json_obj = []

		with open(self.sms_country_points) as csv_data:
			csv_reader = csv.DictReader(csv_data)

			for csv_row in csv_reader:
				code = csv_row["Code"]
				country = csv_row["Country"]
				points = csv_row["Points Cost"]
				if code != "" and country != "" and points != "":
					item = {
						"code": code, 
						"country": country, 
						"points": points
					}
					json_obj.append(item)
					#print(item)

		return json_obj


	def get_sms_country_points_list(self):

		result, contents = self.__get_file(self.sms_country_points, raw=True)
		if not result:
			return []

		with open(self.sms_country_points, 'w') as csv_data:
			csv_data.write(contents)

		try:
			json_obj = self.__read_file_csv_to_json(self.sms_country_points)
		except:
			json_obj = []

		#print(self.__print_json(json_obj))
		return json_obj

