#import os
#import ssl
import json
#import time
#import hmac
#import hashlib
import flask
#import base64
#import datetime
#import calendar
#from flask_json import FlaskJSON, JsonError, json_response, as_json
#from certificate_generator import certificate_generator
#from messaging_client import messaging_client
#from rest_api_config import config
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



CONFIG_SEPARATOR            = '/'
CONFIG_PREPEND_REPLY_TOPIC  = "server"



class access_control:

    def __init__(self, database_client, messaging_client):
        self.database_client = database_client
        self.messaging_client = messaging_client


    ########################################################################################################
    #
    # CREATE ORGANIZATION
    #
    # - Request:
    #   POST /organizations/organization/ORGNAME
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    #
    # DELETE ORGANIZATION
    #
    # - Request:
    #   POST /organizations/organization/ORGNAME
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def create_organization(self, orgname):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Create organization: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Create organization: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('create_organization username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Create organization: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Create organization: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Create organization: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # check orgname
        if len(orgname) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Create organization: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # create or delete organization
        if flask.request.method == 'POST':

            result, errorcode = self.database_client.create_organization(username, orgname)
            if not result:
                if errorcode == 401:
                    errormsg = "Cannot create another organization"
                elif errorcode == 409:
                    errormsg = "Organization name already taken"
                else:
                    errormsg = "Create organization failed"
                response = json.dumps({'status': 'NG', 'message': errormsg})
                print('\r\nERROR {} [{}]\r\n'.format(errormsg, username))
                return response, errorcode
            msg = {'status': 'OK', 'message': 'Create organization successful'}

        elif flask.request.method == 'DELETE':

            # get organization
            result, errorcode = self.database_client.delete_organization(username, orgname)
            if not result:
                if errorcode == 404:
                    errormsg = "Organization not found"
                elif errorcode == 401:
                    errormsg = "User is not the owner of the organization"
                else:
                    errormsg = "Delete organization failed"
                response = json.dumps({'status': 'NG', 'message': errormsg})
                print('\r\nERROR {} [{}]\r\n'.format(errormsg, username))
                return response, errorcode

            msg = {'status': 'OK', 'message': 'Delete organization successful'}


        print('\r\n{}: {}\r\n'.format(msg["message"], username))
        response = json.dumps(msg)
        return response


    ########################################################################################################
    #
    # CREATE/CANCEL INVITATIONS
    #
    # - Request:
    #   POST /organizations/organization/ORGNAME/invitation
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   data: {'emails': [], 'cancel': 1}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def create_organization_invitation(self, orgname):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Create organization invitation: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Create organization invitation: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('create_organization_invitation username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Create organization invitation: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Create organization invitation: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Create organization invitation: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # check orgname
        if len(orgname) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Create organization invitation: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check parameter
        data = flask.request.get_json()
        #print(data)
        if data.get("emails") is None:
            response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
            print('\r\nERROR Create organization invitation: Parameters not included [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST
        if len(data["emails"]) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
            print('\r\nERROR Create organization invitation: Parameters not included [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST
        cancel = 0
        if data.get("cancel") is not None:
            cancel = data["cancel"]

        # create or cancel organization invitation
        results = []
        allfailed = True
        if cancel == 0:
            result = self.database_client.check_create_organization_invitations(username, orgname, data["emails"])
            if result == False:
                msg = {'status': 'NG', 'message': 'Some of the emails are invalid.'}
            else:
                for email in data["emails"]:
                    result, errorcode = self.database_client.create_organization_invitation(username, orgname, email)
                    if not result:
                        if errorcode == 400:
                            errormsg = "User already a member of the organization"
                        elif errorcode == 401:
                            errormsg = "User is not the owner of the organization"
                        elif errorcode == 404:
                            errormsg = "Organization not found"
                        elif errorcode == 409:
                            errormsg = "User already exist"
                        else:
                            errormsg = "Create organization invitation failed"
                        results.append({"email": email, "result": 0, "errormsg": errormsg})
                    else:
                        allfailed = False
                        results.append({"email": email, "result": 1})
                if allfailed == True:
                    msg = {'status': 'NG', 'message': 'Create organization invitation failed', 'results': results}
                else:
                    msg = {'status': 'OK', 'message': 'Create organization invitation successful', 'results': results}

                    # send email invitation
                    try:
                        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + CONFIG_SEPARATOR + orgname + CONFIG_SEPARATOR + "send_invitation_organization"
                        payload  = {"owner": username, "recipients": []}
                        for result in results:
                            if result["result"] == 1:
                                payload["recipients"].append(result["email"])
                        if len(payload["recipients"]):
                            self.messaging_client.publish(pubtopic, json.dumps(payload))
                    except:
                        print("Send email invitation failed!")
                        pass

        else:
            result = self.database_client.check_cancel_organization_invitations(username, orgname, data["emails"])
            if result == False:
                msg = {'status': 'NG', 'message': 'Some of the emails are invalid.'}
            else:
                for email in data["emails"]:
                    result, errorcode = self.database_client.cancel_organization_invitation(username, orgname, email)
                    if not result:
                        if errorcode == 400:
                            errormsg = "User status is not Invited"
                        elif errorcode == 401:
                            errormsg = "User is not the owner of the organization"
                        elif errorcode == 404:
                            errormsg = "Organization or user not found"
                        else:
                            errormsg = "Delete organization invitation failed"
                        results.append({"email": email, "result": 0, "errormsg": errormsg})
                    else:
                        allfailed = False
                        results.append({"email": email, "result": 1})
                if allfailed == True:
                    msg = {'status': 'NG', 'message': 'Delete organization invitation failed', 'results': results}
                else:
                    msg = {'status': 'OK', 'message': 'Delete organization invitation successful', 'results': results}


        print('\r\n{}: {}\r\n'.format(msg["message"], username))
        response = json.dumps(msg)
        return response


    ########################################################################################################
    #
    # UPDATE/REMOVE MEMBERSHIPS
    #
    # - Request:
    #   POST /organizations/organization/ORGNAME/membership
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   data: {'emails': [], 'remove': 1}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def update_organization_membership(self, orgname):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Update organization membership: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Update organization membership: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('create_organization_invitation username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Update organization membership: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Update organization membership: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Update organization membership: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # check orgname
        if len(orgname) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Update organization membership: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check parameter
        data = flask.request.get_json()
        #print(data)
        if data.get("emails") is None:
            response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
            print('\r\nERROR Update organization membership: Parameters not included [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST
        if len(data["emails"]) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
            print('\r\nERROR Update organization membership: Parameters not included [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST
        remove = 0
        if data.get("remove") is not None:
            remove = data["remove"]

        # update or remove organization membership
        results = []
        allfailed = True
        if remove == 0:
            msg = {'status': 'OK', 'message': 'Update membership successful', 'results': results}
            pass

        else:
            result = self.database_client.check_remove_organization_memberships(username, orgname, data["emails"])
            if result == False:
                msg = {'status': 'NG', 'message': 'Some of the emails are invalid.'}
            else:
                for email in data["emails"]:
                    result, errorcode = self.database_client.remove_organization_membership(username, orgname, email)
                    if not result:
                        if errorcode == 400:
                            errormsg = "User status is not Invited"
                        elif errorcode == 401:
                            errormsg = "User is not the owner of the organization"
                        elif errorcode == 404:
                            errormsg = "Organization or user not found"
                        else:
                            errormsg = "Remove membership failed"
                        results.append({"email": email, "result": 0, "errormsg": errormsg})
                    else:
                        allfailed = False
                        results.append({"email": email, "result": 1})
                if allfailed == True:
                    msg = {'status': 'NG', 'message': 'Remove membership failed', 'results': results}
                else:
                    msg = {'status': 'OK', 'message': 'Remove membership successful', 'results': results}


        print('\r\n{}: {}\r\n'.format(msg["message"], username))
        response = json.dumps(msg)
        return response




    ########################################################################################################
    #
    # GET ORGANIZATION GROUPS
    #
    # - Request:
    #   GET /organizations/organization/<orgname>/groups
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'groups': {'groupname': string, 'members': [string]}}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_organization_groups(self, orgname):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get organization groups: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get organization groups: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_organization_groups username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get organization groups: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get organization groups: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get organization groups: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get organization groups
        groups = self.database_client.get_organization_groups(username, orgname)
        msg = {'status': 'OK', 'message': 'Get organization groups successful', 'groups': groups}


        response = json.dumps(msg)
        print('\r\n{} successful: {}\r\n'.format(msg["message"], username))
        return response


    ########################################################################################################
    #
    # CREATE USER GROUP
    #
    # - Request:
    #   POST /organizations/organization/<orgname>/groups/group/<groupname>
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    #
    # DELETE USER GROUP
    #
    # - Request:
    #   POST /organizations/organization/<orgname>/groups/group/<groupname>
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def create_organization_group(self, orgname, groupname):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Create organization group: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Create organization group: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('create_organization_group username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Create organization group: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Create organization group: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Create organization group: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # check orgname
        if len(orgname) == 0 or len(groupname) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Create organization group: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # groupname is not valid
        if groupname == "Ungrouped":
            response = json.dumps({'status': 'NG', 'message': 'Group name is not valid'})
            print('\r\nERROR Create organization group: Group name is not valid\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # create or delete organization group
        if flask.request.method == 'POST':

            result, errorcode = self.database_client.create_organization_group(username, orgname, groupname)
            if not result:
                if errorcode == 409:
                    errormsg = "Organization group name already taken"
                else:
                    errormsg = "Create organization group failed"
                response = json.dumps({'status': 'NG', 'message': errormsg})
                print('\r\nERROR {} [{}]\r\n'.format(errormsg, username))
                return response, errorcode
            msg = {'status': 'OK', 'message': 'Create organization group successful'}

        elif flask.request.method == 'DELETE':

            # get organization
            result, errorcode = self.database_client.delete_organization_group(username, orgname, groupname)
            if not result:
                if errorcode == 404:
                    errormsg = "Organization group not found"
                elif errorcode == 401:
                    errormsg = "User is not the owner of the organization"
                else:
                    errormsg = "Delete organization group failed"
                response = json.dumps({'status': 'NG', 'message': errormsg})
                print('\r\nERROR {} [{}]\r\n'.format(errormsg, username))
                return response, errorcode

            msg = {'status': 'OK', 'message': 'Delete organization group successful'}


        print('\r\n{}: {}\r\n'.format(msg["message"], username))
        response = json.dumps(msg)
        return response



    def get_members_in_organization_group(self, orgname, groupname):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get organization group members: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get organization group members: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_members_in_organization_group username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get organization group members: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get organization group members: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get organization group members: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get organization group members
        result, members = self.database_client.get_members_in_organization_group(username, orgname, groupname)
        if result:
            msg = {'status': 'OK', 'message': 'Get organization group members successful', 'members': members}
        else:
            msg = {'status': 'NG', 'message': 'Get organization group members failed', 'members': []}


        response = json.dumps(msg)
        print('\r\n{} successful: {}\r\n'.format(msg["message"], username))
        return response

    def update_members_in_organization_group(self, orgname, groupname):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Update organization group members: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Update organization group members: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('update_members_in_organization_group username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Update organization group members: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Update organization group members: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Update organization group members: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # check parameter
        data = flask.request.get_json()
        #print(data)
        if data.get("members") is None:
            response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
            print('\r\nERROR Update organization group members: Parameters not included [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # update organization group members
        self.database_client.update_members_in_organization_group(username, orgname, groupname, data["members"])
        msg = {'status': 'OK', 'message': 'Update organization group members successful'}


        response = json.dumps(msg)
        print('\r\n{} successful: {}\r\n'.format(msg["message"], username))
        return response

    def add_member_to_organization_group(self, orgname, groupname, membername):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Add organization group member: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Add organization group member: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('add_member_to_organization_group username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Add organization group member: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Add organization group member: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Add organization group member: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # add or remove organization group member
        if flask.request.method == 'POST':
            result, errcode = self.database_client.add_member_to_organization_group(username, orgname, groupname, membername)
            if result:
                msg = {'status': 'OK', 'message': 'Add organization group member successful'}
            else:
                msg = {'status': 'NG', 'message': 'Add organization group member failed'}

        elif flask.request.method == 'DELETE':
            result, errcode = self.database_client.remove_member_from_organization_group(username, orgname, groupname, membername)
            if result:
                msg = {'status': 'OK', 'message': 'Remove organization group member successful'}
            else:
                msg = {'status': 'NG', 'message': 'Remove organization group member failed'}


        response = json.dumps(msg)
        print('\r\n{}: {}\r\n'.format(msg["message"], username))
        return response


