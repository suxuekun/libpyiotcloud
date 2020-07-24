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
    #   POST /organization
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
    #   POST /organization
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def create_organization(self):
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


        # create or delete organization
        if flask.request.method == 'POST':

            # get the input parameters
            data = flask.request.get_json()
            if data is None:
                response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
                print('\r\nERROR Create organization: Empty parameter found\r\n')
                return response, status.HTTP_400_BAD_REQUEST
            if data.get("orgname") is None:
                response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
                print('\r\nERROR Create organization: Empty parameter found\r\n')
                return response, status.HTTP_400_BAD_REQUEST

            # check orgname
            if data["orgname"].strip() == "":
                response = json.dumps({'status': 'NG', 'message': 'Invalid orgname'})
                print('\r\nERROR Create organization: Invalid orgname\r\n')
                return response, status.HTTP_400_BAD_REQUEST
            if data["orgname"].lower() == "none":
                response = json.dumps({'status': 'NG', 'message': 'Invalid orgname. Orgname reserved'})
                print('\r\nERROR Create organization: Invalid orgname. Orgname is reserved\r\n')
                return response, status.HTTP_400_BAD_REQUEST

            # create organization
            result, errorcode = self.database_client.create_organization(username, data["orgname"])
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

            # there must be an active organization for these APIs
            orgname, orgid = self.database_client.get_active_organization(username)
            if orgname is None:
                response = json.dumps({'status': 'NG', 'message': 'No organization is active'})
                print('\r\nERROR Delete organization: No organization is active [{}]\r\n'.format(username))
                return response, status.HTTP_400_BAD_REQUEST

            # get organization
            result, errorcode = self.database_client.delete_organization(username, orgname, orgid)
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
    #   POST /organization/invitation
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   data: {'emails': [], 'cancel': 1}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def create_organization_invitation(self):
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


        # check parameter
        data = flask.request.get_json()
        if data is None:
            response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
            print('\r\nERROR Create organization invitation: Parameters not included [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST
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


        # there must be an active organization for these APIs
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is None:
            response = json.dumps({'status': 'NG', 'message': 'No organization is active'})
            print('\r\nERROR Create organization invitation: No organization is active [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # create or cancel organization invitation
        results = []
        allfailed = True
        if cancel == 0:
            result = self.database_client.check_create_organization_invitations(username, orgname, orgid, data["emails"])
            if result == False:
                msg = {'status': 'NG', 'message': 'Some of the emails are invalid.'}
            else:
                for email in data["emails"]:
                    result, errorcode = self.database_client.create_organization_invitation(username, orgname, orgid, email)
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
                        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + CONFIG_SEPARATOR + orgname + CONFIG_SEPARATOR + "email" + CONFIG_SEPARATOR + "send_invitation_organization"
                        payload  = {"orgid": orgid, "owner": username, "recipients": []}
                        for result in results:
                            if result["result"] == 1:
                                payload["recipients"].append(result["email"])
                        if len(payload["recipients"]):
                            self.messaging_client.publish(pubtopic, json.dumps(payload))
                    except:
                        print("Send email invitation failed!")
                        pass

        else:
            result = self.database_client.check_cancel_organization_invitations(username, orgname, orgid, data["emails"])
            if result == False:
                msg = {'status': 'NG', 'message': 'Some of the emails are invalid.'}
            else:
                for email in data["emails"]:
                    result, errorcode = self.database_client.cancel_organization_invitation(username, orgname, orgid, email)
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
    #   POST /organization/membership
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   data: {'emails': [], 'remove': 1}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def update_organization_membership(self):
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


        # there must be an active organization for these APIs
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is None:
            response = json.dumps({'status': 'NG', 'message': 'No organization is active'})
            print('\r\nERROR Update organization membership: No organization is active [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # check parameter
        data = flask.request.get_json()
        if data is None:
            response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
            print('\r\nERROR Update organization membership: Parameters not included [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST
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
            result = self.database_client.check_remove_organization_memberships(username, orgname, orgid, data["emails"])
            if result == False:
                msg = {'status': 'NG', 'message': 'Some of the emails are invalid.'}
            else:
                for email in data["emails"]:
                    result, errorcode = self.database_client.remove_organization_membership(username, orgname, orgid, email)
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
    def get_organization_groups(self):
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


        # there must be an active organization for these APIs
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is None:
            response = json.dumps({'status': 'NG', 'message': 'No organization is active'})
            print('\r\nERROR Get organization groups: No organization is active [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # get organization groups
        groups = self.database_client.get_organization_groups(username, orgname, orgid)
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
    def create_organization_group(self, groupname):
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


        # check groupname
        if len(groupname) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Create organization group: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # groupname is not valid
        if groupname == "Ungrouped":
            response = json.dumps({'status': 'NG', 'message': 'Group name is not valid'})
            print('\r\nERROR Create organization group: Group name is not valid\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # there must be an active organization for these APIs
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is None:
            response = json.dumps({'status': 'NG', 'message': 'No organization is active'})
            print('\r\nERROR Get organization groups: No organization is active [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # create or delete organization group
        if flask.request.method == 'POST':

            result, errorcode = self.database_client.create_organization_group(username, orgname, orgid, groupname)
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
            result, errorcode = self.database_client.delete_organization_group(username, orgname, orgid, groupname)
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



    ########################################################################################################
    #
    # GET MEMBERS IN USER GROUP
    #
    # - Request:
    #   GET /organization/groups/group/GROUPNAME/members
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'members': [string]}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_members_in_organization_group(self, groupname):
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


        # there must be an active organization for these APIs
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is None:
            response = json.dumps({'status': 'NG', 'message': 'No organization is active'})
            print('\r\nERROR Get organization group members: No organization is active [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # get organization group members
        result, members = self.database_client.get_members_in_organization_group(username, orgname, orgid, groupname)
        if result:
            msg = {'status': 'OK', 'message': 'Get organization group members successful', 'members': members}
        else:
            msg = {'status': 'NG', 'message': 'Get organization group members failed', 'members': []}


        response = json.dumps(msg)
        print('\r\n{} successful: {}\r\n'.format(msg["message"], username))
        return response


    ########################################################################################################
    #
    # UPDATE MEMBERS IN USER GROUP
    #
    # - Request:
    #   POST /organization/groups/group/GROUPNAME/members
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   data: {'members': [strings]}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def update_members_in_organization_group(self, groupname):
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
        if data is None:
            response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
            print('\r\nERROR Update organization group members: Parameters not included [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST
        if data.get("members") is None:
            response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
            print('\r\nERROR Update organization group members: Parameters not included [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # there must be an active organization for these APIs
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is None:
            response = json.dumps({'status': 'NG', 'message': 'No organization is active'})
            print('\r\nERROR Update organization group members: No organization is active [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # update organization group members
        self.database_client.update_members_in_organization_group(username, orgname, orgid, groupname, data["members"])
        msg = {'status': 'OK', 'message': 'Update organization group members successful'}


        response = json.dumps(msg)
        print('\r\n{} successful: {}\r\n'.format(msg["message"], username))
        return response


    ########################################################################################################
    #
    # ADD MEMBER TO USER GROUP
    #
    # - Request:
    #   POST organization/groups/group/GROUPNAME/members/member/MEMBERNAME
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    #
    # REMOVE MEMBER FROM USER GROUP
    #
    # - Request:
    #   DELETE organization/groups/group/GROUPNAME/members/member/MEMBERNAME
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def add_member_to_organization_group(self, groupname, membername):
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


        # there must be an active organization for these APIs
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is None:
            response = json.dumps({'status': 'NG', 'message': 'No organization is active'})
            print('\r\nERROR Add organization group member: No organization is active [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # add or remove organization group member
        if flask.request.method == 'POST':
            result, errcode = self.database_client.add_member_to_organization_group(username, orgname, orgid, groupname, membername)
            if result:
                msg = {'status': 'OK', 'message': 'Add organization group member successful'}
            else:
                msg = {'status': 'NG', 'message': 'Add organization group member failed'}

        elif flask.request.method == 'DELETE':
            result, errcode = self.database_client.remove_member_from_organization_group(username, orgname, orgid, groupname, membername)
            if result:
                msg = {'status': 'OK', 'message': 'Remove organization group member successful'}
            else:
                msg = {'status': 'NG', 'message': 'Remove organization group member failed'}


        response = json.dumps(msg)
        print('\r\n{}: {}\r\n'.format(msg["message"], username))
        return response




    ########################################################################################################
    #
    # GET ORGANIZATION POLICIES
    #
    # - Request:
    #   GET /organizations/organization/<orgname>/policies
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'policies': [{'policyname': string}]}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_organization_policies(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get organization policies: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get organization policies: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_organization_policies username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get organization policies: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get organization policies: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get organization policies: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # there must be an active organization for these APIs
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is None:
            response = json.dumps({'status': 'NG', 'message': 'No organization is active'})
            print('\r\nERROR Get organization policies: No organization is active [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # get organization policies
        policies = self.database_client.get_organization_policies(username, orgname, orgid)
        msg = {'status': 'OK', 'message': 'Get organization policies successful', 'policies': policies}


        response = json.dumps(msg)
        print('\r\n{} successful: {}\r\n'.format(msg["message"], username))
        return response


    ########################################################################################################
    #
    # GET POLICY
    #
    # - Request:
    #   POST /organizations/organization/<orgname>/policies/policy/<policyname>
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    #
    # CREATE/UPDATE POLICY
    #
    # - Request:
    #   POST /organizations/organization/<orgname>/policies/policy/<policyname>
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    #
    # DELETE POLICY
    #
    # - Request:
    #   POST /organizations/organization/<orgname>/policies/policy/<policyname>
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def create_organization_policy(self, policyname):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Create organization policy: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Create organization policy: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('create_organization_policy username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Create organization policy: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Create organization policy: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Create organization policy: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # check policyname
        if len(policyname) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Create organization policy: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # there must be an active organization for these APIs
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is None:
            response = json.dumps({'status': 'NG', 'message': 'No organization is active'})
            print('\r\nERROR Create organization policy: No organization is active [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # get or create or delete organization policy
        if flask.request.method == 'GET':

            policy = self.database_client.get_organization_policy(username, orgname, orgid, policyname)
            if policy is None:
                errormsg = "Get organization policy failed"
                response = json.dumps({'status': 'NG', 'message': errormsg})
                print('\r\nERROR {} [{}]\r\n'.format(errormsg, username))
                return response, errorcode
            msg = {'status': 'OK', 'message': 'Get organization policy successful', 'settings': policy['settings']}

        elif flask.request.method == 'POST':

            # get the input parameters
            data = flask.request.get_json()
            if data is None:
                response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
                print('\r\nERROR Create organization policy: Empty parameter found\r\n')
                return response, status.HTTP_400_BAD_REQUEST
            if data.get("settings") is None:
                response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
                print('\r\nERROR Create organization policy: Empty parameter found\r\n')
                return response, status.HTTP_400_BAD_REQUEST

            result, errorcode = self.database_client.create_organization_policy(username, orgname, orgid, policyname, data["settings"])
            if not result:
                if errorcode == 401:
                    errormsg = "Organization policy name already taken"
                elif errorcode == 400:
                    errormsg = "Updating default organization policy is not allowed"
                else:
                    errormsg = "Creating/updating organization policy failed"
                response = json.dumps({'status': 'NG', 'message': errormsg})
                print('\r\nERROR {} [{}]\r\n'.format(errormsg, username))
                return response, errorcode
            msg = {'status': 'OK', 'message': 'Create organization policy successful'}

        elif flask.request.method == 'DELETE':

            # get organization
            result, errorcode = self.database_client.delete_organization_policy(username, orgname, orgid, policyname)
            if not result:
                if errorcode == 404:
                    errormsg = "Organization policy not found"
                elif errorcode == 401:
                    errormsg = "User is not the owner of the organization"
                elif errorcode == 400:
                    errormsg = "Deleting default organization policy is not allowed"
                else:
                    errormsg = "Delete organization policy failed"
                response = json.dumps({'status': 'NG', 'message': errormsg})
                print('\r\nERROR {} [{}]\r\n'.format(errormsg, username))
                return response, errorcode

            msg = {'status': 'OK', 'message': 'Delete organization policy successful'}


        print('\r\n{}: {}\r\n'.format(msg["message"], username))
        response = json.dumps(msg)
        return response

    ########################################################################################################
    #
    # GET ORGANIZATION POLICY SETTINGS
    #
    # - Request:
    #   GET /organizations/organization/settings
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'settings': [{'label': string, 'crud': []}]}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_organization_policy_settings(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get organization policy settings: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get organization policy settings: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_organization_policy_settings username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get organization policy settings: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get organization policy settings: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get organization policy settings: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED



        # get policy settings
        settings = self.database_client.get_policy_settings()
        msg = {'status': 'OK', 'message': 'Get organization policy settings successful', 'settings': settings}


        response = json.dumps(msg)
        print('\r\n{} successful: {}\r\n'.format(msg["message"], username))
        return response


    ########################################################################################################
    #
    # GET POLICIES IN USER GROUP
    #
    # - Request:
    #   GET /organization/groups/group/GROUPNAME/policies
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'policies': [string]}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_policies_in_organization_group(self, groupname):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get organization group policies: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get organization group policies: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_policies_in_organization_group username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get organization group policies: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get organization group policies: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get organization group policies: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # there must be an active organization for these APIs
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is None:
            response = json.dumps({'status': 'NG', 'message': 'No organization is active'})
            print('\r\nERROR Get organization group policies: No organization is active [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # get organization group policies
        result, policies = self.database_client.get_policies_in_organization_group(username, orgname, orgid, groupname)
        if result:
            msg = {'status': 'OK', 'message': 'Get organization group policies successful', 'policies': policies}
        else:
            msg = {'status': 'NG', 'message': 'Get organization group policies failed', 'policies': []}


        response = json.dumps(msg)
        print('\r\n{} successful: {}\r\n'.format(msg["message"], username))
        return response

    ########################################################################################################
    #
    # UPDATE POLICIES IN USER GROUP
    #
    # - Request:
    #   POST /organization/groups/group/GROUPNAME/policies
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #   data: {'policies': [strings]}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def update_policies_in_organization_group(self, groupname):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Update organization group policies: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Update organization group policies: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('update_policies_in_organization_group username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Update organization group policies: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Update organization group policies: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Update organization group policies: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # check parameter
        data = flask.request.get_json()
        if data is None:
            response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
            print('\r\nERROR Update organization group policies: Parameters not included [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST
        if data.get("policies") is None:
            response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
            print('\r\nERROR Update organization group policies: Parameters not included [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # there must be an active organization for these APIs
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is None:
            response = json.dumps({'status': 'NG', 'message': 'No organization is active'})
            print('\r\nERROR Update organization group policies: No organization is active [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # update organization group policies
        self.database_client.update_policies_in_organization_group(username, orgname, orgid, groupname, data["policies"])
        msg = {'status': 'OK', 'message': 'Update organization group policies successful'}


        response = json.dumps(msg)
        print('\r\n{} successful: {}\r\n'.format(msg["message"], username))
        return response


    ########################################################################################################
    #
    # ADD POLICY TO USER GROUP
    #
    # - Request:
    #   POST organization/groups/group/GROUPNAME/policies/policy/POLICYNAME
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    #
    # REMOVE POLICY FROM USER GROUP
    #
    # - Request:
    #   DELETE organization/groups/group/GROUPNAME/policies/policy/POLICYNAME
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def add_policy_to_organization_group(self, groupname, policyname):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Add organization group policy: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Add organization group policy: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('add_policy_to_organization_group username={}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Add organization group policy: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2: # token expired
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Add organization group policy: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Add organization group policy: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # there must be an active organization for these APIs
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is None:
            response = json.dumps({'status': 'NG', 'message': 'No organization is active'})
            print('\r\nERROR Add organization group policy: No organization is active [{}]\r\n'.format(username))
            return response, status.HTTP_400_BAD_REQUEST

        # add or remove organization group policy
        if flask.request.method == 'POST':
            result, errcode = self.database_client.add_policy_to_organization_group(username, orgname, orgid, groupname, policyname)
            if result:
                msg = {'status': 'OK', 'message': 'Add organization group policy successful'}
            else:
                msg = {'status': 'NG', 'message': 'Add organization group policy failed'}

        elif flask.request.method == 'DELETE':
            result, errcode = self.database_client.remove_policy_from_organization_group(username, orgname, orgid, groupname, policyname)
            if result:
                msg = {'status': 'OK', 'message': 'Remove organization group policy successful'}
            else:
                msg = {'status': 'NG', 'message': 'Remove organization group policy failed'}


        response = json.dumps(msg)
        print('\r\n{}: {}\r\n'.format(msg["message"], username))
        return response
