import boto3
from warrant.aws_srp import AWSSRP
from cognito_config import config
import time
import ast
from jose import jwk, jwt
from jose.utils import base64url_decode



class cognito_client:

	def __init__(self):
		self.aws_access_key_id     = config.CONFIG_ACCESS_KEY
		self.aws_secret_access_key = config.CONFIG_SECRET_KEY
		self.client_id             = config.CONFIG_CLIENT_ID
		self.pool_id               = config.CONFIG_USER_POOL_ID
		self.pool_region           = config.CONFIG_USER_POOL_REGION
		self.keys, self.keys_iss   = self.__get_userpool_keys()

	def get_cognito_client_id(self):
		return self.client_id
	
	def __get_client(self):
		#return boto3.Session(region_name=self.pool_region).client('cognito-idp')
		return boto3.Session(
			aws_access_key_id = self.aws_access_key_id,
			aws_secret_access_key = self.aws_secret_access_key,
			region_name = self.pool_region).client('cognito-idp')

	def __get_result(self, response):
		return True if response["ResponseMetadata"]["HTTPStatusCode"] == 200 else False

	def __dict_to_cognito(self, attributes, attr_map=None):
		if attr_map is None:
			attr_map = {}
		for k,v in attr_map.items():
			if v in attributes.keys():
				attributes[k] = attributes.pop(v)
		return [{'Name': key, 'Value': value} for key, value in attributes.items()]

	def __cognito_to_dict(self, attr_list, attr_map=None):
		if attr_map is None:
			attr_map = {}
		attr_dict = dict()
		for a in attr_list:
			name = a.get('Name')
			value = a.get('Value')
			if value in ['true', 'false']:
				value = ast.literal_eval(value.capitalize())
			name = attr_map.get(name,name)
			attr_dict[name] = value
		return attr_dict

	def __get_userpool_keys(self):
		import urllib.request
		import json
		keys_iss = 'https://cognito-idp.{}.amazonaws.com/{}'.format(config.CONFIG_USER_POOL_REGION, config.CONFIG_USER_POOL_ID)
		keys_url = '{}/.well-known/jwks.json'.format(keys_iss)
		response = urllib.request.urlopen(keys_url)
		keys = json.loads(response.read())['keys']
		return keys, keys_iss



	def sign_up(self, username, password, **attributes):
		params = {
			'ClientId'       : self.client_id,
			'Username'       : username,
			'Password'       : password,
			'UserAttributes' : self.__dict_to_cognito(attributes)
		}
		try:
			response = self.__get_client().sign_up(**params)
		except:
			return (False, None)
		return (self.__get_result(response), response)

	def confirm_sign_up(self, username, confirmation_code):
		params = {
			'ClientId'        : self.client_id,
			'Username'        : username,
			'ConfirmationCode': confirmation_code
		}
		try:
			response = self.__get_client().confirm_sign_up(**params)
		except:
			return (False, None)
		return (self.__get_result(response), response)

	def resend_confirmation_code(self, username):
		params = {
			'ClientId'        : self.client_id,
			'Username'        : username
		}
		try:
			response = self.__get_client().resend_confirmation_code(**params)
		except:
			return (False, None)
		return (self.__get_result(response), response)


	def forgot_password(self, username):
		params = {
			'ClientId': self.client_id,
			'Username': username
		}
		try:
			response = self.__get_client().forgot_password(**params)
		except:
			return (False, None)
		return (self.__get_result(response), response)

	def confirm_forgot_password(self, username, confirmation_code, new_password):
		params = {
			'ClientId'        : self.client_id,
			'Username'        : username,
			'ConfirmationCode': confirmation_code,
			'Password'        : new_password
		}
		try:
			response = self.__get_client().confirm_forgot_password(**params)
		except:
			return (False, None)
		return (self.__get_result(response), response)



	def login(self, username, password):
		if True:
			params = {
				'AuthFlow'       : 'USER_PASSWORD_AUTH',
				'AuthParameters' : {
					'USERNAME': username,
					'PASSWORD': password,
				},
				'ClientId'        : self.client_id
			}
			try:
				#start_time = time.time()
				response = self.__get_client().initiate_auth(**params)
				#print(time.time()-start_time)
				#print(response)
			except Exception as e:
				#print("exception")
				error_code = e.response.get("Error", {}).get("Code")
				if error_code == "PasswordResetRequiredException":
					print("Password reset required")
				elif error_code == "NotAuthorizedException":
					print("Incorrect password")
				else:
					print(error_code)
				return (False, error_code)
			return (self.__get_result(response), response)
		else:
			client = self.__get_client()
			params = {
				'username'  : username,
				'password'  : password,
				'pool_id'   : self.pool_id,
				'client_id' : self.client_id,
				'client'    : client
			}
			try:
				#start_time = time.time()
				aws = AWSSRP(**params)
				response = aws.authenticate_user()
				#print(time.time()-start_time)
			except:
				return (False, None)
			return (self.__get_result(response), response)

	def login_mfa(self, username, sessionkey, mfacode):
		params = {
			'ClientId' : self.client_id,
			'ChallengeName' : 'SMS_MFA',
			'Session'  : sessionkey,
			'ChallengeResponses' : {
				'SMS_MFA_CODE': mfacode,
				'USERNAME': username
			}
		}
		try:
			response = self.__get_client().respond_to_auth_challenge(**params)
			#print(response)
		except Exception as e:
			print(e)
			return (False, None)
		return (self.__get_result(response), response)

	def logout(self, access_token):
		params = {
			'AccessToken': access_token
		}
		try:
			response = self.__get_client().global_sign_out(**params)
		except:
			return (False, None)
		return (self.__get_result(response), response)

	def get_user(self, access_token):
		#print("get_user")
		params = {
			'AccessToken': access_token
		}
		try:
			response = self.__get_client().get_user(**params)
			user_attributes = self.__cognito_to_dict(response["UserAttributes"])
			#print(user_attributes)
			if 'sub' in user_attributes:
				user_attributes.pop("sub")
			#if 'email_verified' in user_attributes:
			#	user_attributes.pop("email_verified")
			#if 'phone_number_verified' in user_attributes:
			#	user_attributes.pop("phone_number_verified")
		except:
			return (False, None)
		return (self.__get_result(response), user_attributes)

	def delete_user(self, username, access_token):
		params = {
			'UserPoolId' : self.pool_id,
			'Username'   : username,
			#'AccessToken': access_token
		}
		try:
			response = self.__get_client().admin_delete_user(**params)
			#response = self.__get_client().delete_user(**params)
		except:
			return (False, None)
		return (self.__get_result(response), response)

	def admin_delete_user(self, username):
		params = {
			'UserPoolId' : self.pool_id,
			'Username'   : username,
		}
		try:
			response = self.__get_client().admin_delete_user(**params)
		except:
			return (False, None)
		return (self.__get_result(response), response)

	def update_user(self, access_token, **attributes):
		params = {
			'AccessToken'    : access_token,
			'UserAttributes' : self.__dict_to_cognito(attributes)
		}
		try:
			response = self.__get_client().update_user_attributes(**params)
		except:
			return (False, None)
		return (self.__get_result(response), response)
	
	def change_password(self, access_token, password, new_password):
		params = {
			'PreviousPassword': password,
			'ProposedPassword': new_password,
			'AccessToken'     : access_token
		}
		try:
			response = self.__get_client().change_password(**params)
		except:
			return (False, None)
		return (self.__get_result(response), response)

	def request_verify_phone_number(self, access_token):
		params = {
			'AccessToken': access_token,
			'AttributeName': 'phone_number'
		}
		try:
			print("get_user_attribute_verification_code")
			response = self.__get_client().get_user_attribute_verification_code(**params)
			print(response)
		except Exception as e:
			print(e)
			return (False, None)
		return (self.__get_result(response), response)

	def confirm_verify_phone_number(self, access_token, confirmation_code):
		params = {
			'AccessToken': access_token,
			'AttributeName': 'phone_number',
			'Code': confirmation_code
		}
		try:
			response = self.__get_client().verify_user_attribute(**params)
		except:
			return (False, None)
		return (self.__get_result(response), response)

	def enable_mfa(self, access_token, enable):
		params = {
			'AccessToken'     : access_token,
			'SMSMfaSettings'  : {
				'Enabled'     : enable,
				'PreferredMfa': enable
			},
		}
		try:
			response = self.__get_client().set_user_mfa_preference(**params)
		except Exception as e:
			print(e)
			return (False, None)
		return (self.__get_result(response), response)

	def admin_enable_mfa(self, username, enable):
		params = {
			'Username'        : username,
			'UserPoolId'      : self.pool_id,
			'SMSMfaSettings'  : {
				'Enabled'     : enable,
				'PreferredMfa': enable
			},
		}
		try:
			response = self.__get_client().admin_set_user_mfa_preference(**params)
		except Exception as e:
			print(e)
			return (False, None)
		return (self.__get_result(response), response)

	def admin_refresh_token(self, refresh_token):
		params = {
			'UserPoolId'      : self.pool_id,
			'ClientId'        : self.client_id,
			'AuthFlow'       : 'REFRESH_TOKEN',
			'AuthParameters' : {
				'REFRESH_TOKEN': refresh_token
			},
		}
		try:
			response = self.__get_client().admin_initiate_auth(**params)
		except Exception as e:
			print(e)
			return (False, None)
		return (self.__get_result(response), response)

	def refresh_token(self, refresh_token):
		params = {
			'AuthFlow'       : 'REFRESH_TOKEN',
			'AuthParameters' : {
				'REFRESH_TOKEN': refresh_token
			},
			'ClientId'        : self.client_id
		}
		try:
			response = self.__get_client().initiate_auth(**params)
		except Exception as e:
			print(e)
			return (False, None)
		return (self.__get_result(response), response)

	def get_username_from_token(self, token):
		if self.keys is None:
			(self.keys, self.keys_iss) = self.__get_userpool_keys()

		try:
			headers = jwt.get_unverified_header(token)
		except:
			return None
		if not headers.get('kid'):
			return None
		kid = headers['kid']

		key_index = -1
		for i in range(len(self.keys)):
			if kid == self.keys[i]['kid']:
				key_index = i
				break
		if key_index == -1:
			return None

		public_key = jwk.construct(self.keys[key_index])
		message, encoded_signature = str(token).rsplit('.', 1)
		decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
		if not public_key.verify(message.encode("utf8"), decoded_signature):
			return None

		claims = jwt.get_unverified_claims(token)
		return claims["username"]

	def verify_token(self, token, username):
		if self.keys is None:
			(self.keys, self.keys_iss) = self.__get_userpool_keys()

		# get the kid from the headers prior to verification
		try:
			headers = jwt.get_unverified_header(token)
		except:
			return 6
		if not headers.get('kid'):
			return 7
		kid = headers['kid']

		# search for the kid in the downloaded public keys
		key_index = -1
		for i in range(len(self.keys)):
			if kid == self.keys[i]['kid']:
				key_index = i
				break
		if key_index == -1:
			print('Public key not found in jwks.json')
			return 8

		# construct the public key
		public_key = jwk.construct(self.keys[key_index])

		# get the last two sections of the token,
		# message and signature (encoded in base64)
		message, encoded_signature = str(token).rsplit('.', 1)

		# decode the signature
		decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))

		# verify the signature
		if not public_key.verify(message.encode("utf8"), decoded_signature):
			print('Signature verification failed')
			return 9

		# since we passed the verification, we can now safely
		# use the unverified claims
		claims = jwt.get_unverified_claims(token)
		if claims["token_use"] != "access":
			print('Token is not an access token')
			return 1
		curr_time = int(time.time())
		if curr_time > claims["exp"] or curr_time < claims["iat"]:
			#print('Token is expired {} [iat {}, exp {}]'.format(curr_time, claims["iat"], claims["exp"]))
			return 2
		if claims["client_id"] != config.CONFIG_CLIENT_ID:
			print('Token was not issued for this client_id')
			return 3
		if claims["username"] != username:
			print('Token was not issued for this username')
			return 4
		if claims['iss'] != self.keys_iss:
			print('Token was not issued for this pool_id')
			return 5
		return 0



	def admin_list_users(self):
		#attributes = ["email", "given_name", "family_name", "email"]
		params = {
			'UserPoolId'      : self.pool_id,
			#'AttributesToGet' : attributes
		}
		try:
			response = self.__get_client().list_users(**params)
			users = response.copy()
			users.pop("ResponseMetadata")
			#print(users)
			users = users["Users"]
			num_users = len(users)
			user_list = []
			for user in users:
				user_attributes = self.__cognito_to_dict(user["Attributes"])
				#print(user)
				user_attributes["username"] = user["Username"]
				user_attributes["creationdate"] = user["UserCreateDate"]
				user_attributes["modifieddate"] = user["UserLastModifiedDate"]
				user_attributes["enabled"] = user["Enabled"]
				user_attributes["status"] = user["UserStatus"]
				user_list.append(user_attributes)
		except Exception as e:
			print(e)
			return (False, None)
		return (self.__get_result(response), user_list)

	def admin_display_users(self, users):
		print()
		if users:
			for user in users:
				print("username       : {}".format(user["username"]))
				print("  email        : {}".format(user["email"]))
				print("  given_name   : {}".format(user["given_name"]))
				print("  family_name  : {}".format(user["family_name"]))
				print("  creationdate : {}".format(user["creationdate"]))
				print("  modifieddate : {}".format(user["modifieddate"]))
				print("  enabled      : {}".format(user["enabled"]))
				print("  status       : {}".format(user["status"]))
				if user.get("phone_number"):
					print("  phone_number : {}".format(user["phone_number"]))
				print()

	def admin_reset_user_password(self, username):
		params = {
			'UserPoolId' : self.pool_id,
			'Username'   : username
		}
		try:
			response = self.__get_client().admin_reset_user_password(**params)
		except:
			return (False, None)
		return (self.__get_result(response), response)

	def admin_disable_user(self, username):
		params = {
			'UserPoolId' : self.pool_id,
			'Username'   : username
		}
		try:
			response = self.__get_client().admin_disable_user(**params)
		except:
			return (False, None)
		return (self.__get_result(response), response)

	def admin_enable_user(self, username):
		params = {
			'UserPoolId' : self.pool_id,
			'Username'   : username
		}
		try:
			response = self.__get_client().admin_enable_user(**params)
		except:
			return (False, None)
		return (self.__get_result(response), response)

	def admin_add_user_to_group(self, username, groupname):
		params = {
			'UserPoolId' : self.pool_id,
			'Username'   : username,
			'GroupName'  : groupname
		}
		try:
			response = self.__get_client().admin_add_user_to_group(**params)
		except:
			return (False, None)
		return (self.__get_result(response), response)

	def admin_remove_user_from_group(self, username, groupname):
		params = {
			'UserPoolId' : self.pool_id,
			'Username'   : username,
			'GroupName'  : groupname
		}
		try:
			response = self.__get_client().admin_remove_user_from_group(**params)
		except:
			return (False, None)
		return (self.__get_result(response), response)

	def admin_list_groups_for_user(self, username):
		params = {
			'Username'   : username,
			'UserPoolId' : self.pool_id
		}
		try:
			response = self.__get_client().admin_list_groups_for_user(**params)

			groups = response.copy()
			groups.pop("ResponseMetadata")
			groups = groups["Groups"]
			#print(groups)
			num_users = len(groups)
			group_list = []
			for group in groups:
				group_attributes = {}
				group_attributes["groupname"] = group["GroupName"]
				#group_attributes["description"] = group["Description"]
				#group_attributes["modifieddate"] = str(group["LastModifiedDate"])
				#group_attributes["creationdate"] = str(group["CreationDate"])
				group_list.append(group_attributes)
		except:
			return (False, None)
		return (self.__get_result(response), group_list)

	def admin_display_groups_for_user(self, groups):
		print()
		if groups:
			for group in groups:
				print("groupname      : {}".format(group["groupname"]))
				print("  description  : {}".format(group["description"]))
				print("  modifieddate : {}".format(group["modifieddate"]))
				print("  creationdate : {}".format(group["creationdate"]))
				print()

	def admin_logout_user(self, username):
		params = {
			'UserPoolId': self.pool_id,
			'Username'  : username
		}
		try:
			response = self.__get_client().admin_user_global_sign_out(**params)
		except:
			return (False, None)
		return (self.__get_result(response), response)

	def admin_delete_user(self, username):
		params = {
			'UserPoolId': self.pool_id,
			'Username'  : username
		}
		try:
			response = self.__get_client().admin_delete_user(**params)
		except:
			return (False, None)
		return (self.__get_result(response), response)


