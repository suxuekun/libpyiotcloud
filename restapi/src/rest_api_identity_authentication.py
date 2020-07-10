#import os
#import ssl
import json
import time
#import hmac
#import hashlib
import flask
import base64
import datetime
#import calendar
#from flask_json import FlaskJSON, JsonError, json_response, as_json
#from certificate_generator import certificate_generator
#from messaging_client import messaging_client
from rest_api_config import config
#from database import database_client
#from flask_cors import CORS
from flask_api import status
from jose import jwk, jwt
#import http.client
#from s3_client import s3_client
#import threading
#import copy
#from redis_client import redis_client
#import statistics
import rest_api_utils
import pycountry
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import (
    region_code_for_country_code,
    region_code_for_number,
)



CONFIG_ALLOW_LOGIN_VIA_PHONE_NUMBER = True
CONFIG_USE_REDIS_FOR_IDP            = True
CONFIG_SUPPORT_MFA                  = True



class identity_authentication:

    def __init__(self, database_client, redis_client):
        self.database_client = database_client
        self.redis_client = redis_client


    ########################################################################################################
    #
    # LOGIN IDP STORE CODE
    #
    # - Request:
    #   POST /user/login/idp/code/<id>
    #   headers: {'Content-Type': 'application/json'}
    #   data: {'code': string}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def login_idp_storecode(self, id):
        data = flask.request.get_json()
        if data.get("code") is None:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Login IDP STORE CODE: Empty parameter found [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        if CONFIG_USE_REDIS_FOR_IDP:
            # redis
            print("xxxxx idp {}:{}".format(id, data["code"]))
            self.redis_client.idp_set_code(id, data["code"])
            print("yyyyy idp {}:{}".format(id, data["code"]))
        else:
            self.database_client.set_idp_code(id, data["code"])

        response = json.dumps({'status': 'OK', 'message': "Login IDP store code successful"})
        return response


    ########################################################################################################
    #
    # LOGIN IDP QUERY CODE
    #
    # - Request:
    #   GET /user/login/idp/code/<id>
    #   headers: {'Content-Type': 'application/json'}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'code': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def login_idp_querycode(self, id):
        # check if code is available
        if CONFIG_USE_REDIS_FOR_IDP:
            # redis
            code = self.redis_client.idp_get_code(id)
            if code:
                self.redis_client.idp_del_code(id)
        else:
            code = self.database_client.get_idp_code(id)

        if code is None:
            response = json.dumps({'status': 'NG', 'message': 'Login IDP query code not found'})
            print('\r\nERROR Login IDP query: Code not found [{}]\r\n'.format(id))
            return response, status.HTTP_404_NOT_FOUND

        response = json.dumps({'status': 'OK', 'message': "Login IDP query code successful", 'code': code})
        return response


    ########################################################################################################
    #
    # LOGIN
    #
    # - Request:
    #   POST /user/login
    #   headers: {'Authorization': 'Basic ' + jwtEncode(username, password)}
    #   User can login using email or phone_number so the username parameter can be either an email or phone_number
    #   When username is a phone_number, it must start with '+'.
    #   When username is a phone_number, it must be verified first via OTP
    # - Response:
    #   {'status': 'OK', 'message': string, 'token': {'access': string, 'id': string, 'refresh': string}, 'name': string }
    #   {'status': 'NG', 'message': string}
    #   // When user logins with incorrect password for 5 consecutive times, user needs to reset the password
    #   // When error is HTTP_401_UNAUTHORIZED, web/mobile app should check message
    #   // If message is PasswordResetRequiredException, the web/mobile app should redirect user to the CONFIRM FORGOT PASSWORD page
    #   // User should input the OTP code sent in email and the new password to be used
    #
    ########################################################################################################
    def login(self):
        # get username and password from Authorization header
        username, password, reason = rest_api_utils.utils().get_auth_header_user_pass()
        if username is None or password is None:
            response = json.dumps({'status': 'NG', 'message': reason})
            print('\r\nERROR Login: Username password format invalid\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('login {} {}'.format(username, password))

        # check if a parameter is empty
        if len(username) == 0 or len(password) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Login: Empty parameter found [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST


        if CONFIG_ALLOW_LOGIN_VIA_PHONE_NUMBER:
            # support login via phonenumber
            # check if username is a phonenumber (starts with '+'), email (has '@') or string(login via idp)
            # since login via phone_number is now allowed,
            # the phone_number must be unique
            if username.startswith('+'):
                # username is a phone number
                # get the username given the phone number
                username = self.database_client.get_username_by_phonenumber(username)
                if username is None:
                    response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
                    print('\r\nERROR Login: Phone number does not exist [{}]\r\n'.format(username))
                    return response, status.HTTP_404_NOT_FOUND
            else:
                # check if username does not exist
                if not self.database_client.find_user(username):
                    # NOTE:
                    # its not good to provide a specific error message for LOGIN
                    # because it provides additional info for hackers
                    response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
                    print('\r\nERROR Login: Username does not exist [{}]\r\n'.format(username))
                    return response, status.HTTP_404_NOT_FOUND
        else:
            # check if username does not exist
            if not self.database_client.find_user(username):
                # NOTE:
                # its not good to provide a specific error message for LOGIN
                # because it provides additional info for hackers
                response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
                print('\r\nERROR Login: Username does not exist [{}]\r\n'.format(username))
                return response, status.HTTP_404_NOT_FOUND


        # RESOLVE MFA ISSUES
        #self.database_client.admin_enable_mfa(username, False)


        # check if password is valid
        access, refresh, id = self.database_client.login(username, password)
        if access is None:
            print(username)
            # NOTE:
            # its not good to provide a specific error message for LOGIN
            # because it provides additional info for hackers
            if id == "PasswordResetRequiredException":
                response = json.dumps({'status': 'NG', 'message': 'PasswordResetRequiredException', 'username': username})
                # trigger to send OTP to email
                result = self.database_client.forgot_password(username)
                #print(result)
            elif id == "NotAuthorizedException":
                self.database_client.set_last_login(username, False)
                # increment failed attempts
                self.redis_client.login_failed_set_attempts(username)
                attempts = self.redis_client.login_failed_get_attempts(username)
                # force password reset on 5 consecutive failed attempts
                if int(attempts) >= 5:
                    response = json.dumps({'status': 'NG', 'message': 'PasswordResetRequiredException', 'username': username})
                    self.database_client.reset_user_password(username)
                    #self.redis_client.login_failed_del_attempts(username)
                else:
                    response = json.dumps({'status': 'NG', 'message': 'NotAuthorizedException'})
            elif id == "MFARequiredException":
                if CONFIG_SUPPORT_MFA:
                    response = json.dumps({'status': 'NG', 'message': 'MFARequiredException', 'username': username})
                    # save the sessionkey saved in refresh username, session key
                    if self.redis_client.mfa_get_session(username) is not None:
                        self.redis_client.mfa_del_session(username)
                    self.redis_client.mfa_set_session(username, refresh)
                else:
                    response = json.dumps({'status': 'NG', 'message': 'NotAuthorizedException'})
            else:
                self.database_client.set_last_login(username, False)
                response = json.dumps({'status': 'NG', 'message': 'NotAuthorizedException'})
            print('\r\nERROR Login: Password is incorrect [{}] {}\r\n'.format(username, id))
            return response, status.HTTP_401_UNAUTHORIZED


        # delete the couter for failed logins
        attempts = self.redis_client.login_failed_get_attempts(username)
        if attempts is not None:
            self.redis_client.login_failed_del_attempts(username)

        # save the last login time
        self.database_client.set_last_login(username, True)


        # return name during login as per special request
        name = None
        info = self.database_client.get_user_info(access)
        if info:
            # handle no family name
            if 'given_name' in info:
                name = info['given_name']
            if 'family_name' in info:
                if info['family_name'] != "NONE":
                    name += " " + info['family_name']

        # link social idp
        #print(username)
        #self.database_client.admin_link_provider_for_user(username, 'Facebook')
        #self.database_client.admin_link_provider_for_user(username, info["email"], 'Facebook')


        msg = {'status': 'OK', 'message': "Login successful", 'token': {'access': access, 'refresh': refresh, 'id': id} }
        if name is not None:
            msg['name'] = name
        response = json.dumps(msg)
        #print('\r\nLogin successful: {}\r\n'.format(username))
        return response


    ########################################################################################################
    #
    # SIGN-UP
    #
    # - Request:
    #   POST /user/signup
    #   headers: {'Authorization': 'Bearer ' + jwtEncode(email, password), 'Content-Type': 'application/json'}
    #   data: { 'email': string, 'phone_number': string, 'name': string }
    #   // name can be 1 or multiple words
    #   // phone_number is optional
    #   // phone number should begin with "+" followed by country code then the number (ex. SG number +6512341234)
    #   // password length is 6 characters minimum as set in Cognito
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def signup(self):
        # get username and password from Authorization header
        username, password, reason = rest_api_utils.utils().get_auth_header_user_pass()
        if username is None or password is None:
            response = json.dumps({'status': 'NG', 'message': reason})
            print('\r\nERROR Signup: Username password format invalid\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        #print('signup username={}'.format(username))

        data = flask.request.get_json()
        email = data['email']
        if data.get("phone_number") is not None:
            phonenumber = data['phone_number']
        else:
            phonenumber = None
        name = data['name']
        names = name.split(" ")
        if (len(names) > 1):
            givenname = " ".join(names[:-1])
            familyname = names[-1]
        else:
            # handle no family name
            givenname = names[0]
            familyname = "NONE"

        print('signup username={} password={} email={} phonenumber={} givenname={} familyname={}'.format(username, password, email, phonenumber, givenname, familyname))

        # check if a parameter is empty
        if len(username) == 0 or len(password) == 0 or len(email) == 0 or len(givenname) == 0 or len(familyname) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Signup: Empty parameter found [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # check format of phonenumber
        if phonenumber is not None:
            if phonenumber != "":
                if phonenumber[0] != "+":
                    response = json.dumps({'status': 'NG', 'message': 'Phone number should follow the standard E.164 international phone numbering format: +<country code><number>'})
                    print('\r\nERROR Signup: Phone number should follow the standard E.164 international phone numbering format: +<country code><number> [{}]\r\n'.format(phonenumber))
                    return response, status.HTTP_400_BAD_REQUEST
            else:
                phonenumber = None

            # verify phone number using phonenumbers library
            try:
                if phonenumber is not None and phonenumber != "":
                    x = phonenumbers.parse(phonenumber, None)
                    if phonenumbers.is_possible_number(x) == False or phonenumbers.is_valid_number(x) == False:
                        response = json.dumps({'status': 'NG', 'message': 'Phone number is not valid'})
                        print('\r\nERROR Signup: Phone number is not valid [{}]\r\n'.format(phonenumber))
                        return response, status.HTTP_400_BAD_REQUEST
            except:
                response = json.dumps({'status': 'NG', 'message': 'Phone number is not valid'})
                print('\r\nERROR Signup: Phone number is not valid [{}]\r\n'.format(phonenumber))
                return response, status.HTTP_400_BAD_REQUEST

            if CONFIG_ALLOW_LOGIN_VIA_PHONE_NUMBER:
                # since login via phone_number is now allowed,
                # the phone_number must be unique,
                # so check if phone_number is already taken or not
                if self.database_client.get_username_by_phonenumber(phonenumber) is not None:
                    response = json.dumps({'status': 'NG', 'message': 'Phone number is already registered to another user'})
                    print('\r\nERROR Signup: Phone number is already registered to another user [{}]\r\n'.format(phonenumber))
                    return response, status.HTTP_400_BAD_REQUEST


        # check length of password
        if len(password) < 8:
            response = json.dumps({'status': 'NG', 'message': 'Password length should at least be 8 characters'})
            print('\r\nERROR Signup: Password length should at least be 8 characters [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # check if username is already in database
        if self.database_client.find_user(username):
            if self.database_client.is_email_verified(username):
                response = json.dumps({'status': 'NG', 'message': 'Username already exists'})
                print('\r\nERROR Signup: Username already exists [{}]\r\n'.format(username))
                return response, status.HTTP_409_CONFLICT
            else:
                # user already signed up but unverified, so delete the user for signup to proceed
                self.database_client.admin_delete_user(username)

        # Remove for scenario of login with social accounts identity providers
        # check if email is already in database
        #if self.database_client.find_email(email) is not None:
        #    response = json.dumps({'status': 'NG', 'message': 'Email already used'})
        #    print('\r\nERROR Signup: Email already used [{}]\r\n'.format(email))
        #    return response, status.HTTP_409_CONFLICT

        # add entry in database
        result, errorcode = self.database_client.add_user(username, password, email, phonenumber, givenname, familyname)
        if not result:
            if errorcode == "InvalidPasswordException":
                msg = "Password must be atleast 8 characters with a lowercase character, uppercase character, special character and a number."
            else:
                msg = 'Internal server error'
            response = json.dumps({'status': 'NG', 'message': msg})
            print('\r\nERROR Signup: {} [{},{},{},{},{}]\r\n'.format(msg, username, password, email, givenname, familyname))
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR

        response = json.dumps({'status': 'OK', 'message': 'User registered successfully. Check email for confirmation code.'})
        print('\r\nSignup successful: {}\r\n{}\r\n'.format(username, response))
        return response


    ########################################################################################################
    #
    # CONFIRM SIGN-UP
    #
    # - Request:
    #   POST /user/confirm_signup
    #   headers: {'Content-Type': 'application/json'}
    #   data: { 'username': string, 'confirmationcode': string }
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def confirm_signup(self):
        data = flask.request.get_json()
        username = data['username']
        confirmationcode = data['confirmationcode']
        #print('confirm_signup username={} confirmationcode={}'.format(username, confirmationcode))

        # check if a parameter is empty
        if len(username) == 0 or len(confirmationcode) != 6:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Confirm Signup: Empty parameter found [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # confirm user in database
        result = self.database_client.confirm_user(username, confirmationcode)
        if not result:
            response = json.dumps({'status': 'NG', 'message': 'Invalid code'})
            print('\r\nERROR Confirm Signup: Invalid code [{},{}]\r\n'.format(username, confirmationcode))
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR

        response = json.dumps({'status': 'OK', 'message': 'User registration confirmed successfully'})
        print('\r\nConfirm Signup successful: {}\r\n{}\r\n'.format(username, response))
        return response


    ########################################################################################################
    #
    # RESEND CONFIRMATION CODE
    #
    # - Request:
    #   POST /user/resend_confirmation_code
    #   headers: {'Content-Type': 'application/json'}
    #   data: { 'username': string }
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def resend_confirmation_code(self):
        data = flask.request.get_json()
        if data is None:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Resend Confirmation: Empty parameter found [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST
        if data.get('username') is None:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Resend Confirmation: Empty parameter found [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST
        username = data['username']
        print('resend_confirmation_code username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Resend Confirmation: Empty parameter found [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # check if a valid user
        if not self.database_client.find_user(username):
            response = json.dumps({'status': 'NG', 'message': 'Invalid user'})
            print('\r\nERROR Resend Confirmation: Invalid user [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # confirm user in database
        result = self.database_client.resend_confirmationcode(username)
        if not result:
            response = json.dumps({'status': 'NG', 'message': 'Invalid code'})
            print('\r\nERROR Resend Confirmation: Invalid code [{}]\r\n'.format(username))
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR

        response = json.dumps({'status': 'OK', 'message': 'Confirmation code resend successfully'})
        print('\r\nResend Confirmation successful: {}\r\n{}\r\n'.format(username, response))
        return response


    ########################################################################################################
    #
    # FORGOT PASSWORD
    #
    # - Request:
    #   POST /user/forgot_password
    #   headers: {'Content-Type': 'application/json'}
    #   data: { 'email': string }
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'username': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def forgot_password(self):
        data = flask.request.get_json()

        if CONFIG_ALLOW_LOGIN_VIA_PHONE_NUMBER:
            if data.get("email") is None and data.get("phone_number") is None:
                response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
                print('\r\nERROR Recover Account: Empty parameter found\r\n')
                return response, status.HTTP_400_BAD_REQUEST
        else:
            if data.get("email") is None:
                response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
                print('\r\nERROR Recover Account: Empty parameter found\r\n')
                return response, status.HTTP_400_BAD_REQUEST


        email = None
        if data.get("email") is not None:
            email = data['email']

            # check if a parameter is empty
            if len(email) == 0:
                response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
                print('\r\nERROR Recover Account: Empty parameter found\r\n')
                return response, status.HTTP_400_BAD_REQUEST

            # check if email is in database
            username = self.database_client.find_user(email)
            if username == False:
                response = json.dumps({'status': 'NG', 'message': 'Email does not exist'})
                print('\r\nERROR Recover Account: Email does not exist [{}]\r\n'.format(email))
                return response, status.HTTP_400_BAD_REQUEST

            username = email
            response = json.dumps({'status': 'OK', 'message': 'User account recovery successfully. Check email for confirmation code.', 'username': username})
            print('forgot_password email={}'.format(username))


        if CONFIG_ALLOW_LOGIN_VIA_PHONE_NUMBER:
            phone_number = None
            if data.get("phone_number") is not None:
                phone_number = data['phone_number']

                # check if a parameter is empty
                if len(phone_number) == 0:
                    response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
                    print('\r\nERROR Recover Account: Empty parameter found\r\n')
                    return response, status.HTTP_400_BAD_REQUEST

                # check if email is in database
                username = self.database_client.get_username_by_phonenumber(phone_number)
                if username is None:
                    response = json.dumps({'status': 'NG', 'message': 'Email does not exist'})
                    print('\r\nERROR Recover Account: Email does not exist [{}]\r\n'.format(email))
                    return response, status.HTTP_400_BAD_REQUEST

                response = json.dumps({'status': 'OK', 'message': 'User account recovery successfully. Check mobile number for confirmation code.', 'username': username})
                print('forgot_password phone_number={}'.format(phone_number))


        # recover account
        result = self.database_client.forgot_password(username)
        if not result:
            response = json.dumps({'status': 'NG', 'message': 'Internal server error'})
            print('\r\nERROR Recover Account: Internal server error [{}]\r\n'.format(username))
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR

        print('\r\nRecover Account successful: {}\r\n{}\r\n'.format(username, response))
        return response


    ########################################################################################################
    #
    # CONFIRM FORGOT PASSWORD
    #
    # - Request:
    #   POST /user/confirm_forgot_password
    #   headers: {'Authorization': 'Bearer ' + jwtEncode(username, password), 'Content-Type': 'application/json'}
    #   data: { 'confirmationcode': string }
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def confirm_forgot_password(self):
        # get username and password from Authorization header
        username, password, reason = rest_api_utils.utils().get_auth_header_user_pass()
        if username is None or password is None:
            response = json.dumps({'status': 'NG', 'message': reason})
            print('\r\nERROR Reset Password: Username password format invalid\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('confirm_forgot_password username={}'.format(username))

        data = flask.request.get_json()
        if data is None:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Reset Password: Empty parameter found [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST
        if data.get('confirmationcode') is None:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Reset Password: Empty parameter found [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST
        confirmationcode = data['confirmationcode']
        #print('confirm_forgot_password username={} confirmationcode={} password={}'.format(username, confirmationcode, password))

        # check if a parameter is empty
        if len(username) == 0 or len(confirmationcode) == 0 or len(password) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Reset Password: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check length of password
        if len(password) < 8:
            response = json.dumps({'status': 'NG', 'message': 'Password length should at least be 8 characters'})
            print('\r\nERROR Reset Password: Password length should at least be 8 characters [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # confirm user in database
        result, errorcode = self.database_client.confirm_forgot_password(username, confirmationcode, password)
        if not result:
            if errorcode == "InvalidPasswordException":
                msg = "Password must be atleast 8 characters with a lowercase character, uppercase character, special character and a number."
            elif errorcode == "CodeMismatchException":
                msg = 'Invalid verification code'
            elif errorcode == "LimitExceededException":
                msg = 'Attempt limit exceeded. Please try again later.'
            else:
                msg = 'Internal error'
            response = json.dumps({'status': 'NG', 'message': msg})
            print('\r\nERROR Reset Password: {} [{}]\r\n'.format(msg, username))
            return response, status.HTTP_400_BAD_REQUEST

        # delete the couter for failed logins
        attempts = self.redis_client.login_failed_get_attempts(username)
        if attempts is not None:
            self.redis_client.login_failed_del_attempts(username)

        response = json.dumps({'status': 'OK', 'message': 'User account recovery confirmed successfully.'})
        print('\r\nReset Password successful: {}\r\n{}\r\n'.format(username, response))
        return response


    ########################################################################################################
    #
    # LOGOUT
    #
    # - Request:
    #   POST /user/logout
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def logout(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Logout: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Logout: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Logout: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        try:
            #print("")
            #devicetoken = self.database_client.get_all_mobile_device_token(username)
            #print(len(devicetoken))
            #print(devicetoken)

            # delete mobile device tokens
            self.database_client.delete_mobile_device_token(username, token['access'])
            #self.database_client.delete_all_mobile_device_token(username)
            #print('\r\nDeleted mobile device token')

            #devicetoken = self.database_client.get_all_mobile_device_token(username)
            #print(len(devicetoken))
            #print(devicetoken)
            #print("")

            # there's only global_sign_out, no sign_out so just skip calling it logout
            # self.database_client.logout(token['access'])
            print('logout {}\r\n'.format(username))
        except:
            print('\r\nERROR Logout: exception\r\n')

        #self.database_client.delete_ota_statuses(username)
        return json.dumps({'status': 'OK', 'message': 'User logout successfully.'})

    ########################################################################################################
    #
    # GET USER INFO
    #
    # - Request:
    #   GET /user
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 
    #    'info': {'name': string, 'email': string, 'phone_number': string, 'email_verified': boolean, 'phone_number_verified': boolean} }
    #   // phone_number and phone_number_verified are not included if no phone_number has been added yet
    #   // phone_number_country, phone_number_isocode and phone_number_carrier is included only if phone_number has been verified
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_user(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Userinfo: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Userinfo: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED

        print('get_user username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Userinfo: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Userinfo: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Userinfo: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED

        if new_token:
            info = self.database_client.get_user_info(new_token['access'])
        else:
            info = self.database_client.get_user_info(token['access'])

        # handle no family name
        if info is not None:
            if 'identities' in info:
                identity = json.loads(info['identities'].strip(']['))
                info['identity'] = { 'providerName': identity['providerName'], 'userId': identity['userId'] }
                info.pop('identities')
            if 'given_name' in info:
                info['name'] = info['given_name']
                info.pop('given_name')
            if 'family_name' in info:
                if info['family_name'] != "NONE":
                    # do not append family name if login with amazon
                    if 'identity' in info:
                        if info['identity']['providerName'] != 'LoginWithAmazon':
                            info['name'] += " " + info['family_name']
                    else:
                        info['name'] += " " + info['family_name']
                info.pop('family_name')

            # add the country deducted from the phone number
            try:
                if 'phone_number' in info:
                    if 'phone_number_verified' in info:
                        if info['phone_number_verified'] == True:
                            pn = phonenumbers.parse(info['phone_number'])
                            isocode = region_code_for_country_code(pn.country_code)
                            country = pycountry.countries.get(alpha_2=isocode)
                            info['phone_number_country'] = country.name
                            info['phone_number_isocode'] = isocode
                            info['phone_number_carrier'] = carrier.name_for_number(pn, "en")
            except Exception as e:
                print(e)
                if info.get('phone_number_country') is None:
                    info['phone_number_country'] = "Unknown"
                if info.get('phone_number_isocode') is None:
                    info['phone_number_isocode'] = "Unknown"
                if info.get('phone_number_carrier') is None:
                    info['phone_number_carrier'] = "Unknown"
                pass

            # add username to info for Login via Social IDP (Facebook, Google, Amazon)
            info['username'] = username

            # add last login information
            last_login = self.database_client.get_last_login(username)
            if last_login is not None:
                if 'lastsuccess' in last_login:
                    info['last_login'] = last_login['lastsuccess']
                if 'lastfailed' in last_login:
                    info['last_failed_login'] = last_login['lastfailed']


        msg = {'status': 'OK', 'message': 'Userinfo queried successfully.'}
        if info:
            msg['info'] = info
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nUserinfo queried successful: {}\r\n{}\r\n'.format(username, response))
        return response


    ########################################################################################################
    #
    # DELETE USER
    #
    # - Request:
    #   DELETE /user
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string }
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def delete_user(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Delete user: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Delete user: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('delete_user username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Delete user: Empty parameter found\r\n')
            # NOTE:
            # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Delete user: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Delete user: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED

        # delete the user in cognito
        if new_token:
            result = self.database_client.delete_user(username, new_token['access'])
        else:
            result = self.database_client.delete_user(username, token['access'])
        if result == False:
            response = json.dumps({'status': 'NG', 'message': 'Delete user failed internal error'})
            print('\r\nERROR Delete user: Internal error [{}]\r\n'.format(username))
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR

        # TODO: delete user devices

        msg = {'status': 'OK', 'message': 'Delete user successful.'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nDelete user successful: {}\r\n{}\r\n'.format(username, response))
        return response


    ########################################################################################################
    #
    # REFRESH USER TOKEN
    #
    # - Request:
    #   POST /user/token
    #   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
    #   data: { 'refresh': string, 'id: string' }
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'token' : {'access': string, 'refresh': string, 'id': string} }
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def refresh_user_token(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Refresh token: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        #print('refresh_user_token')

        # check if a parameter is empty
        if len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Refresh token: Empty parameter found\r\n')
            # NOTE:
            # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
            return response, status.HTTP_400_BAD_REQUEST

        # get refresh and id token
        data = flask.request.get_json()
        if not data.get("refresh") or not data.get("id"):
            response = json.dumps({'status': 'NG', 'message': 'Refresh and ID tokens are not provided'})
            print('\r\nERROR Refresh token: Refresh and ID tokens are not provided\r\n')
            return response, status.HTTP_400_BAD_REQUEST
        token['refresh'] = data['refresh']
        token['id'] = data['id']

        # refresh the access token
        new_token = self.database_client.refresh_token(token)
        if new_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Refresh token invalid'})
            print('\r\nERROR Refresh token: Token expired. DATETIME {}\r\n\r\n'.format(datetime.datetime.now()))
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR

        # update mobile device token
        try:
            self.database_client.update_mobile_device_token(token["access"], new_token["access"])
        except:
            print("exception update_mobile_device_token")
            pass

        msg = {'status': 'OK', 'message': 'Refresh token successful.', 'token': new_token}
        response = json.dumps(msg)
        print('\r\nRefresh token successful DATETIME {}\r\n'.format(datetime.datetime.now()))
        return response

    ########################################################################################################
    #
    # VERIFY PHONE NUMBER
    #
    # - Request:
    #   POST /user/verify_phone_number
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def verify_phone_number(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Verify phone: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Verify phone: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('verify_phone_number username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Verify phone: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Verify phone: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Verify phone: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        if CONFIG_ALLOW_LOGIN_VIA_PHONE_NUMBER:
            info = self.database_client.get_user_info(token['access'])
            if info is not None:
                # since login via phone_number is now allowed,
                # the phone_number must be unique,
                # so check if phone_number is already taken or not
                if info.get("phone_number") is not None:
                    if self.database_client.get_username_by_phonenumber(info["phone_number"]) is not None:
                        response = json.dumps({'status': 'NG', 'message': 'Phone number is already registered to another user'})
                        print('\r\nERROR Verify phone: Phone number is already registered to another user [{}]\r\n'.format(info["phone_number"]))
                        return response, status.HTTP_400_BAD_REQUEST

                # verify phone number using phonenumbers library
                try:
                    if info["phone_number"] is not None and info["phone_number"] != "":
                        if info["phone_number"][0] != "+":
                            response = json.dumps({'status': 'NG', 'message': 'Phone number should follow the standard E.164 international phone numbering format: +<country code><number>'})
                            print('\r\nERROR Verify phone: Phone number should follow the standard E.164 international phone numbering format: +<country code><number> [{}]\r\n'.format(info["phone_number"]))
                            return response, status.HTTP_400_BAD_REQUEST

                        x = phonenumbers.parse(info["phone_number"], None)
                        if phonenumbers.is_possible_number(x) == False or phonenumbers.is_valid_number(x) == False:
                            response = json.dumps({'status': 'NG', 'message': 'Phone number is not valid'})
                            print('\r\nERROR Verify phone: Phone number is not valid [{}]\r\n'.format(info["phone_number"]))
                            return response, status.HTTP_400_BAD_REQUEST
                except:
                    response = json.dumps({'status': 'NG', 'message': 'Phone number is not valid'})
                    print('\r\nERROR Verify phone: Phone number is not valid [{}]\r\n'.format(info["phone_number"]))
                    return response, status.HTTP_400_BAD_REQUEST


        # verify phone number
        result = self.database_client.request_verify_phone_number(token["access"])
        if not result:
            response = json.dumps({'status': 'NG', 'message': 'Request failed'})
            print('\r\nERROR Verify phone: Request failed [{}]\r\n'.format(username))
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR

        response = json.dumps({'status': 'OK', 'message': 'Verify phone successful'})
        print('\r\nVerify phone successful: {}\r\n{}\r\n'.format(username, response))
        return response


    ########################################################################################################
    #
    # CONFIRM VERIFY PHONE NUMBER
    #
    # - Request:
    #   POST /user/confirm_verify_phone_number
    #   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
    #   data: {'confirmationcode': string}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def confirm_verify_phone_number(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Confirm verify phone: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Confirm verify phone: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('confirm_verify_phone_number username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Confirm verify phone: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Confirm verify phone: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Confirm verify phone: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED

        data = flask.request.get_json()

        # confirm verify phone number
        result = self.database_client.confirm_verify_phone_number(token["access"], data["confirmationcode"])
        if not result:
            response = json.dumps({'status': 'NG', 'message': 'Request failed'})
            print('\r\nERROR Confirm verify phone: Request failed [{}]\r\n'.format(username))
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR

        # update notifications for all devices to contain new phone number (for UART only)
        try:
            info = self.database_client.get_user_info(token['access'])
            devices = self.database_client.get_devices(username)
            sources = ["uart"]
            for source in sources:
                for device in devices:
                    notification = self.database_client.get_device_notification(username, device["devicename"], source)
                    if notification is not None:
                        if info is not None:
                            if info.get("phone_number"):
                                notification["endpoints"]["mobile"]["recipients"] = info["phone_number"]
                                notification["endpoints"]["mobile"]["recipients_list"] = []
                                notification["endpoints"]["mobile"]["recipients_list"].append({ "to": info["phone_number"], "group": False })
                                notification["endpoints"]["notification"]["recipients"] = info["phone_number"]
                                notification["endpoints"]["notification"]["recipients_list"] = []
                                notification["endpoints"]["notification"]["recipients_list"].append({ "to": info["phone_number"], "group": False })
                            if info.get("phone_number_verified"):
                                notification["endpoints"]["mobile"]["enable"] = info["phone_number_verified"]
                                notification["endpoints"]["notification"]["enable"] = False
                            self.database_client.update_device_notification(username, device["devicename"], source, notification)
        except:
            print("exception")
            pass

        response = json.dumps({'status': 'OK', 'message': 'Confirm verify phone successful'})
        print('\r\nConfirm verify phone successful: {}\r\n{}\r\n'.format(username, response))
        return response


    ########################################################################################################
    #
    # CHANGE PASSWORD
    #
    # - Request:
    #   POST /user/change_password
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   data: {'token': jwtEncode(password, newpassword)}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def change_password(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Change password: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Change password: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('refresh_user_token username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Change password: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Change password: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Change password: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED

        data = flask.request.get_json()
        password, newpassword, reason = rest_api_utils.utils().get_jwtencode_user_pass(data["token"])
        if password is None or newpassword is None:
            response = json.dumps({'status': 'NG', 'message': reason})
            print('\r\nERROR Change password: Password newpassword format invalid\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check length of newpassword
        if len(newpassword) < 8:
            response = json.dumps({'status': 'NG', 'message': 'Password length should at least be 8 characters'})
            print('\r\nERROR Change password: Password length should at least be 8 characters [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # check password is same as newpassword
        if password == newpassword:
            response = json.dumps({'status': 'NG', 'message': 'New password should be different from old password'})
            print('\r\nERROR Change password: New password should be different from old password [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # change password
        result, errorcode = self.database_client.change_password(token["access"], password, newpassword)
        if not result:
            if errorcode == "InvalidPasswordException":
                msg = "Password must be atleast 8 characters with a lowercase character, uppercase character, special character and a number."
            else:
                msg = 'Internal server error'
            response = json.dumps({'status': 'NG', 'message': msg})
            print('\r\nERROR Change password: {} [{}]\r\n'.format(msg, username))
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR

        response = json.dumps({'status': 'OK', 'message': 'Change password successful'})
        print('\r\nChange password successful: {}\r\n{}\r\n'.format(username, response))
        return response


    ########################################################################################################
    #
    # ENABLE MFA
    #
    # - Request:
    #   POST /user/mfa
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   data: {'enable': boolean}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def enable_mfa(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Enable MFA: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Enable MFA: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('enable_mfa username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Enable MFA: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Enable MFA: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Enable MFA: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        data = flask.request.get_json()
        if data.get("enable") is None:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Enable MFA: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        user = self.database_client.get_user_info(token['access'])
        if user.get("phone_number") is None or user.get("phone_number_verified") is None:
            response = json.dumps({'status': 'NG', 'message': 'Phone number is not registered'})
            print('\r\nERROR Enable MFA: Phone number is not registered\r\n')
            return response, status.HTTP_400_BAD_REQUEST
        if user["phone_number_verified"] == False:
            response = json.dumps({'status': 'NG', 'message': 'Phone number is not verified'})
            print('\r\nERROR Enable MFA: Phone number is not verified\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # enable/disable MFA
        if CONFIG_SUPPORT_MFA:
            if user["mfa_enabled"] != data['enable']:
                result = self.database_client.enable_mfa(token['access'], data['enable'])
                if not result:
                    response = json.dumps({'status': 'NG', 'message': 'Request failed'})
                    print('\r\nERROR Enable MFA: Request failed [{}]\r\n'.format(username))
                    return response, status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            response = json.dumps({'status': 'NG', 'message': 'MFA Support has been DISABLED!'})
            print('\r\nERROR Enable MFA: MFA Support has been DISABLED!\r\n')
            return response, status.HTTP_400_BAD_REQUEST


        if data['enable'] == True:
            msg = {'status': 'OK', 'message': 'Enable MFA successful'}
        else:
            msg = {'status': 'OK', 'message': 'Disable MFA successful'}
        response = json.dumps(msg)
        print('\r\n{}: {}\r\n{}\r\n'.format(msg["message"], username, response))
        return response


    ########################################################################################################
    #
    # LOGIN MFA
    #
    # - Request:
    #   POST /user/login/mfa
    #   headers: {'Content-Type': 'application/json'}
    #   data: { 'username': string, 'confirmationcode': string }
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'token': {'access': string, 'id': string, 'refresh': string}, 'name': string }
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def login_mfa(self):
        data = flask.request.get_json()
        if data.get("username") is None or data.get("confirmationcode") is None:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Login MFA: Empty parameter found [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        username = data['username']
        mfacode = data['confirmationcode']
        print('login_mfa username={} confirmationcode={}'.format(username, mfacode))

        # check if a parameter is empty
        if len(username) == 0 or len(mfacode) != 6:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Login MFA: Empty parameter found [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST


        sessionkey = self.redis_client.mfa_get_session(username)
        if sessionkey is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid request'})
            print('\r\nERROR Login MFA: Invalid request [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        access, refresh, id = self.database_client.login_mfa(username, sessionkey, mfacode)
        if not access:
            self.database_client.set_last_login(username, False)
            response = json.dumps({'status': 'NG', 'message': 'Invalid code'})
            print('\r\nERROR Login MFA: Invalid code [{},{}]\r\n'.format(username, mfacode))
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR

        self.redis_client.mfa_del_session(username)

        # delete the couter for failed logins
        attempts = self.redis_client.login_failed_get_attempts(username)
        if attempts is not None:
            self.redis_client.login_failed_del_attempts(username)

        self.database_client.set_last_login(username, True)


        # return name during login as per special request
        name = None
        info = self.database_client.get_user_info(access)
        if info:
            # handle no family name
            if 'given_name' in info:
                name = info['given_name']
            if 'family_name' in info:
                if info['family_name'] != "NONE":
                    name += " " + info['family_name']

        # Disable MFA since it is an expensive feature
        #self.database_client.admin_enable_mfa(username, False)


        msg = {'status': 'OK', 'message': "Login MFA successful", 'token': {'access': access, 'refresh': refresh, 'id': id} }
        if name is not None:
            msg['name'] = name
        response = json.dumps(msg)
        #print('\r\nLogin successful: {}\r\n'.format(username))
        return response


    ########################################################################################################
    #
    # UPDATE USER INFO
    #
    # - Request:
    #   POST /user
    #   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
    #   data: {'name': string, 'phone_number': string}
    #   // phone_number is optional
    #   // phone number should begin with "+" followed by country code then the number (ex. SG number +6512341234)
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def update_user(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Update user: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Update user: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('update_user username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Update user: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Update user: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Update user: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED

        # get the input parameters
        data = flask.request.get_json()
        if data.get('name') is None:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Update user: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST
        if data.get('phone_number') is not None:
            phonenumber = data['phone_number']
        else:
            phonenumber = None

        # verify phone number using phonenumbers library
        try:
            if phonenumber is not None and phonenumber != "":
                if phonenumber[0] != "+":
                    response = json.dumps({'status': 'NG', 'message': 'Phone number should follow the standard E.164 international phone numbering format: +<country code><number>'})
                    print('\r\nERROR Update user: Phone number should follow the standard E.164 international phone numbering format: +<country code><number> [{}]\r\n'.format(phonenumber))
                    return response, status.HTTP_400_BAD_REQUEST

                x = phonenumbers.parse(phonenumber, None)
                if phonenumbers.is_possible_number(x) == False or phonenumbers.is_valid_number(x) == False:
                    response = json.dumps({'status': 'NG', 'message': 'Phone number is not valid'})
                    print('\r\nERROR Update user: Phone number is not valid [{}]\r\n'.format(phonenumber))
                    return response, status.HTTP_400_BAD_REQUEST
        except:
            response = json.dumps({'status': 'NG', 'message': 'Phone number is not valid'})
            print('\r\nERROR Update user: Phone number is not valid [{}]\r\n'.format(phonenumber))
            return response, status.HTTP_400_BAD_REQUEST


        if CONFIG_ALLOW_LOGIN_VIA_PHONE_NUMBER:
            # since login via phone_number is now allowed,
            # the phone_number must be unique,
            # so check if phone_number is already taken or not
            phonenumber_owner = self.database_client.get_username_by_phonenumber(phonenumber)
            if phonenumber_owner is not None:
                if username != phonenumber_owner:
                    response = json.dumps({'status': 'NG', 'message': 'Phone number is already registered to another user'})
                    print('\r\nERROR Update user: Phone number is already registered to another user [{}]\r\n'.format(phonenumber))
                    return response, status.HTTP_400_BAD_REQUEST


        #print(phonenumber)
        name = data['name']
        names = name.split(" ")
        if (len(names) > 1):
            givenname = " ".join(names[:-1])
            familyname = names[-1]
        else:
            # handle no family name
            givenname = names[0]
            familyname = "NONE"


        # when changing number (and MFA is enabled), disable MFA first
        try:
            info = self.database_client.get_user_info(token['access'])
            if info:
                if info.get("mfa_enabled") is not None:
                    if info["mfa_enabled"]:
                        # mfa is enabled
                        if info.get("phone_number") is not None:
                            if info["phone_number"] != phonenumber:
                                # phone number has been changed
                                # disable MFA
                                self.database_client.enable_mfa(token['access'], False)
        except:
            pass


        # change user
        result = self.database_client.update_user(token["access"], phonenumber, givenname, familyname)
        if not result:
            response = json.dumps({'status': 'NG', 'message': 'Request failed'})
            print('\r\nERROR Update user: Request failed [{}]\r\n'.format(username))
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR

        response = json.dumps({'status': 'OK', 'message': 'Change password successful'})
        print('\r\nUpdate user successful: {}\r\n{}\r\n'.format(username, response))
        return response




    ########################################################################################################
    #
    # GET ORGANIZATIONS
    #
    # - Request:
    #   GET /user/organizations
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 
    #    'organizations': [{'orgname': string, 'orgid': string, 'membership': string, 'status': string, 'date': int, 'active': int}, ...]}
    #   {'status': 'NG', 'message': string}
    #
    #
    # SET ACTIVE ORGANIZATION
    #
    # - Request:
    #   POST /user/organizations
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   data: {'orgname': string, 'orgid': string}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_organizations(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get organization: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get organization: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_organizations username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get organization: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get organization: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get organization: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get organizations
        if flask.request.method == 'GET':
            organizations = self.database_client.get_organizations(username)
            msg = {'status': 'OK', 'message': 'Get organizations successful'}
            if organizations:
                msg["organizations"] = organizations
            else:
                msg["message"] = "No organizations"

        elif flask.request.method == 'POST':

            # get the input parameters
            data = flask.request.get_json()
            if data is None or data.get("orgname") is None or data.get("orgid") is None:
                response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
                print('\r\nERROR Get organizations: Empty parameter found\r\n')
                return response, status.HTTP_400_BAD_REQUEST

            organization = self.database_client.set_active_organization(username, data["orgname"], data["orgid"])
            msg = {'status': 'OK', 'message': 'Set active organization successful'}


        response = json.dumps(msg)
        print('\r\n{} successful: {}\r\n'.format(msg["message"], username))
        return response


    ########################################################################################################
    #
    # GET ORGANIZATION
    #
    # - Request:
    #   GET /user/organization
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    #
    # LEAVE ORGANIZATION
    #
    # - Request:
    #   GET /user/organization
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_organization(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get organization: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get organization: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_organization username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get organization: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get organization: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get organization: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get or leave organization
        if flask.request.method == 'GET':

            # get the active organization
            # its ok if no active organization
            orgname, orgid = self.database_client.get_active_organization(username)
            if orgname is None:
                msg = {'status': 'OK', 'message': 'No organization is active'}
                response = json.dumps(msg)
                print('\r\n{} successful: {}\r\n'.format(msg["message"], username))
                return response

            organization = self.database_client.get_organization(username, orgname, orgid)
            msg = {'status': 'OK', 'message': 'Get organization successful'}
            if organization:
                msg["organization"] = organization
            else:
                msg["message"] = "No organization"

        elif flask.request.method == 'DELETE':

            print("leave_organization 1 DELETE")
            # get the active organization
            # its ok if no active organization
            orgname, orgid = self.database_client.get_active_organization(username)
            if orgname is None:
                response = json.dumps({'status': 'NG', 'message': 'No active organization'})
                print('\r\nERROR Leave organization: No active organization\r\n')
                return response, status.HTTP_400_BAD_REQUEST

            self.database_client.leave_organization(username, orgname, orgid)
            msg = {'status': 'OK', 'message': 'Leave organization successful'}


        response = json.dumps(msg)
        print('\r\n{} successful: {}\r\n'.format(msg["message"], username))
        return response


    ########################################################################################################
    #
    # ACCEPT ORGANIZATION INVITATION
    #
    # - Request:
    #   POST /user/organization/invitation
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    #
    # DECLINE ORGANIZATION INVITATION
    #
    # - Request:
    #   POST /user/organization/invitation
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def accept_organization_invitation(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Accept organization invitation: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Accept organization invitation: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('accept_organization_invitation username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Accept organization invitation: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Accept organization invitation: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Accept organization invitation: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # there must be an active organization for these APIs
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is None:
            response = json.dumps({'status': 'NG', 'message': 'No organization is active'})
            print('\r\nERROR Accept organization invitation: No organization is active [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # accept or decline invitation
        if flask.request.method == 'POST':
            result, errorcode = self.database_client.accept_organization_invitation(username, orgname, orgid)
            if not result:
                if errorcode == 401:
                    errormsg = "User is not allowed to accept invitation"
                elif errorcode == 404:
                    errormsg = "User is not allowed to accept invitation"
                else:
                    errormsg = "Accept organization invitation failed"
                response = json.dumps({'status': 'NG', 'message': errormsg})
                print('\r\nERROR {} [{}]\r\n'.format(errormsg, username))
                return response, errorcode
            msg = {'status': 'OK', 'message': 'Accept organization invitation successful'}

        elif flask.request.method == 'DELETE':
            result, errorcode = self.database_client.decline_organization_invitation(username, orgname, orgid)
            if not result:
                if errorcode == 401:
                    errormsg = "User is not allowed to accept invitation"
                elif errorcode == 404:
                    errormsg = "User is not allowed to accept invitation"
                else:
                    errormsg = "Decline organization invitation failed"
                response = json.dumps({'status': 'NG', 'message': errormsg})
                print('\r\nERROR {} [{}]\r\n'.format(errormsg, username))
                return response, errorcode
            msg = {'status': 'OK', 'message': 'Decline organization invitation successful'}

        response = json.dumps(msg)
        print('\r\n{} successful: {}\r\n'.format(msg["message"], username))
        return response
