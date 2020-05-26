import os
import ssl
import json
import time
import hmac
import hashlib
import flask
import base64
import datetime
import calendar
from flask_json import FlaskJSON, JsonError, json_response, as_json
from certificate_generator import certificate_generator
from messaging_client import messaging_client
from rest_api_config import config
from database import database_client, database_categorylabel, database_crudindex
from flask_cors import CORS
from flask_api import status
import jwt
#from jose import jwk, jwt
import http.client
from s3_client import s3_client
import threading
import copy
from redis_client import redis_client
import statistics

from message_broker_api import message_broker_api

from rest_api_messaging_requests import messaging_requests
from rest_api_identity_authentication import identity_authentication
from rest_api_access_control import access_control
from rest_api_payment_accounting import payment_accounting
from rest_api_device_groups import device_groups
from rest_api_device_locations import device_locations
from rest_api_device_otaupdates import device_otaupdates
from rest_api_device_hierarchies import device_hierarchies
from rest_api_device_histories import device_histories
from rest_api_other_stuffs import other_stuffs
import rest_api_utils



###################################################################################
# Some configurations
###################################################################################

CONFIG_DEVICE_ID            = "restapi_manager"

CONFIG_USE_ECC              = True if int(os.environ["CONFIG_USE_ECC"]) == 1 else False
CONFIG_SEPARATOR            = '/'
CONFIG_PREPEND_REPLY_TOPIC  = "server"

CONFIG_USE_REDIS_FOR_MQTT_RESPONSE  = True



###################################################################################
# global variables
###################################################################################

g_messaging_client          = None
g_database_client           = None
g_storage_client            = None
g_redis_client              = None
g_queue_dict  = {} # no longer used; replaced by redis
g_event_dict  = {} # still used to trigger event from callback thread to rest api thread
app = flask.Flask(__name__)
CORS(app)



###################################################################################
# Class instances
###################################################################################

g_messaging_requests        = None
g_identity_authentication   = None
g_access_control            = None
g_payment_accounting        = None
g_device_locations          = None
g_device_groups             = None
g_device_otaupdates         = None
g_device_hierarchies        = None
g_device_histories          = None
g_other_stuffs              = None
g_utils                     = None


###################################################################################
# HTTP REST APIs
###################################################################################

@app.route('/')
def index():
    return "", status.HTTP_401_UNAUTHORIZED



########################################################################################################
#
# IDENTITY AUTHENTICATION
#
########################################################################################################

@app.route('/user/signup', methods=['POST'])
def signup():
    return g_identity_authentication.signup()

@app.route('/user/confirm_signup', methods=['POST'])
def confirm_signup():
    return g_identity_authentication.confirm_signup()

@app.route('/user/resend_confirmation_code', methods=['POST'])
def resend_confirmation_code():
    return g_identity_authentication.resend_confirmation_code()

@app.route('/user/forgot_password', methods=['POST'])
def forgot_password():
    return g_identity_authentication.forgot_password()

@app.route('/user/confirm_forgot_password', methods=['POST'])
def confirm_forgot_password():
    return g_identity_authentication.confirm_forgot_password()

@app.route('/user/login', methods=['POST'])
def login():
    # flask.request.endpoint
    return g_identity_authentication.login()

@app.route('/user/logout', methods=['POST'])
def logout():
    return g_identity_authentication.logout()

@app.route('/user', methods=['GET'])
def get_user():
    return g_identity_authentication.get_user()

@app.route('/user', methods=['POST'])
def update_user():
    return g_identity_authentication.update_user()

@app.route('/user', methods=['DELETE'])
def delete_user():
    return g_identity_authentication.delete_user()

@app.route('/user/token', methods=['POST'])
def refresh_user_token():
    return g_identity_authentication.refresh_user_token()

@app.route('/user/verify_phone_number', methods=['POST'])
def verify_phone_number():
    return g_identity_authentication.verify_phone_number()

@app.route('/user/confirm_verify_phone_number', methods=['POST'])
def confirm_verify_phone_number():
    return g_identity_authentication.confirm_verify_phone_number()

@app.route('/user/change_password', methods=['POST'])
def change_password():
    return g_identity_authentication.change_password()

@app.route('/user/login/idp/code/<id>', methods=['POST'])
def login_idp_storecode(id):
    return g_identity_authentication.login_idp_storecode(id)

@app.route('/user/login/idp/code/<id>', methods=['GET'])
def login_idp_querycode(id):
    return g_identity_authentication.login_idp_querycode(id)

@app.route('/user/mfa', methods=['POST'])
def enable_mfa():
    return g_identity_authentication.enable_mfa()

@app.route('/user/login/mfa', methods=['POST'])
def login_mfa():
    return g_identity_authentication.login_mfa()


@app.route('/user/organizations', methods=['GET'])
def get_organizations():
    return g_identity_authentication.get_organizations()

@app.route('/user/organizations', methods=['POST'])
def set_active_organization():
    return g_identity_authentication.get_organizations()

@app.route('/user/organization', methods=['GET'])
def get_organization():
    return g_identity_authentication.get_organization()

@app.route('/user/organization', methods=['DELETE'])
def leave_organization():
    print("leave_organization 1")
    return g_identity_authentication.get_organization()

@app.route('/user/organization/invitation', methods=['POST'])
def accept_organization_invitation():
    return g_identity_authentication.accept_organization_invitation()

@app.route('/user/organization/invitation', methods=['DELETE'])
def decline_organization_invitation():
    return g_identity_authentication.accept_organization_invitation()

g_identity_authentication_list = [
    { "name": "SIGN-UP",                         "func": signup,                          "api": "/user/signup",                      "method": "POST"   },
    { "name": "CONFIRM SIGN-UP",                 "func": confirm_signup,                  "api": "/user/confirm_signup",              "method": "POST"   },
    { "name": "RESEND CONFIRMATION CODE",        "func": resend_confirmation_code,        "api": "/user/resend_confirmation_code",    "method": "POST"   },
    { "name": "FORGOT PASSWORD",                 "func": forgot_password,                 "api": "/user/forgot_password",             "method": "POST"   },
    { "name": "CONFIRM FORGOT PASSWORD",         "func": confirm_forgot_password,         "api": "/user/confirm_forgot_password",     "method": "POST"   },
    { "name": "LOGIN",                           "func": login,                           "api": "/user/login",                       "method": "POST"   },
    { "name": "LOGOUT",                          "func": logout,                          "api": "/user/logout",                      "method": "POST"   },
    { "name": "GET USER INFO",                   "func": get_user,                        "api": "/user",                             "method": "GET"    },
    { "name": "UPDATE USER INFO",                "func": update_user,                     "api": "/user",                             "method": "POST"   },
    { "name": "DELETE USER",                     "func": delete_user,                     "api": "/user",                             "method": "DELETE" },
    { "name": "REFRESH USER TOKEN",              "func": refresh_user_token,              "api": "/user/token",                       "method": "POST"   },
    { "name": "VERIFY PHONE NUMBER",             "func": verify_phone_number,             "api": "/user/verify_phone_number",         "method": "POST"   },
    { "name": "CONFIRM VERIFY PHONE NUMBER",     "func": confirm_verify_phone_number,     "api": "/user/confirm_verify_phone_number", "method": "POST"   },
    { "name": "CHANGE PASSWORD",                 "func": change_password,                 "api": "/user/change_password",             "method": "POST"   },
    { "name": "LOGIN IDP STORE CODE",            "func": login_idp_storecode,             "api": "/user/login/idp/code/<id>",         "method": "POST"   },
    { "name": "LOGIN IDP QUERY CODE",            "func": login_idp_querycode,             "api": "/user/login/idp/code/<id>",         "method": "GET"    },
    { "name": "ENABLE MFA",                      "func": enable_mfa,                      "api": "/user/mfa",                         "method": "POST"   },
    { "name": "LOGIN MFA",                       "func": login_mfa,                       "api": "/user/login/mfa",                   "method": "POST"   },

    { "name": "GET ORGANIZATIONS",               "func": get_organizations,               "api": "/user/organizations",               "method": "GET"    },
    { "name": "SET ACTIVE ORGANIZATION",         "func": get_organizations,               "api": "/user/organizations",               "method": "POST"   },
    { "name": "GET ORGANIZATION",                "func": get_organization,                "api": "/user/organization",                "method": "GET"    },
    { "name": "LEAVE ORGANIZATION",              "func": get_organization,                "api": "/user/organization",                "method": "DELETE" },
    { "name": "ACCEPT ORGANIZATION INVITATION",  "func": accept_organization_invitation,  "api": "/user/organization/invitation",     "method": "POST"   },
    { "name": "DECLINE ORGANIZATION INVITATION", "func": decline_organization_invitation, "api": "/user/organization/invitation",     "method": "DELETE" },
]


########################################################################################################
#
# ACCESS CONTROL
#
########################################################################################################

@app.route('/organization', methods=['POST'])
def create_organization():
    return g_access_control.create_organization()

@app.route('/organization', methods=['DELETE'])
def delete_organization():
    return g_access_control.create_organization()

@app.route('/organization/invitation', methods=['POST'])
def create_organization_invitation():
    return g_access_control.create_organization_invitation()

@app.route('/organization/membership', methods=['POST'])
def update_organization_membership():
    return g_access_control.update_organization_membership()


#############
# GROUPS

@app.route('/organization/groups', methods=['GET'])
def get_organization_groups():
    return g_access_control.get_organization_groups()

@app.route('/organization/groups/group/<groupname>', methods=['POST'])
def create_organization_group(groupname):
    return g_access_control.create_organization_group(groupname)

@app.route('/organization/groups/group/<groupname>', methods=['DELETE'])
def delete_organization_group(groupname):
    return g_access_control.create_organization_group(groupname)

@app.route('/organization/groups/group/<groupname>/members', methods=['GET'])
def get_members_in_organization_group(groupname):
    return g_access_control.get_members_in_organization_group(groupname)

@app.route('/organization/groups/group/<groupname>/members', methods=['POST'])
def update_members_in_organization_group(groupname):
    return g_access_control.update_members_in_organization_group(groupname)

@app.route('/organization/groups/group/<groupname>/members/member/<membername>', methods=['POST'])
def add_member_to_organization_group(groupname, membername):
    return g_access_control.add_member_to_organization_group(groupname, membername)

@app.route('/organization/groups/group/<groupname>/members/member/<membername>', methods=['DELETE'])
def remove_member_from_organization_group(groupname, membername):
    return g_access_control.add_member_to_organization_group(groupname, membername)


#############
# POLICIES

@app.route('/organization/policies', methods=['GET'])
def get_organization_policies():
    return g_access_control.get_organization_policies()

@app.route('/organization/policies/policy/<policyname>', methods=['GET'])
def get_organization_policy(policyname):
    return g_access_control.create_organization_policy(policyname)

@app.route('/organization/policies/policy/<policyname>', methods=['POST'])
def create_organization_policy(policyname):
    return g_access_control.create_organization_policy(policyname)

@app.route('/organization/policies/policy/<policyname>', methods=['DELETE'])
def delete_organization_policy(policyname):
    return g_access_control.create_organization_policy(policyname)

@app.route('/organization/policies/settings', methods=['GET'])
def get_organization_policy_settings():
    return g_access_control.get_organization_policy_settings()


@app.route('/organization/groups/group/<groupname>/policies', methods=['GET'])
def get_policies_in_organization_group(groupname):
    return g_access_control.get_policies_in_organization_group(groupname)

@app.route('/organization/groups/group/<groupname>/policies', methods=['POST'])
def update_policies_in_organization_group(groupname):
    return g_access_control.update_policies_in_organization_group(groupname)

@app.route('/organization/groups/group/<groupname>/policies/policy/<policyname>', methods=['POST'])
def add_policy_to_organization_group(groupname, policyname):
    return g_access_control.add_policy_to_organization_group(groupname, policyname)

@app.route('/organization/groups/group/<groupname>/policies/policy/<policyname>', methods=['DELETE'])
def remove_policy_from_organization_group(groupname, policyname):
    return g_access_control.add_policy_to_organization_group(groupname, policyname)


g_access_control_list = [
    { "name": "CREATE ORGANIZATION",           "func": create_organization,                   "api": "/organization",                                                       "method": "POST"   },
    { "name": "DELETE ORGANIZATION",           "func": create_organization,                   "api": "/organization",                                                       "method": "DELETE" },
    { "name": "CREATE/CANCEL INVITATIONS",     "func": create_organization_invitation,        "api": "/organization/invitation",                                            "method": "POST"   },
    { "name": "UPDATE/REMOVE MEMBERSHIPS",     "func": update_organization_membership,        "api": "/organization/membership",                                            "method": "POST"   },

    { "name": "GET USER GROUPS",               "func": get_organization_groups,               "api": "/organization/groups",                                                "method": "GET"    },
    { "name": "CREATE USER GROUP",             "func": create_organization_group,             "api": "/organization/groups/group/<groupname>",                              "method": "POST"   },
    { "name": "DELETE USER GROUP",             "func": delete_organization_group,             "api": "/organization/groups/group/<groupname>",                              "method": "DELETE" },

    { "name": "GET MEMBERS IN USER GROUP",     "func": get_members_in_organization_group,     "api": "/organization/groups/group/<groupname>/members",                      "method": "GET"    },
    { "name": "UPDATE MEMBERS IN USER GROUP",  "func": update_members_in_organization_group,  "api": "/organization/groups/group/<groupname>/members",                      "method": "POST"   },
    { "name": "ADD MEMBER TO USER GROUP",      "func": add_member_to_organization_group,      "api": "/organization/groups/group/<groupname>/members/member/<membername>",  "method": "POST"   },
    { "name": "REMOVE MEMBER FROM USER GROUP", "func": remove_member_from_organization_group, "api": "/organization/groups/group/<groupname>/members/member/<membername>",  "method": "DELETE" },

    { "name": "GET POLICIES",                  "func": get_organization_policies,             "api": "/organization/policies",                                              "method": "GET"    },
    { "name": "GET POLICY",                    "func": get_organization_policy,               "api": "/organization/policies/policy/<policyname>",                          "method": "GET"    },
    { "name": "CREATE/UPDATE POLICY",          "func": create_organization_policy,            "api": "/organization/policies/policy/<policyname>",                          "method": "POST"   },
    { "name": "DELETE POLICY",                 "func": delete_organization_policy,            "api": "/organization/policies/policy/<policyname>",                          "method": "DELETE" },
    { "name": "GET POLICY SETTINGS",           "func": get_organization_policy_settings,      "api": "/organization/policies/settings",                                     "method": "GET"    },

    { "name": "GET POLICIES IN USER GROUP",    "func": get_policies_in_organization_group,    "api": "/organization/groups/group/<groupname>/policies",                     "method": "GET"    },
    { "name": "UPDATE POLICIES IN USER GROUP", "func": update_policies_in_organization_group, "api": "/organization/groups/group/<groupname>/policies",                     "method": "POST"   },
    { "name": "ADD POLICY TO USER GROUP",      "func": add_policy_to_organization_group,      "api": "/organization/groups/group/<groupname>/policies/policy/<policyname>", "method": "POST"   },
    { "name": "REMOVE POLICY FROM USER GROUP", "func": remove_policy_from_organization_group, "api": "/organization/groups/group/<groupname>/policies/policy/<policyname>", "method": "DELETE" },

]


########################################################################################################
#
# PAYMENT ACCOUNTING
#
########################################################################################################

@app.route('/account/subscription', methods=['GET'])
def get_subscription():
    return g_payment_accounting.get_subscription()

@app.route('/account/payment/paypalsetup', methods=['POST'])
def set_payment_paypal_setup():
    return g_payment_accounting.set_payment_paypal_setup()

@app.route('/account/payment/paypalpayerid/<paymentid>', methods=['POST'])
def store_payment_paypal_payerid(paymentid):
    return g_payment_accounting.store_payment_paypal_payerid(paymentid)

@app.route('/account/payment/paypalexecute/<paymentid>', methods=['POST'])
def set_payment_paypal_execute(paymentid):
    return g_payment_accounting.set_payment_paypal_execute(paymentid)

@app.route('/account/payment/paypal', methods=['GET'])
def get_payment_paypal_transactions():
    return g_payment_accounting.get_payment_paypal_transactions()

@app.route('/account/payment/paypal/<transactionid>', methods=['GET'])
def get_payment_paypal_transactions_detailed(transactionid):
    return g_payment_accounting.get_payment_paypal_transactions_detailed(transactionid)

g_payment_accounting_list = [
    { "name": "GET SUBSCRIPTION",           "func": get_subscription,                         "api": "/account/subscription",                      "method": "GET"    },
    { "name": "PAYPAL SETUP",               "func": set_payment_paypal_setup,                 "api": "/account/payment/paypalsetup",               "method": "POST"   },
    { "name": "PAYPAL STORE PAYERID",       "func": store_payment_paypal_payerid,             "api": "/account/payment/paypalpayerid/<paymentid>", "method": "POST"   },
    { "name": "PAYPAL EXECUTE",             "func": set_payment_paypal_execute,               "api": "/account/payment/paypalexecute/<paymentid>", "method": "POST"   },
    { "name": "GET PAYPAL TRANSACTIONS",    "func": get_payment_paypal_transactions,          "api": "/account/payment/paypal",                    "method": "GET"    },
    { "name": "GET PAYPAL TRANSACTIONS EX", "func": get_payment_paypal_transactions_detailed, "api": "/account/payment/paypal/<transactionid>",    "method": "GET"    },
]


########################################################################################################
#
# DEVICE GROUPS
#
########################################################################################################

@app.route('/devicegroups', methods=['GET'])
def get_device_group_list():
    return g_device_groups.get_device_group_list()

@app.route('/devicegroups/group/<devicegroupname>', methods=['POST'])
def register_devicegroups(devicegroupname):
    return g_device_groups.register_devicegroups(devicegroupname)

@app.route('/devicegroups/group/<devicegroupname>', methods=['DELETE'])
def unregister_devicegroups(devicegroupname):
    return g_device_groups.register_devicegroups(devicegroupname)

@app.route('/devicegroups/group/<devicegroupname>', methods=['GET'])
def get_devicegroups(devicegroupname):
    return g_device_groups.register_devicegroups(devicegroupname)


@app.route('/devicegroups/group/<devicegroupname>/name', methods=['POST'])
def update_devicegroupname(devicegroupname):
    return g_device_groups.update_devicegroupname(devicegroupname)

@app.route('/devicegroups/group/<devicegroupname>/device/<devicename>', methods=['POST'])
def register_device_to_devicegroups(devicegroupname, devicename):
    return g_device_groups.register_device_to_devicegroups(devicegroupname, devicename)

@app.route('/devicegroups/group/<devicegroupname>/device/<devicename>', methods=['DELETE'])
def unregister_device_to_devicegroups(devicegroupname, devicename):
    return g_device_groups.register_device_to_devicegroups(devicegroupname, devicename)

@app.route('/devicegroups/group/<devicegroupname>/devices', methods=['POST'])
def set_devices_to_devicegroups(devicegroupname):
    return g_device_groups.set_devices_to_devicegroups(devicegroupname)


@app.route('/devicegroups/group/<devicegroupname>/devices', methods=['GET'])
def get_devicegroup_detailed(devicegroupname):
    return g_device_groups.get_devicegroup_detailed(devicegroupname)

@app.route('/devicegroups/ungrouped', methods=['GET'])
def get_ungroupeddevices():
    return g_device_groups.get_ungroupeddevices()

@app.route('/devicegroups/mixed', methods=['GET'])
def get_mixeddevices():
    return g_device_groups.get_mixeddevices()


g_device_groups_list = [
    { "name": "GET DEVICE GROUPS",           "func": get_device_group_list,             "api": "/devicegroups",                                             "method": "GET"    },
    { "name": "ADD DEVICE GROUP",            "func": register_devicegroups,             "api": "/devicegroups/group/<devicegroupname>",                     "method": "POST"   },
    { "name": "DELETE DEVICE GROUP",         "func": register_devicegroups,             "api": "/devicegroups/group/<devicegroupname>",                     "method": "DELETE" },
    { "name": "GET DEVICE GROUP",            "func": register_devicegroups,             "api": "/devicegroups/group/<devicegroupname>",                     "method": "GET"    },
    { "name": "UPDATE DEVICE GROUP NAME",    "func": update_devicegroupname,            "api": "/devicegroups/group/<devicegroupname>/name",                "method": "POST"   },
    { "name": "ADD DEVICE TO GROUP",         "func": register_device_to_devicegroups,   "api": "/devicegroups/group/<devicegroupname>/device/<devicename>", "method": "POST"   },
    { "name": "DELETE DEVICE FROM GROUP",    "func": unregister_device_to_devicegroups, "api": "/devicegroups/group/<devicegroupname>/device/<devicename>", "method": "DELETE" },
    { "name": "SET DEVICES IN DEVICE GROUP", "func": set_devices_to_devicegroups,       "api": "/devicegroups/group/<devicegroupname>/devices",             "method": "POST"   },
    { "name": "GET DEVICE GROUP DETAILED",   "func": get_devicegroup_detailed,          "api": "/devicegroups/group/<devicegroupname>/devices",             "method": "GET"    },
    { "name": "GET UNGROUPED DEVICES",       "func": get_ungroupeddevices,              "api": "/devicegroups/ungrouped",                                   "method": "GET"    },
    { "name": "GET MIXED DEVICES",           "func": get_mixeddevices,                  "api": "/devicegroups/mixed",                                       "method": "GET"    },
]


########################################################################################################
#
# DEVICE LOCATIONS
#
########################################################################################################

@app.route('/devices/location', methods=['GET'])
def get_deviceslocations():
    return g_device_locations.get_deviceslocations()

@app.route('/devices/location', methods=['POST'])
def set_deviceslocation():
    return g_device_locations.set_deviceslocation()

@app.route('/devices/location', methods=['DELETE'])
def delete_deviceslocation():
    return g_device_locations.set_deviceslocation()

@app.route('/devices/device/<devicename>/location', methods=['GET'])
def get_devicelocation(devicename):
    return g_device_locations.get_devicelocation(devicename)

@app.route('/devices/device/<devicename>/location', methods=['POST'])
def set_devicelocation(devicename):
    return g_device_locations.set_devicelocation(devicename)

@app.route('/devices/device/<devicename>/location', methods=['DELETE'])
def delete_devicelocation(devicename):
    return g_device_locations.set_devicelocation(devicename)

g_device_locations_list = [
    { "name": "GET DEVICES LOCATIONS",    "func": get_deviceslocations,   "api": "/devices/location",                     "method": "GET"    },
    { "name": "SET DEVICES LOCATIONS",    "func": set_deviceslocation,    "api": "/devices/location",                     "method": "POST"   },
    { "name": "DELETE DEVICES LOCATIONS", "func": delete_deviceslocation, "api": "/devices/location",                     "method": "DELETE" },
    { "name": "GET DEVICE LOCATION",      "func": get_devicelocation,     "api": "/devices/device/<devicename>/location", "method": "POST"   },
    { "name": "SET DEVICE LOCATION",      "func": set_devicelocation,     "api": "/devices/device/<devicename>/location", "method": "GET"    },
    { "name": "DELETE DEVICE LOCATION",   "func": delete_devicelocation,  "api": "/devices/device/<devicename>/location", "method": "DELETE" },
]


########################################################################################################
#
# DEVICE OTA FIRMWARE UPDATE
#
########################################################################################################

@app.route('/devices/device/<devicename>/firmware', methods=['POST'])
def update_firmware(devicename):
    return g_device_otaupdates.update_firmware(devicename)

@app.route('/devices/firmware', methods=['POST'])
def update_firmwares():
    return g_device_otaupdates.update_firmwares()

@app.route('/devices/device/<devicename>/firmware', methods=['GET'])
def get_update_firmware(devicename):
    return g_device_otaupdates.get_update_firmware(devicename)

@app.route('/devices/ota', methods=['GET'])
def get_ota_statuses():
    return g_device_otaupdates.get_ota_statuses()

@app.route('/devices/device/<devicename>/ota', methods=['GET'])
def get_ota_status(devicename):
    return g_device_otaupdates.get_ota_status(devicename)

@app.route('/firmware/<device>/<filename>', methods=['GET'])
def download_firmware_file(device, filename):
    return g_device_otaupdates.download_firmware_file(device, filename)

g_device_otaupdates_list = [
    { "name": "UPDATE FIRMWARE",     "func": update_firmware,        "api": "/devices/location",                     "method": "POST"   },
    { "name": "UPDATE FIRMWARES",    "func": update_firmwares,       "api": "/devices/location",                     "method": "POST"   },
    { "name": "GET UPDATE FIRMWARE", "func": get_update_firmware,    "api": "/devices/location",                     "method": "GET"    },
    { "name": "GET OTA STATUSES",    "func": get_ota_statuses,       "api": "/devices/device/<devicename>/location", "method": "GET"    },
    { "name": "GET OTA STATUS",      "func": get_ota_status,         "api": "/devices/device/<devicename>/location", "method": "GET"    },
    { "name": "DOWNLOAD FIRMWARE",   "func": download_firmware_file, "api": "/firmware/<device>/<filename>",         "method": "GET"    },
]


########################################################################################################
#
# DEVICE HIERARCHIES
#
########################################################################################################

@app.route('/devices/device/<devicename>/hierarchy', methods=['GET'])
def get_device_hierarchy(devicename):
    return g_device_hierarchies.get_device_hierarchy(devicename)

@app.route('/devices/device/<devicename>/hierarchy', methods=['POST'])
def get_device_hierarchy_with_status(devicename):
    return g_device_hierarchies.get_device_hierarchy_with_status(devicename)

g_device_hierarchies_list = [
    { "name": "GET DEVICE HIERARCHY TREE",               "func": get_device_hierarchy,             "api": "/devices/device/<devicename>/hierarchy", "method": "GET"    },
    { "name": "GET DEVICE HIERARCHY TREE (WITH STATUS)", "func": get_device_hierarchy_with_status, "api": "/devices/device/<devicename>/hierarchy", "method": "POST"   },
]


########################################################################################################
#
# DEVICE HISTORIES
#
########################################################################################################

@app.route('/devices/histories', methods=['GET'])
def get_device_histories():
    return g_device_histories.get_device_histories()

@app.route('/devices/histories', methods=['POST'])
def get_device_histories_filtered():
    return g_device_histories.get_device_histories_filtered()

@app.route('/devices/menos', methods=['GET'])
def get_device_menos_histories():
    return g_device_histories.get_device_menos_histories()

@app.route('/devices/menos', methods=['POST'])
def get_device_menos_histories_filtered():
    return g_device_histories.get_device_menos_histories_filtered()

g_device_histories_list = [
    { "name": "GET HISTORIES",                "func": get_device_histories,                "api": "/devices/histories", "method": "GET"    },
    { "name": "GET HISTORIES FILTERED",       "func": get_device_histories_filtered,       "api": "/devices/histories", "method": "POST"   },
    { "name": "GET MENOS HISTORIES",          "func": get_device_menos_histories,          "api": "/devices/menos",     "method": "GET"    },
    { "name": "GET MENOS HISTORIES FILTERED", "func": get_device_menos_histories_filtered, "api": "/devices/menos",     "method": "POST"   },
]


########################################################################################################
#
# OTHERS
#
########################################################################################################

@app.route('/others/feedback', methods=['POST'])
def send_feedback():
    return g_other_stuffs.send_feedback()

@app.route('/others/<item>', methods=['GET'])
def get_item(item):
    return g_other_stuffs.get_item(item)

@app.route('/others/sensordevices', methods=['GET'])
def get_supported_sensors():
    return g_other_stuffs.get_supported_sensors()

@app.route('/others/firmwareupdates', methods=['GET'])
def get_device_firmware_updates():
    return g_other_stuffs.get_device_firmware_updates()

@app.route('/mobile/devicetoken', methods=['POST'])
def register_mobile_device_token():
    return g_other_stuffs.register_mobile_device_token()

g_other_stuffs_list = [
    { "name": "SEND FEEDBACK",         "func": send_feedback,                "api": "/others/feedback",        "method": "POST"   },
    { "name": "GET ITEM",              "func": get_item,                     "api": "/others/<item>",          "method": "GET"    },
    { "name": "GET SUPPORTED SENSORS", "func": get_supported_sensors,        "api": "/others/sensordevices",   "method": "GET"    },
    { "name": "GET FIRMWARE UPDATES",  "func": get_device_firmware_updates,  "api": "/others/firmwareupdates", "method": "GET"    },
    { "name": "REGISTER MOBILE TOKEN", "func": register_mobile_device_token, "api": "/mobile/devicetoken",     "method": "POST"   },
]



def sort_by_timestamp(elem):
    return elem['timestamp']

def sort_by_devicename(elem):
    return elem['devicename']

def sort_by_sensorname(elem):
    return elem['sensorname']



########################################################################################################
#
# DASHBOARD
#
########################################################################################################


########################################################################################################
#
# GET PERIPHERAL SENSOR READINGS
#
# - Request:
#   GET /devices/device/DEVICENAME/sensors/readings
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string, 'readings': {'value': int, 'lowest': int, 'highest': int}, 'enabled': int}, ...] }
#   { 'status': 'NG', 'message': string }
#
#
# DELETE PERIPHERAL SENSOR READINGS
#
# - Request:
#   DELETE /devices/device/DEVICENAME/sensors/readings
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
########################################################################################################
@app.route('/devices/device/<devicename>/sensors/readings', methods=['GET', 'DELETE'])
def get_all_device_sensors_enabled_input_readings(devicename):

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get All Device Sensors: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get All Device Sensors: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    #print('get_all_device_sensors_enabled_input {} devicename={}'.format(username, devicename))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get All Device Sensors: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get All Device Sensors: Token expired [{} {}] DATETIME {}\r\n'.format(username, devicename, datetime.datetime.now()))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get All Device Sensors: Token is invalid [{} {}]\r\n'.format(username, devicename))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username

    if flask.request.method == 'GET':
        if orgname is not None:
            # check authorization
            if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DASHBOARDS, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get All Device Sensors: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED

        # query device
        api = "get_devs"
        data = {}
        data['token'] = token
        data['devicename'] = devicename
        data['username'] = username
        response, status_return = g_messaging_requests.process(api, data)
        if status_return == 200:
            # query database
            sensors = g_database_client.get_all_device_sensors_input(entityname, devicename)

            # map queried result with database result
            #print("from device")
            response = json.loads(response)
            #print(response["value"])

            for sensor in sensors:
                #print(sensor)
                found = False
                peripheral = "{}{}".format(sensor['source'], sensor['number'])

                if sensor["source"] == "i2c":
                    if response["value"].get(peripheral):
                        for item in response["value"][peripheral]:
                            # match found for database result and actual device result
                            # set database record to configured and actual device item["enabled"]
                            if sensor["address"] == item["address"]:
                                g_database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], item["enabled"], 1)
                                found = True
                                break
                else:
                    if response["value"].get(peripheral):
                        for item in response["value"][peripheral]:
                            if item["class"] == g_utils.get_i2c_device_class(sensor["class"]):
                                g_database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], item["enabled"], 1)
                                found = True
                                break

                # no match found
                # set database record to unconfigured and disabled
                if found == False:
                    g_database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], 0, 0)
            #print()
        else:
            # cannot communicate with device so set database record to unconfigured and disabled
            g_database_client.disable_unconfigure_sensors(entityname, devicename)

        # query database
        sensors = g_database_client.get_all_device_sensors_enabled_input(entityname, devicename)
        for sensor in sensors:
            address = None
            if sensor.get("address"):
                address = sensor["address"]
            source = "{}{}".format(sensor["source"], sensor["number"])
            #sensor["devicename"] = devicename
            sensor.pop("deviceid")
            sensor_reading = g_database_client.get_sensor_reading(entityname, devicename, source, address)
            if sensor_reading is not None:
                sensor['readings'] = sensor_reading
        msg = {'status': 'OK', 'message': 'Get All Device Sensors queried successfully.', 'sensors': sensors}

    elif flask.request.method == 'DELETE':
        if orgname is not None:
            # check authorization
            if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DASHBOARDS, database_crudindex.DELETE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Delete All Device Sensors: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED

        #sensors = g_database_client.get_all_device_sensors_input(entityname, devicename)
        #for sensor in sensors:
        #    address = None
        #    if sensor.get("address"):
        #        address = sensor["address"]
        #    source = "{}{}".format(sensor["source"], sensor["number"])
        #    g_database_client.delete_sensor_reading(entityname, devicename, source, address)
        g_database_client.delete_device_sensor_reading(entityname, devicename)
        msg = {'status': 'OK', 'message': 'Delete All Device Sensors queried successfully.'}


    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    #print('\r\nGet All Device Sensors successful: {} {} {} sensors\r\n'.format(username, devicename, len(sensors)))
    return response


########################################################################################################
#
# GET PERIPHERAL SENSOR READINGS DATASET
#
# - Request:
#   GET /devices/device/DEVICENAME/sensors/readings/dataset
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string, 'readings': [{'timestamp': float, 'value': float, 'subclass': {'value': float}}], 'enabled': int}, ...] }
#   { 'status': 'NG', 'message': string }
#
########################################################################################################
@app.route('/devices/device/<devicename>/sensors/readings/dataset', methods=['GET'])
def get_all_device_sensors_enabled_input_readings_dataset(devicename):

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get All Device Sensors Dataset: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get All Device Sensors Dataset: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    #print('get_all_device_sensors_enabled_input_readings_dataset {} devicename={}'.format(username, devicename))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get All Device Sensors Dataset: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get All Device Sensors Dataset: Token expired [{} {}] DATETIME {}\r\n'.format(username, devicename, datetime.datetime.now()))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get All Device Sensors Dataset: Token is invalid [{} {}]\r\n'.format(username, devicename))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DASHBOARDS, database_crudindex.READ) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Get All Device Sensors Dataset: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username

    if flask.request.method == 'GET':
        # query device
        api = "get_devs"
        data = {}
        data['token'] = token
        data['devicename'] = devicename
        data['username'] = username
        response, status_return = g_messaging_requests.process(api, data)
        if status_return == 200:
            # query database
            sensors = g_database_client.get_all_device_sensors_input(entityname, devicename)

            # map queried result with database result
            #print("from device")
            response = json.loads(response)
            #print(response["value"])

            for sensor in sensors:
                #print(sensor)
                found = False
                peripheral = "{}{}".format(sensor['source'], sensor['number'])

                if sensor["source"] == "i2c":
                    if response["value"].get(peripheral):
                        for item in response["value"][peripheral]:
                            # match found for database result and actual device result
                            # set database record to configured and actual device item["enabled"]
                            if sensor["address"] == item["address"]:
                                g_database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], item["enabled"], 1)
                                found = True
                                break
                else:
                    if response["value"].get(peripheral):
                        for item in response["value"][peripheral]:
                            if item["class"] == g_utils.get_i2c_device_class(sensor["class"]):
                                g_database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], item["enabled"], 1)
                                found = True
                                break

                # no match found
                # set database record to unconfigured and disabled
                if found == False:
                    g_database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], 0, 0)
            #print()
        else:
            # cannot communicate with device so set database record to unconfigured and disabled
            g_database_client.disable_unconfigure_sensors(entityname, devicename)

        # query database
        sensors = g_database_client.get_all_device_sensors_enabled_input(entityname, devicename)
        for sensor in sensors:
            address = None
            if sensor.get("address"):
                address = sensor["address"]
            source = "{}{}".format(sensor["source"], sensor["number"])
            sensor.pop("deviceid")
            sensor_reading = g_database_client.get_sensor_reading_dataset(entityname, devicename, source, address)
            if sensor_reading is not None:
                sensor['dataset'] = sensor_reading
            readings = g_database_client.get_sensor_reading(entityname, sensor["devicename"], source, address)
            if readings is not None:
                sensor['readings'] = readings


    msg = {'status': 'OK', 'message': 'Get All Device Sensors Dataset queried successfully.', 'sensors': sensors}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    #print('\r\nGet All Device Sensors Dataset successful: {} {} {} sensors\r\n'.format(username, devicename, len(sensors)))
    return response


def get_running_sensors(token, username, devicename, device):

    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username


    # query device
    api = "get_devs"
    data = {}
    data['token'] = token
    data['devicename'] = devicename
    data['username'] = username
    response, status_return = g_messaging_requests.process(api, data)
    if status_return == 200:
        device['status'] = 1
        # query database
        sensors = g_database_client.get_all_device_sensors(entityname, devicename)

        # map queried result with database result
        #print("from device")
        response = json.loads(response)
        #print(response["value"])

        for sensor in sensors:
            #print(sensor)
            found = False
            peripheral = "{}{}".format(sensor['source'], sensor['number'])

            if sensor["source"] == "i2c":
                if response["value"].get(peripheral):
                    for item in response["value"][peripheral]:
                        # match found for database result and actual device result
                        # set database record to configured and actual device item["enabled"]
                        if sensor["address"] == item["address"]:
                            g_database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], item["enabled"], 1)
                            found = True
                            break
            else:
                if response["value"].get(peripheral):
                    for item in response["value"][peripheral]:
                        if item["class"] == g_utils.get_i2c_device_class(sensor["class"]):
                            g_database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], item["enabled"], 1)
                            found = True
                            break

            # no match found
            # set database record to unconfigured and disabled
            if found == False:
                g_database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], 0, 0)
        #print()
    else:
        device['status'] = 0
        # cannot communicate with device so set database record to unconfigured and disabled
        g_database_client.disable_unconfigure_sensors(entityname, devicename)
        #print('\r\nERROR Get All Device Sensors Dataset: Device is offline\r\n')
        return response, status_return
    return response, 200

def get_sensor_data_threaded(sensor, entityname, datebegin, dateend, period, maxpoints, readings, filter):
    address = None
    if sensor.get("address"):
        address = sensor["address"]
    source = "{}{}".format(sensor["source"], sensor["number"])
    sensor["devicename"] = filter["devicename"]
    dataset = g_database_client.get_sensor_reading_dataset_timebound(entityname, sensor["devicename"], source, address, datebegin, dateend, period, maxpoints)
    if dataset is not None:
        sensor['dataset'] = dataset
        #print(len(dataset["labels"]))

    #readings = g_database_client.get_sensor_reading(entityname, sensor["devicename"], source, address)
    #if readings is not None:
    #    sensor['readings'] = readings
    for reading in readings:
        if source == reading["source"]:
            if address is not None:
                if address == reading["address"]:
                    sensor['readings'] = reading['sensor_readings']
                    break
            else:
                sensor['readings'] = reading['sensor_readings']
                break

def get_sensor_data_threaded_ex(sensor, entityname, datebegin, dateend, period, maxpoints, readings, devices):
    address = None
    if sensor.get("address"):
        address = sensor["address"]
    source = "{}{}".format(sensor["source"], sensor["number"])
    for device in devices:
        if device["deviceid"] == sensor["deviceid"]:
            sensor["devicename"] = device["devicename"]
            break
    dataset = g_database_client.get_sensor_reading_dataset_timebound(entityname, sensor["devicename"], source, address, datebegin, dateend, period, maxpoints)
    if dataset is not None:
        sensor['dataset'] = dataset
        #print(len(dataset))

    #readings = g_database_client.get_sensor_reading(entityname, sensor["devicename"], source, address)
    #if readings is not None:
    #    sensor['readings'] = readings
    for reading in readings:
        if sensor["deviceid"] == reading["deviceid"]:
            if source == reading["source"]:
                if address is not None:
                    if address == reading["address"]:
                        sensor['readings'] = reading['sensor_readings']
                        break
                else:
                    sensor['readings'] = reading['sensor_readings']
                    break
    sensor.pop("deviceid")

def get_sensor_comparisons(devices, sensors_list):
    classes = []
    comparisons = []

    for sensor in sensors_list:
        label = sensor["sensorname"] + "." + sensor["devicename"]

        try:
            average_data = round(statistics.mean(sensor["dataset"]["data"][0]), 1)
        except:
            average_data = 0
        try:
            min_low = round(min(sensor["dataset"]["low"][0]), 1)
        except:
            min_low = 0
        try:
            max_high = round(max(sensor["dataset"]["high"][0]), 1)
        except:
            max_high = 0

        if average_data > 0:
            if sensor["class"] not in classes:
                classes.append(sensor["class"])
                item = {
                    'class': sensor["class"], 'labels': [], 'data': [[],[],[]]
                }
                item['data'][0].append(min_low)
                item['data'][1].append(average_data)
                item['data'][2].append(max_high)
                item['labels'].append(label)
                comparisons.append(item)
            else:
                for comparison in comparisons:
                    if comparison["class"] == sensor["class"]:
                        comparison['data'][0].append(min_low)
                        comparison['data'][1].append(average_data)
                        comparison['data'][2].append(max_high)
                        comparison['labels'].append(label)
                        break

        if sensor.get("subclass"):
            try:
                average_data = round(statistics.mean(sensor["dataset"]["data"][1]), 1)
            except:
                average_data = 0
            try:
                min_low = round(min(sensor["dataset"]["low"][1]), 1)
            except:
                min_low = 0
            try:
                max_high = round(max(sensor["dataset"]["high"][1]), 1)
            except:
                max_high = 0

            if average_data > 0:
                if sensor["subclass"] not in classes:
                    classes.append(sensor["subclass"])
                    item = {
                        'class': sensor["subclass"], 'labels': [], 'data': [[],[],[]]
                    }
                    item['data'][0].append(min_low)
                    item['data'][1].append(average_data)
                    item['data'][2].append(max_high)
                    item['labels'].append(label)
                    comparisons.append(item)
                else:
                    for comparison in comparisons:
                        if comparison["class"] == sensor["subclass"]:
                            comparison['data'][0].append(min_low)
                            comparison['data'][1].append(average_data)
                            comparison['data'][2].append(max_high)
                            comparison['labels'].append(label)
                            break
    for x in range(len(comparisons)-1, 0, -1):
        if len(comparisons[x]['labels']) == 1:
            comparisons.remove(comparisons[x])
    #    print(comparison)
    return comparisons

def get_device_stats(entityname, devices, sensordevicename):
    stats = {}

    if sensordevicename is not None: # All devices
        devices[0]["deviceid"] = g_database_client.get_deviceid(entityname, devices[0]["devicename"])

    devicegroups    = g_database_client.get_devicegroups(entityname)
    devicelocations = g_database_client.get_devices_location(entityname)
    stats['groups']    = { 'labels': ['no group'], 'data': [0] }
    stats['versions']  = { 'labels': ['unknown'], 'data': [0] }
    stats['locations'] = { 'labels': ['known', 'unknown'], 'data': [0, 0] }
    enabled_devices = 0

    for device in devices:
        # handle statuses
        if device["status"] == 1:
            enabled_devices += 1

        # handle groups
        found = 0
        #print(device["devicename"])
        for devicegroup in devicegroups:
            if len(devicegroup["devices"]):
                if device["deviceid"] in devicegroup["devices"]:
                    #print(devicegroup["groupname"])
                    found = 1
                    try:
                        index = stats['groups']['labels'].index(devicegroup["groupname"])
                        stats['groups']['data'][index] += 1
                    except:
                        stats['groups']['labels'].insert(0, devicegroup["groupname"])
                        stats['groups']['data'].insert(0, 1)
                    break
        if found == 0:
            #print(stats['groups']['labels'][0])
            stats['groups']['data'][-1] += 1

        # handle versions
        if device.get("version") is not None:
            try:
                index = stats['versions']['labels'].index("version " + device["version"])
                stats['versions']['data'][index] += 1
            except:
                stats['versions']['labels'].insert(0, "version " + device["version"])
                stats['versions']['data'].insert(0, 1)
        else:
            stats['versions']['data'][-1] += 1

        # handle locations
        found = 0
        for devicelocation in devicelocations:
            if device.get("deviceid"):
                if device["deviceid"] == devicelocation["deviceid"]:
                    stats['locations']['data'][0] += 1
                    found = 1
                    break
        if found == 0:
            stats['locations']['data'][1] += 1


    stats['statuses'] = { 
        'total': len(devices), 
        'online': enabled_devices, 
        'offline': len(devices)-enabled_devices, 
        'labels': ['online', 'offline'], 
        'data': [enabled_devices, len(devices)-enabled_devices] }

    return stats

def get_sensor_stats(sensors_list):
    stats = {}

    input_sensors = 0
    stats['types'] = { 'total': 0, 'input': 0, 'output': 0 }
    peripherals = []
    stats['peripherals'] = { 'total': 0, 'labels': [], 'data': [] }
    classes = []
    stats['classes'] = { 'total': 0, 'labels': [], 'data': [] }

    enabled_sensors = 0
    for sensor in sensors_list:
        if sensor["enabled"] == 1:
            enabled_sensors += 1

        if sensor["type"] == "input":
            input_sensors += 1

        if sensor["source"] not in peripherals:
            peripherals.append(sensor["source"])
            stats['peripherals']['total'] += 1
            stats['peripherals'][sensor["source"]] = 1
            stats['peripherals']['label'] = ''
        else:
            stats['peripherals'][sensor["source"]] += 1

        if sensor["class"] not in classes:
            classes.append(sensor["class"])
            stats['classes']['total'] += 1
            stats['classes'][sensor["class"]] = 1
            stats['classes']['label'] = ''
        else:
            stats['classes'][sensor["class"]] += 1

        if sensor.get("subclass"):
            if sensor["subclass"] not in classes:
                classes.append(sensor["subclass"])
                stats['classes']['total'] += 1
                stats['classes'][sensor["subclass"]] = 1
                stats['classes']['label'] = ''
            else:
                stats['classes'][sensor["subclass"]] += 1

    len_sensors = len(sensors_list)
    stats['types'] = { 
        'total': len_sensors, 
        'input': input_sensors, 
        'output': len_sensors-input_sensors, 
        'labels': ['input', 'output'], 
        'data': [input_sensors, len_sensors-input_sensors] }
    stats['statuses'] = { 
        'total': len_sensors, 
        'enabled': enabled_sensors, 
        'disabled': len_sensors-enabled_sensors, 
        'labels': ['enabled', 'disabled'], 
        'data': [enabled_sensors, len_sensors-enabled_sensors] }

    if len(peripherals):
        peripherals.sort()
    for peripheral in peripherals:
        stats['peripherals']['labels'].append(peripheral)
        stats['peripherals']['data'].append(stats['peripherals'][peripheral])
        stats['peripherals']['label'] += "{} {}, ".format(stats['peripherals'][peripheral], peripheral)
    if len(peripherals):
        stats['peripherals']['label'] = stats['peripherals']['label'][:len(stats['peripherals']['label'])-2]

    if len(classes):
        classes.sort()
    for classe in classes:
        stats['classes']['labels'].append(classe)
        stats['classes']['data'].append(stats['classes'][classe])
        stats['classes']['label'] += "{} {}, ".format(stats['classes'][classe], classe[:3])
    if len(classes):
        stats['classes']['label'] = stats['classes']['label'][:len(stats['classes']['label'])-2]

    return stats

def get_usage():
    curr_month = calendar.month_name[datetime.datetime.now().month]
    usages = {
#        'month': curr_month,
#        'alerts':  {'labels': ['sms', 'email', 'notification'], 'data': [75, 50, 25]},
#        'storage': {'labels': ['sensor data', 'alert data'], 'data': [50, 25]},
#        'login':   {'labels': ['email', 'sms'], 'data': [100, 100]}
        'alerts':  {'labels': [curr_month], 'data': [[75], [50], [25]]},
        'storage': {'labels': [""], 'data': [[50], [25]]},
        'login':   {'labels': [curr_month], 'data': [[100], [100]]}
    }
    return usages

########################################################################################################
#
# GET PERIPHERAL SENSOR READINGS DATASET (FILTERED)
#
# - Request:
#   POST /devices/sensors/readings/dataset
#   headers: { 'Authorization': 'Bearer ' + token.access }
#   data: {'devicename': string, 'peripheral': string, 'class': string, 'status': string, 'timerange': string, 'points': int, 'index': int, 'checkdevice': int}
#   // devicename can be "All devices" or the devicename of specific device
#   // peripheral can be ["All peripherals", "I2C1", "I2C2", "I2C3", "I2C4", "ADC1", "ADC2", "1WIRE1", "TPROBE1"]
#   // class can be ["All classes", "potentiometer", "temperature", "humidity", "anemometer", "battery", "fluid"]
#   // status can be ["All online/offline", "online", "offline"]
#   // timerange can be:
#        Last 5 minutes
#        Last 15 minutes
#        Last 30 minutes
#        Last 60 minutes
#        Last 3 hours
#        Last 6 hours
#        Last 12 hours
#        Last 24 hours
#        Last 3 days
#        Last 7 days
#        Last 2 weeks
#        Last 4 weeks
#        Last 3 months
#        Last 6 months
#        Last 12 months
#   // points can be 60, 30 or 15 points (for mobile, since screen is small, should use 30 or 15 instead of 60)
#   // index is 0 by default. 
#        To view the timeranges above, index is 0
#        To view the next timerange, ex. "Last Last 5 minutes", the previous instance, index is 1. and so on...
#   // checkdevice is 1 or 0. 1 if device status needs to be check if device is online and if sensor is active
#
# - Response:
#   { 'status': 'OK', 'message': string, 
#     'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string, 'readings': [{'timestamp': float, 'value': float, 'subclass': {'value': float}}], 'enabled': int}, ...] }
#   { 'status': 'NG', 'message': string }
#
#
# DELETE PERIPHERAL SENSOR READINGS DATASET (FILTERED)
#
# - Request:
#   POST /devices/sensors/readings/dataset
#   headers: { 'Authorization': 'Bearer ' + token.access }
#   data: {'devicename': string}
#   // devicename can be "All devices" or the devicename of specific device
#
# - Response:
#   { 'status': 'OK', 'message': string, 
#     'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string, 'readings': [{'timestamp': float, 'value': float, 'subclass': {'value': float}}], 'enabled': int}, ...] }
#   { 'status': 'NG', 'message': string }
#
########################################################################################################
@app.route('/devices/sensors/readings/dataset', methods=['POST', 'DELETE'])
def get_all_device_sensors_enabled_input_readings_dataset_filtered():

    #start_time = time.time()

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get All Device Sensors Dataset: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get All Device Sensors Dataset: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    #print('get_all_device_sensors_enabled_input_readings_dataset_filtered {}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get All Device Sensors Dataset: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get All Device Sensors Dataset: Token expired [{}] DATETIME {}\r\n'.format(username, datetime.datetime.now()))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get All Device Sensors Dataset: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username


    if flask.request.method == 'POST':
        if orgname is not None:
            # check authorization
            if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DASHBOARDS, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get All Device Sensors Dataset: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED

        # get filter parameters
        filter = flask.request.get_json()
        if filter.get("devicename") is None or filter.get("peripheral") is None or filter.get("class") is None or filter.get("status") is None or filter.get("timerange") is None or filter.get("points") is None or filter.get("index") is None:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get All Device Sensors Dataset: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        #print(filter["timerange"])
        timerange = [int(s) for s in filter["timerange"].split() if s.isdigit()][0]
        timeranges = ["minute", "hour", "day", "week", "month", "year"]
        multiplier = [60, 3600, 86400, 604800, 2592000, 31536000]
        for x in range(len(timeranges)):
            if timeranges[x] in filter["timerange"]:
                timerange *= multiplier[x]
                break

        devices = []
        if filter["devicename"] == "All devices":
            devices = g_database_client.get_devices(entityname)
        else:
            devices.append({"devicename": filter["devicename"]})

        # get active sensors for each device
        checkdevice = 1
        if filter.get("checkdevice") is not None:
            checkdevice = filter["checkdevice"]
        #print(checkdevice)
        if checkdevice != 0:
            thread_list = []
            for device in devices:
                devicename = device["devicename"]
                thr = threading.Thread(target = get_running_sensors, args = (token, username, devicename, device, ))
                thread_list.append(thr) 
                thr.start()
            for thr in thread_list:
                thr.join()

        # get all sensors based on specified filter
        sensors_list = []
        source = None
        number = None
        sensorclass = None
        sensorstatus = None
        sensordevicename = filter["devicename"]
        if sensordevicename == "All devices":
            sensordevicename = None
        if filter["peripheral"] != "All peripherals":
            source = filter["peripheral"][:len(filter["peripheral"])-1].lower()
            number = filter["peripheral"][len(filter["peripheral"])-1:]
        if filter["class"] != "All classes":
            sensorclass = filter["class"]
        if filter["status"] != "All online/offline":
            sensorstatus = 1 if filter["status"] == "online" else 0
        sensors_list = g_database_client.get_all_device_sensors_enabled_input(entityname, sensordevicename, source, number, sensorclass, sensorstatus)
        if len(sensors_list):
            sensors_list.sort(key=sort_by_sensorname)

        # get time bound
        maxpoints = filter["points"] # tested with 60 points
        if (maxpoints != 60 and maxpoints != 30 and maxpoints != 15):
            maxpoints = 60
        period = int(timerange/maxpoints)
        maxpoints += 1
        dateend = int(time.time())
        #print(dateend)
        if period == 5:
            dateend = int(dateend/period) * period + period
            # adjust based on specified index
            if filter["index"] != 0:
                dateend -= filter["index"] * timerange
            datebegin = dateend - timerange - period
        else:
            # adjust for adaptive begin and end "shift to left"
            dateend = int(dateend/period) * period# + period
            # adjust based on specified index
            if filter["index"] != 0:
                dateend -= filter["index"] * timerange
            #print(dateend)
            # add - period since we added 1 point
            datebegin = dateend - timerange - period 
        #print("datebegin={} dateend={} period={} maxpoints={}".format(datebegin, dateend, period, maxpoints))

        # add sensor properties to the result filtered sensors
        thread_list = []
        if filter["devicename"] != "All devices":
            readings = g_database_client.get_device_sensors_readings(entityname, filter["devicename"])
            for sensor in sensors_list:
                thr = threading.Thread(target = get_sensor_data_threaded, args = (sensor, entityname, datebegin, dateend, period, maxpoints, readings, filter, ))
                thread_list.append(thr) 
                thr.start()
        else:
            readings = g_database_client.get_user_sensors_readings(entityname)
            for sensor in sensors_list:
                thr = threading.Thread(target = get_sensor_data_threaded_ex, args = (sensor, entityname, datebegin, dateend, period, maxpoints, readings, devices, ))
                thread_list.append(thr) 
                thr.start()
        for thr in thread_list:
            thr.join()

        if len(sensors_list):
            sensors_list.sort(key=sort_by_devicename)


        # compute stats, summary and comparisons
        stats = None
        summary = None
        comparisons = None
        usages = None
        if checkdevice != 0:
            # stats
            output_sensors_list = g_database_client.get_all_device_sensors_enabled_input(entityname, sensordevicename, source, number, sensorclass, sensorstatus, type="output")
            stats = {"sensors": {}, "devices": {}}
            try:
                stats["sensors"] = get_sensor_stats(sensors_list+output_sensors_list)
            except:
                pass
            try:
                stats["devices"] = get_device_stats(entityname, devices, sensordevicename)
            except:
                pass

            # summary
            summary = {"sensors": [], "devices": []}
            try:
                summary["sensors"] = get_sensor_summary(entityname, devices, sensordevicename)
            except:
                pass
            try:
                summary["devices"] = get_device_summary(entityname, devices, sensordevicename)
            except:
                pass

            # comparisons
            try:
                comparisons = get_sensor_comparisons(devices, sensors_list)
            except:
                pass

            usages = get_usage()

        #print(time.time()-start_time)
        msg = {'status': 'OK', 'message': 'Get All Device Sensors Dataset queried successfully.', 'sensors': sensors_list}
        if stats:
            msg['stats'] = stats
        if summary:
            msg['summary'] = summary
        if comparisons:
            msg['comparisons'] = comparisons
        if usages:
            msg['usages'] = usages

    elif flask.request.method == 'DELETE':
        if orgname is not None:
            # check authorization
            if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DASHBOARDS, database_crudindex.DELETE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Delete All Device Sensors Dataset: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED

        filter = flask.request.get_json()
        if filter.get("devicename") is None:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get All Device Sensors Dataset: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        if filter["devicename"] == "All devices":
            g_database_client.delete_user_sensor_reading(entityname)
        else:
            g_database_client.delete_device_sensor_reading(entityname, filter["devicename"])

        msg = {'status': 'OK', 'message': 'Delete All Device Sensors Dataset queried successfully.'}


    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    #print('\r\nGet All Device Sensors Dataset successful: {} {} {} sensors\r\n'.format(username, devicename, len(sensors)))
    return response





def get_device_summary(entityname, devices, sensordevicename):
    devices_list = []

    devicegroups    = g_database_client.get_devicegroups(entityname)
    devicelocations = g_database_client.get_devices_location(entityname)

    if sensordevicename is not None: #"All devices":
        devices[0]["deviceid"] = g_database_client.get_deviceid(entityname, devices[0]["devicename"])

    for device in devices:
        version = "unknown"
        if device.get("version") is not None:
            version = device["version"]

        group = "no group"
        for devicegroup in devicegroups:
            if len(devicegroup["devices"]):
                if device["deviceid"] in devicegroup["devices"]:
                    group = devicegroup["groupname"]
                    break

        location = "unknown"
        for devicelocation in devicelocations:
            if device["deviceid"] == devicelocation["deviceid"]:
                location = json.dumps(devicelocation["location"])
                break

        devices_list.append({
            "devicename": device["devicename"],
            "version": version,
            "group": group,
            "location": location,
            "status": device["status"],
        })

    return devices_list


def get_sensor_summary(entityname, devices, sensordevicename):
    sensors_list = []
    if sensordevicename is not None: #"All devices":
        devices[0]["deviceid"] = g_database_client.get_deviceid(entityname, devices[0]["devicename"])
    for device in devices:
        # get all user input sensors
        sensors = g_database_client.get_all_device_sensors_by_deviceid(device["deviceid"])
        if len(sensors):
            #print(len(sensors))
            for sensor in sensors:
                address = None
                if sensor.get("address"):
                    address = sensor["address"]
                configuration = g_database_client.get_device_peripheral_configuration_by_deviceid(device["deviceid"], sensor["source"], int(sensor["number"]), address)
                if sensor["type"] == "input":
                    if configuration is not None:
                        mode = configuration["attributes"]["mode"]
                        # check if continuous mode (sensor forwarding) or thresholding mode (notification triggering)
                        if configuration.get("attributes"):
                            if mode == 2: #MODE_CONTINUOUS: 
                                value = configuration["attributes"]["hardware"]["devicename"]
                                value = "forward: " + value
                            else: 
                                threshold = configuration["attributes"]["threshold"]
                                if mode == 0: # MODE_THRESHOLD_SINGLE
                                    value = {"value": threshold["value"]}
                                elif mode == 1: # MODE_THRESHOLD_DUAL
                                    value = {"min": threshold["min"], "max": threshold["max"]}
                                value = "threshold: " + json.dumps(value)
                            classes = sensor["class"]
                        # handle subclass
                        if configuration["attributes"].get("subattributes"):
                            if mode == 2: #MODE_CONTINUOUS: 
                                subvalue = configuration["attributes"]["subattributes"]["hardware"]["devicename"]
                                subvalue = "forward: " + value
                            else: 
                                threshold = configuration["attributes"]["subattributes"]["threshold"]
                                if mode == 0: # MODE_THRESHOLD_SINGLE
                                    subvalue = {"value": threshold["value"]}
                                elif mode == 1: # MODE_THRESHOLD_DUAL
                                    subvalue = {"min": threshold["min"], "max": threshold["max"]}
                                subvalue = "threshold: " + json.dumps(subvalue)
                            value += ", " + subvalue
                            classes += ", " + sensor["subclass"]
                    else:
                        value = "Unconfigured"
                        classes = sensor["class"]
                        if sensor.get("subclass"):
                            classes += ", " + sensor["subclass"]
                elif sensor["type"] == "output":
                    if configuration is not None:
                        if sensor["class"] == "light":
                            usage = configuration["attributes"]["color"]["usage"]
                            if usage == 0:
                                endpoint = configuration["attributes"]["color"]["single"]["endpoint"]
                                if endpoint == 0:
                                    value = "source: manual"
                                else:
                                    hardware = configuration["attributes"]["color"]["single"]["hardware"]
                                    value = "source: " + hardware["devicename"] + "." + hardware["peripheral"] + "." + hardware["sensorname"]
                            else:
                                individual = configuration["attributes"]["color"]["individual"]
                                value = {"red": "", "blue": "", "green": ""}
                                # red
                                if individual["red"]["endpoint"] == 0:
                                    value["red"] = "manual"
                                else:
                                    hardware = individual["red"]["hardware"]
                                    value["red"] = hardware["devicename"] + "." + hardware["peripheral"] + "." + hardware["sensorname"]
                                # blue
                                if individual["blue"]["endpoint"] == 0:
                                    value["blue"] = "manual"
                                else:
                                    hardware = individual["blue"]["hardware"]
                                    value["blue"] = hardware["devicename"] + "." + hardware["peripheral"] + "." + hardware["sensorname"]
                                # green
                                if individual["green"]["endpoint"] == 0:
                                    value["green"] = "manual"
                                else:
                                    hardware = individual["green"]["hardware"]
                                    value["green"] = hardware["devicename"] + "." + hardware["peripheral"] + "." + hardware["sensorname"]
                                value = "source: " + json.dumps(value)
                        else:
                            try:
                                endpoint = configuration["attributes"]["endpoint"]
                            except:
                                print("XXXXXXX" + str(json.dumps(configuration)))
                                endpoint = 0
                            if endpoint == 0:
                                value = "source: manual"
                            else:
                                hardware = configuration["attributes"]["hardware"]
                                value = "source: " + hardware["devicename"] + "." + hardware["peripheral"] + "." + hardware["sensorname"]
                    else:
                        value = "Unconfigured"
                    classes = sensor["class"]
                    if sensor.get("subclass"):
                        classes += ", " + sensor["subclass"]
                #print("{}, {}, {}, {}, {}, {}".format(sensor["sensorname"], device["devicename"], classes, value, sensor["enabled"], sensor["source"]))
                sensors_list.append({
                    "sensorname": sensor["sensorname"], 
                    "devicename": device["devicename"], 
                    "type": sensor["type"], 
                    "peripheral": sensor["source"], 
                    "classes": classes, 
                    "configuration": value, 
                    "enabled": sensor["enabled"]})
    return sensors_list


########################################################################################################
#
# GET PERIPHERAL SENSOR CONFIGURATION SUMMARY
#
# - Request:
#   GET /devices/sensors/configurationsummary
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'summary': [{'sensorname': string, 'devicename': string, 'classes': string, 'configuration': string, 'enabled': int}] }
#   { 'status': 'NG', 'message': string }
#
########################################################################################################
@app.route('/devices/sensors/configurationsummary', methods=['GET'])
def get_all_sensor_configurationsummary():

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get All Sensor Thresholds: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get All Sensor Thresholds: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    #print('get_all_sensor_configurationsummary {}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get All Sensor Thresholds: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get All Sensor Thresholds: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get All Sensor Thresholds: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DASHBOARDS, database_crudindex.READ) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Get All Sensor Thresholds: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username

    summary = get_sensor_summary(entityname)


    msg = {'status': 'OK', 'message': 'All Sensor Thresholds queried successfully.', 'summary': summary}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\nAll Sensor Thresholds queried successful: {}\r\n'.format(username))
    return response


########################################################################################################
#
# GET I2C DEVICES READINGS (per peripheral slot)
#
# - Request:
#   GET /devices/device/<devicename>/i2c/NUMBER/sensors/readings
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'sensor_readings': {'value': int, 'lowest': int, 'highest': int} }
#   {'status': 'NG', 'message': string }
#
# GET ADC DEVICES READINGS (per peripheral slot)
# GET 1WIRE DEVICES READINGS (per peripheral slot)
# GET TPROBE DEVICES READINGS (per peripheral slot)
#
# - Request:
#   GET /devices/device/<devicename>/adc/NUMBER/sensors/readings
#   GET /devices/device/<devicename>/1wire/NUMBER/sensors/readings
#   GET /devices/device/<devicename>/tprobe/NUMBER/sensors/readings
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'sensor_readings': {'value': int, 'lowest': int, 'highest': int} }
#   {'status': 'NG', 'message': string }
#
#
# DELETE I2C DEVICES READINGS (per peripheral slot)
#
# - Request:
#   DELETE /devices/device/<devicename>/i2c/NUMBER/sensors/readings
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string }
#   {'status': 'NG', 'message': string }
#
# DELETE ADC DEVICES READINGS (per peripheral slot)
# DELETE 1WIRE DEVICES READINGS (per peripheral slot)
# DELETE TPROBE DEVICES READINGS (per peripheral slot)
#
# - Request:
#   DELETE /devices/device/<devicename>/adc/NUMBER/sensors/readings
#   DELETE /devices/device/<devicename>/1wire/NUMBER/sensors/readings
#   DELETE /devices/device/<devicename>/tprobe/NUMBER/sensors/readings
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string }
#   {'status': 'NG', 'message': string }
#
########################################################################################################
@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/readings', methods=['GET', 'DELETE'])
def get_xxx_sensors_readings(devicename, xxx, number):

    # check number parameter
    if int(number) > 4 or int(number) < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get {} Sensor: Invalid authorization header\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensor: Token expired\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_{}_sensor_readings {} devicename={} number={}'.format(xxx, username, devicename, number))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(devicename) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get {} Sensor: Empty parameter found\r\n'.format(xxx))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensor: Token expired [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get {} Sensor: Token is invalid [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username


    source = "{}{}".format(xxx, number)
    if flask.request.method == 'GET':
        if orgname is not None:
            # check authorization
            if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DASHBOARDS, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get Peripheral Sensor Readings: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED

        if True:
            # get enabled input sensors
            sensors = g_database_client.get_sensors_enabled_input(entityname, devicename, xxx, number)

            # get sensor reading for each enabled input sensors
            for sensor in sensors:
                address = None
                if sensor.get("address"):
                    address = sensor["address"]
                sensor_reading = g_database_client.get_sensor_reading(entityname, devicename, source, address)
                sensor['readings'] = sensor_reading

            msg = {'status': 'OK', 'message': 'Sensors readings queried successfully.', 'sensor_readings': sensors}
            if new_token:
                msg['new_token'] = new_token
            response = json.dumps(msg)
            print('\r\nSensors readings queried successful: {}\r\n{}\r\n'.format(entityname, response))
            return response
        else:
            # get sensors readings
            sensor_readings = g_database_client.get_sensors_readings(entityname, devicename, source)

            msg = {'status': 'OK', 'message': 'Sensors readings queried successfully.', 'sensor_readings': sensor_readings}
            if new_token:
                msg['new_token'] = new_token
            response = json.dumps(msg)
            print('\r\nSensors readings queried successful: {}\r\n{}\r\n'.format(entityname, response))
            return response

    elif flask.request.method == 'DELETE':
        if orgname is not None:
            # check authorization
            if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DASHBOARDS, database_crudindex.DELETE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get Peripheral Sensor Readings: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED

        # delete sensors readings
        g_database_client.delete_sensors_readings(entityname, devicename, source)

        msg = {'status': 'OK', 'message': 'Sensors readings deleted successfully.'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nSensors readings deleted successful: {}\r\n{}\r\n'.format(entityname, response))
        return response


########################################################################################################
#
# GET I2C DEVICES READINGS DATASET (per peripheral slot)
#
# - Request:
#   GET /devices/device/<devicename>/i2c/NUMBER/sensors/sensor/SENSORNAME/readings/dataset
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'sensor_readings': [{'timestamp': int, 'value': int}] }
#   {'status': 'NG', 'message': string }
#
# GET ADC DEVICES READINGS DATASET (per peripheral slot)
# GET 1WIRE DEVICES READINGS DATASET (per peripheral slot)
# GET TPROBE DEVICES READINGS DATASET (per peripheral slot)
#
# - Request:
#   GET /devices/device/<devicename>/adc/NUMBER/sensors/sensor/SENSORNAME/readings/dataset
#   GET /devices/device/<devicename>/1wire/NUMBER/sensors/sensor/SENSORNAME/readings/dataset
#   GET /devices/device/<devicename>/tprobe/NUMBER/sensors/sensor/SENSORNAME/readings/dataset
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'sensor_readings': [{'timestamp': int, 'value': int}] }
#   {'status': 'NG', 'message': string }
#
########################################################################################################
@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>/readings/dataset', methods=['GET'])
def get_xxx_sensors_readings_dataset(devicename, xxx, number, sensorname):

    print('get_{}_sensor_readings_dataset'.format(xxx))

    # check number parameter
    if int(number) > 4 or int(number) < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get {} Sensor: Invalid authorization header\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensor: Token expired\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_{}_sensor_readings_dataset {} devicename={} number={}'.format(xxx, username, devicename, number))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(devicename) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get {} Sensor: Empty parameter found\r\n'.format(xxx))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensor: Token expired [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get {} Sensor: Token is invalid [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username


    # get sensor
    sensor = g_database_client.get_sensor(entityname, devicename, xxx, number, sensorname)

    source = "{}{}".format(xxx, number)
    address = None
    if sensor.get("address"):
        address = sensor["address"]
    sensor_reading = g_database_client.get_sensor_reading_dataset(entityname, devicename, source, address)
    sensor['readings'] = sensor_reading

    msg = {'status': 'OK', 'message': 'Sensors readings dataset queried successfully.', 'sensor_readings': sensor}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\nSensors readings dataset queried successful: {}\r\n{}\r\n'.format(username, response))
    return response


###########################





########################################################################################################
#
# DEVICES
#
########################################################################################################



########################################################################################################
# 
# GET LDS BUS
#
# - Request:
#   GET /devices/device/DEVICENAME/ldsbus/PORTNUMBER
#   headers: {'Authorization': 'Bearer ' + token.access}
#   // PORT_NUMBER can be 1, 2, 3, or 0 (0 if all lds bus)
#
# - Response:
#   {'status': 'OK', 'message': string, 'ldsbus': obj }
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/device/<devicename>/ldsbus/<portnumber>', methods=['GET'])
def get_lds_bus(devicename, portnumber):
    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get LDSBUS: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get LDSBUS: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    #print('get_lds_bus {}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get LDSBUS: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get LDSBUS: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get LDSBUS: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Get LDSBUS: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username


    ldsbus = []
    #[
    #{
    #    "port": int(portnumber),
    #    "ldsus": [
    #        {
    #            'name'             : 'LDSU01',
    #            'uuid'             : 'LDSUUUID',
    #            'serialnumber'     : 'asdasdasd',
    #            'manufacturingdate': 'erwrwer',
    #            'productversion'   : '0.0.1',
    #            'productname'      : 'ldsuname 01'
    #        },
    #        {
    #            'name'             : 'LDSU02',
    #            'uuid'             : 'LDSUUUID02',
    #            'serialnumber'     : 'asdasdasd',
    #            'manufacturingdate': 'erwrwer',
    #            'productversion'   : '0.0.2',
    #            'productname'      : 'ldsuname 02'
    #        }
    #    ], 
    #    "sensors": [
    #        {
    #            "name"    : "Sensor01", 
    #            "class"   : "temperature", 
    #            "ldsuname": "LDSU01", 
    #            "ldsuuuid": "LDSUUUID01", 
    #            "ldsuport": int(portnumber)
    #        },
    #        {
    #            "name"    : "Sensor02", 
    #            "class"   : "potentiometer", 
    #            "ldsuname": "LDSU02", 
    #            "ldsuuuid": "LDSUUUID02", 
    #            "ldsuport": int(portnumber)
    #        }
    #    ], 
    #    "actuators": [
    #        {
    #            "name"    : "Actuator01", 
    #            "class"   : "display", 
    #            "ldsuname": "LDSU01", 
    #            "ldsuuuid": "LDSUUUID01", 
    #            "ldsuport": int(portnumber)
    #        },
    #        {
    #            "name"    : "Actuator02", 
    #            "class"   : "led", 
    #            "ldsuname": "LDSU02", 
    #            "ldsuuuid": "LDSUUUID02", 
    #            "ldsuport": int(portnumber)
    #        }
    #    ]
    #}
    #]


    msg = {'status': 'OK', 'message': 'LDSBUS queried successfully.'}
    if ldsbus:
        msg['ldsbus'] = ldsbus
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    return response


########################################################################################################
# 
# SCAN LDS BUS
#
# - Request:
#   POST /devices/device/DEVICENAME/ldsbus/PORTNUMBER
#   headers: {'Authorization': 'Bearer ' + token.access}
#   // PORT_NUMBER can be 1, 2, 3, or 0 (0 if all lds bus)
#
# - Response:
#   {'status': 'OK', 'message': string, 'ldsbus': obj }
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/device/<devicename>/ldsbus/<portnumber>', methods=['POST'])
def scan_lds_bus(devicename, portnumber):
    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get LDSBUS: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get LDSBUS: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    #print('scan_lds_bus {}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get LDSBUS: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get LDSBUS: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get LDSBUS: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Get LDSBUS: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username


    # get username from token
    data = {}
    data['token'] = token
    data['devicename'] = devicename
    data['username'] = username
    data['port'] = int(portnumber)
    api = 'req_ldsus'
    response, status_return = g_messaging_requests.process(api, data)
    if status_return != 200:
        ldsbus = None
    else:
        response = json.loads(response)
        ldsbus = response["value"]


    msg = {'status': 'OK', 'message': 'LDSBUS queried successfully.'}
    if ldsbus:
        msg['ldsbus'] = ldsbus
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    return response


########################################################################################################
# 
# CHANGE LDSU NAME
#
# - Request:
#   GET /devices/device/DEVICENAME/ldsu/LDSUUUID/name
#   headers: {'Authorization': 'Bearer ' + token.access}
#   data: {'name': string}
#   // PORT_NUMBER can be 1, 2, 3, or 0 (0 if all lds bus)
#
# - Response:
#   {'status': 'OK', 'message': string, 'ldsbus': obj }
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/device/<devicename>/ldsu/<ldsuuuid>/name', methods=['POST'])
def change_ldsu_name(devicename, ldsuuuid):
    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Change LDSU name: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Change LDSU name: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    #print('change_ldsu_name {}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Change LDSU name: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Change LDSU name: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Change LDSU name: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Change LDSU name: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username


    msg = {'status': 'OK', 'message': 'LDSU name changed successfully.'}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    return response


########################################################################################################
# 
# IDENTIFY LDSU
#
# - Request:
#   GET /devices/device/DEVICENAME/ldsu/LDSUUUID/identify
#   headers: {'Authorization': 'Bearer ' + token.access}
#   data: {'name': string}
#
# - Response:
#   {'status': 'OK', 'message': string, 'ldsbus': obj }
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/device/<devicename>/ldsu/<ldsuuuid>/identify', methods=['POST'])
def identify_ldsu(devicename, ldsuuuid):
    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Identify LDSU: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Identify LDSU: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    #print('identify_ldsu {}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Identify LDSU: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Identify LDSU: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Identify LDSU: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Identify LDSU: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username


    # get username from token
    data = {}
    data['token'] = token
    data['devicename'] = devicename
    data['username'] = username
    data['uuid'] = ldsuuuid
    api = 'ide_ldsu'
    response, status_return = g_messaging_requests.process(api, data)
    if status_return != 200:
        return response, status_return


    msg = {'status': 'OK', 'message': 'LDSU identified successfully.'}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    return response




########################################################################################################
# 
# GET DEVICES
#
# - Request:
#   GET /devices
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'devices': array[{'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': string, 'heartbeat': string, 'version': string, location: {'latitude': float, 'longitude': float}}, ...]}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices', methods=['GET'])
def get_device_list():
    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get Devices: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get Devices: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    #print('get_device_list {}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get Devices: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get Devices: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get Devices: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Get Devices: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username


    devices = g_database_client.get_devices(entityname)


    msg = {'status': 'OK', 'message': 'Devices queried successfully.', 'devices': devices}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('get_device_list {} {} devices'.format(username, len(devices)))
    return response

########################################################################################################
# 
# GET DEVICES FILTERED
#
# - Request:
#   GET /devices/filter/FILTERSTRING
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'devices': array[{'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': string, 'heartbeat': string, 'version': string, location: {'latitude': float, 'longitude': float}}, ...]}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/filter/<filter>', methods=['GET'])
def get_device_list_filtered(filter):
    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get Devices: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get Devices: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_device_list_filtered {}'.format(username))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(filter) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get Devices: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get Devices: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get Devices: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Get Devices: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username


    devices = g_database_client.get_devices_with_filter(entityname, filter)

    # get the location from database
    #for device in devices:
    #    location  = g_database_client.get_device_location(username, device["devicename"])
    #    if location:
    #        device["location"] = location


    msg = {'status': 'OK', 'message': 'Devices queried successfully.', 'devices': devices}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\nGet Devices successful: {}\r\n{} devices\r\n'.format(username, len(devices)))
    return response

def decode_password(secret_key, password):

    return jwt.decode(password, secret_key, algorithms=['HS256'])

def compute_password(secret_key, uuid, serial_number, mac_address, debug=False):

    if secret_key=='' or uuid=='' or serial_number=='' or mac_address=='':
        printf("secret key, uuid, serial number and mac address should not be empty!")
        return None

    current_time = int(time.time())
    params = {
        "uuid": uuid,                  # device uuid
        "serialnumber": serial_number, # device serial number
        "poemacaddress": mac_address,  # device mac address in uppercase string ex. AA:BB:CC:DD:EE:FF
    }
    password = jwt.encode(params, secret_key, algorithm='HS256')

    # pyjwt returns bytes while jose returns string
    # if bytes is returned, then convert to string
    if type(password) == bytes:
        password = password.decode("utf-8")

    if debug:
        print("")
        print("compute_password")
        g_utils.print_json(params)
        print(password)
        print("")

        payload = decode_password(secret_key, password)
        print("")
        print("decode_password")
        g_utils.print_json(payload)
        print("")

    return password


def device_cleanup(entityname, deviceid):

    # delete device sensor-related information
    sensors = g_database_client.get_all_device_sensors_by_deviceid(deviceid)
    if sensors is not None:
        for sensor in sensors:
            if sensor.get("source") and sensor.get("number") and sensor.get("sensorname"):
                sensor_cleanup(None, None, deviceid, sensor["source"], sensor["number"], sensor["sensorname"], sensor)

    # delete device-related information
    g_database_client.delete_device_history_by_deviceid(deviceid)
    g_database_client.delete_ota_status_by_deviceid(deviceid)
    g_database_client.delete_device_notification_by_deviceid(deviceid)
    g_database_client.delete_device_location_by_deviceid(deviceid)
    g_database_client.remove_device_from_devicegroups(entityname, deviceid)
    g_database_client.delete_menos_transaction_by_deviceid(deviceid)

    # delete device from database
    g_database_client.delete_device_by_deviceid(deviceid)

    # delete device from message broker
    try:
        message_broker_api().unregister(deviceid)
    except:
        pass


########################################################################################################
#
# ADD DEVICE
#
# - Request:
#   POST /devices/device/<devicename>
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: {'deviceid': string, 'serialnumber': string, 'poemacaddress': string}
#   // poemacaddress is a mac address in uppercase string ex. AA:BB:CC:DD:EE:FF
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
#
# DELETE DEVICE
#
# - Request:
#   DELETE /devices/device/<devicename>
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/device/<devicename>', methods=['POST', 'DELETE'])
def register_device(devicename):
    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Add/Delete Device: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Add/Delete Device: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('register_device {} devicename={}'.format(username, devicename))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(devicename) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Add/Delete Device: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Add/Delete Device: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Add/Delete Device: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username


    if flask.request.method == 'POST':
        if orgname is not None:
            # check authorization
            if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.CREATE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Add Device: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED

        # check parameters
        data = flask.request.get_json()
        #print(data)
        if not data.get("deviceid") or not data.get("serialnumber") or not data.get("poemacaddress"):
            response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
            print('\r\nERROR Add Device: Parameters not included [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_400_BAD_REQUEST
        #print(data["deviceid"])
        #print(data["serialnumber"])

        # check if device is registered
        # a user cannot register the same device name
        if g_database_client.find_device(entityname, devicename):
            response = json.dumps({'status': 'NG', 'message': 'Device name is already taken'})
            print('\r\nERROR Add Device: Device name is already taken [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_409_CONFLICT

        # check if UUID is unique
        # a user cannot register a device if it is already registered by another user
        if g_database_client.find_device_by_id(data["deviceid"]):
            response = json.dumps({'status': 'NG', 'message': 'Device UUID is already registered'})
            print('\r\nERROR Add Device: Device uuid is already registered[{}]\r\n'.format(data["deviceid"]))
            return response, status.HTTP_409_CONFLICT

        # TODO: check if serial number matches UUID

        # check if poe mac address is unique
        if g_database_client.find_device_by_poemacaddress(data["poemacaddress"]):
            response = json.dumps({'status': 'NG', 'message': 'Device POE MAC Address is already registered'})
            print('\r\nERROR Add Device: Device POE MAC Address is already registered[{}]\r\n'.format(data["deviceid"]))
            return response, status.HTTP_409_CONFLICT

        # add device to database
        result = g_database_client.add_device(entityname, devicename, data["deviceid"], data["serialnumber"], data['poemacaddress'])
        #print(result)
        if not result:
            response = json.dumps({'status': 'NG', 'message': 'Device could not be registered'})
            print('\r\nERROR Add Device: Device could not be registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_400_BAD_REQUEST

        # add and configure message broker user
        try:
            # Password is now a combination of UUID, Serial Number and POE Mac Address
            # Previously, PASSWORD is just the DEVICE_SERIAL
            #devicepass = data["serialnumber"]
            deviceuser = data["deviceid"]
            devicepass = compute_password(config.CONFIG_JWT_SECRET_KEY_DEVICE, data["deviceid"], data["serialnumber"], data['poemacaddress'], debug=False)
            #print(devicepass)

            # if secure is True, device will only be able to publish and subscribe to server/<deviceid>/# and <deviceid>/# respectively
            # this means a hacker can only hack that particular device and will not be able to eavesdrop on other devices
            # if secure is False, device will be able to publish and subscribe to/from other devices which enables multi-subscriptions
            secure = True
            result = message_broker_api().register(deviceuser, devicepass, secure)
            #print(result)
            if not result:
                response = json.dumps({'status': 'NG', 'message': 'Device could not be registered in message broker'})
                print('\r\nERROR Add Device: Device could not be registered  in message broker [{},{}]\r\n'.format(entityname, devicename))
                return response, status.HTTP_500_INTERNAL_SERVER_ERROR
        except Exception as e:
            print("Exception encountered {}".format(e))
            response = json.dumps({'status': 'NG', 'message': 'Device could not be registered in message broker'})
            print('\r\nERROR Add Device: Device could not be registered in message broker [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR

        # add default uart notification recipients
        # this is necessary so that an entry exist for consumption of notification manager
        source = "uart"
        notification = g_database_client.get_device_notification(entityname, devicename, source)
        if notification is None:
            notification = build_default_notifications(source, token)
            if notification is not None:
                g_database_client.update_device_notification(entityname, devicename, source, notification)

        msg = {'status': 'OK', 'message': 'Devices registered successfully.'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nDevice registered successful: {}\r\n{}\r\n'.format(username, response))
        return response

    elif flask.request.method == 'DELETE':
        if orgname is not None:
            # check authorization
            if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.DELETE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Delete Device: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED

        # check if device is registered
        device = g_database_client.find_device(entityname, devicename)
        if not device:
            response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
            print('\r\nERROR Delete Device: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND


        # cleanup device
        device_cleanup(entityname, device['deviceid'])


        msg = {'status': 'OK', 'message': 'Devices unregistered successfully.'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nDevice unregistered successful: {}\r\n{}\r\n'.format(username, response))
        return response


########################################################################################################
#
# GET DEVICE
#
# - Request:
#   GET /devices/device/<devicename>
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'device': {'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': string, 'heartbeat': string, 'version': string, location: {'latitude': float, 'longitude': float} }}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/device/<devicename>', methods=['GET'])
def get_device(devicename):
    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get Device: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get Device: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_device {} devicename={}'.format(username, devicename))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(devicename) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get Device: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get Device: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get Device: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Get Device: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username


    # check if device is registered
    device = g_database_client.find_device(entityname, devicename)
    if not device:
        response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
        print('\r\nERROR Get Device: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
        return response, status.HTTP_404_NOT_FOUND


    msg = {'status': 'OK', 'message': 'Devices queried successfully.', 'device': device}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\nDevice queried successful: {}\r\n{}\r\n'.format(username, response))
    return response


########################################################################################################
#
# UPDATE DEVICE NAME
#
# - Request:
#   POST /devices/device/<devicename>/name
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: {'new_devicename': string}
#
# - Response:
#   {'status': 'OK', 'message': string}}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/device/<devicename>/name', methods=['POST'])
def update_devicename(devicename):
    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Update Device Name: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Update Device Name: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_device {} devicename={}'.format(username, devicename))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(devicename) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Update Device Name: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Update Device Name: Token expired [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Update Device Name: Token is invalid [{}]\r\n'.format(username))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Get Device: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED

        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username

    # check if device is registered
    device = g_database_client.find_device(entityname, devicename)
    if not device:
        response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
        print('\r\nERROR Update Device Name: Device is not registered [{},{}]\r\n'.format(entityname, devicename))
        return response, status.HTTP_404_NOT_FOUND


    # check if new device name is already registered
    data = flask.request.get_json()
    if not data.get("new_devicename"):
        response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
        print('\r\nERROR Update Device Name: Parameters not included [{},{}]\r\n'.format(entityname, devicename))
        return response, status.HTTP_400_BAD_REQUEST
    if len(data["new_devicename"]) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Update Device Name: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST
    device = g_database_client.find_device(entityname, data["new_devicename"])
    if device:
        response = json.dumps({'status': 'NG', 'message': 'Device name is already registered'})
        print('\r\nERROR Update Device Name: Device name is already registered [{},{}]\r\n'.format(entityname, devicename))
        return response, status.HTTP_400_BAD_REQUEST


    # update the device name
    g_database_client.update_devicename(entityname, devicename, data["new_devicename"])


    msg = {'status': 'OK', 'message': 'Device name updated successfully.', 'device': device}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\nDevice name updated successful: {}\r\n{}\r\n'.format(username, response))
    return response


#########################





#########################


########################################################################################################
# GET  /devices/device/<devicename>/xxx
# POST /devices/device/<devicename>/xxx
########################################################################################################
#
# GET STATUS
# - Request:
#   GET /devices/device/<devicename>/status
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': { 'status': int, 'version': string } }
#   { 'status': 'NG', 'message': string, 'value': { 'heartbeat': string, 'version': string} }
#
@app.route('/devices/device/<devicename>/status', methods=['GET'])
def get_status(devicename):
    api = 'get_status'

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = {}
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username
    #print('get_status {} devicename={}'.format(data['username'], data['devicename']))


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Get Status: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username

    response, status_return = g_messaging_requests.process(api, data)
    if status_return == 503: # HTTP_503_SERVICE_UNAVAILABLE
        # if device is unreachable, get the cached heartbeat and version
        cached_value = g_database_client.get_device_cached_values(entityname, devicename)
        if not cached_value:
            response = json.dumps({'status': 'NG', 'message': 'Device is not registered'})
            print('\r\nERROR Device is not registered [{},{}]\r\n'.format(username, devicename))
            return response, status.HTTP_404_NOT_FOUND
        response = json.loads(response)
        response['value'] = cached_value
        response = json.dumps(response)
        return response, status_return

    if status_return == 200:
        response = json.loads(response)
        version = response["value"]["version"]
        response = json.dumps(response)
        g_database_client.save_device_version(entityname, devicename, version)

    return response

def get_status_threaded(entityname, api, data, device):
    response, status_return = g_messaging_requests.process(api, data)
    if status_return == 503: # HTTP_503_SERVICE_UNAVAILABLE
        # if device is unreachable, get the cached heartbeat and version
        cached_value = g_database_client.get_device_cached_values(entityname, device["devicename"])
        if cached_value:
            if cached_value.get("heartbeat"):
                device["heartbeat"] = cached_value["heartbeat"]
            if cached_value.get("version"):
                device["version"] = cached_value["version"]

    if status_return == 200:
        response = json.loads(response)
        version = response["value"]["version"]
        status = response["value"]["status"]
        response = json.dumps(response)
        g_database_client.save_device_version(entityname, device["devicename"], version)
        device["version"] = version
        device["status"] = status

#
# GET STATUSES
# - Request:
#   GET /devices/status
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': [{ "devicename": string, 'status': int, 'version': string }] }
#   { 'status': 'NG', 'message': string, 'value': [{ "devicename": string, 'heartbeat': string, 'version': string}] }
#
@app.route('/devices/status', methods=['GET'])
def get_statuses():
    api = 'get_status'

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    token = {'access': auth_header_token}
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    #print('get_status {} devicename={}'.format(data['username'], data['devicename']))


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Get Statuses: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username


    thread_list = []
    devices = g_database_client.get_devicenames(entityname)
    for device in devices:
        data = {}
        data['token'] = token
        data['devicename'] = device["devicename"]
        data['username'] = entityname
        thr = threading.Thread(target = get_status_threaded, args = (entityname, api, data, device, ))
        thread_list.append(thr) 
        thr.start()
    for thr in thread_list:
        thr.join()
    #print(devices)

    msg = {'status': 'OK', 'message': 'Device statuses queried successfully.', 'devices': devices}
    response = json.dumps(msg)
    return response

#
# SET STATUS
# - Request:
#   POST /devices/device/<devicename>/status
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'status': int }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': {'status': string} }
#   { 'status': 'NG', 'message': string}
#
@app.route('/devices/device/<devicename>/status', methods=['POST'])
def set_status(devicename):
    api = 'set_status'

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get parameter input
    data = flask.request.get_json()

    # check parameter input
    if data['status'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Set status: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get username from token
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    data['username'] = g_database_client.get_username_from_token(data['token'])
    if data['username'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('set_status {} devicename={}'.format(data['username'], data['devicename']))

    return g_messaging_requests.process(api, data)

#
# GET SETTINGS
# - Request:
#   GET /devices/device/<devicename>/settings
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/settings', methods=['GET'])
def get_settings(devicename):
    api = 'get_settings'

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = {}
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username
    print('get_settings {} devicename={}'.format(data['username'], data['devicename']))

    return g_messaging_requests.process(api, data)

#
# SET SETTINGS
# - Request:
#   POST /devices/device/<devicename>/settings
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: { 'status': int }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': { 'sensorrate': int } }
#   { 'status': 'NG', 'message': string}
#
@app.route('/devices/device/<devicename>/settings', methods=['POST'])
def set_settings(devicename):
    api = 'set_settings'

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get parameter input
    data = flask.request.get_json()

    # get username from token
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    data['username'] = g_database_client.get_username_from_token(data['token'])
    if data['username'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('set_settings {} devicename={}'.format(data['username'], data['devicename']))

    return g_messaging_requests.process(api, data)



#########################

def build_default_notifications(type, token):
    notifications = {}

    if type == "uart":
        notifications["messages"] = [
            {
                "message": "Hello World", 
                "enable": True
            }
        ]
    elif type == "gpio":
        notifications["messages"] = [
            {
                "message": "Hello World", 
                "enable": True
            }, 
            {
                "message": "Hi World", 
                "enable": True
            }
        ]
    else:
        notifications["messages"] = [
            {
                "message": "Sensor threshold activated", 
                "enable": True
            }, 
            {
                "message": "Sensor threshold deactivated", 
                "enable": True
            }
        ]

    notifications["endpoints"] = {
        "mobile": {
            "recipients": "",
            "recipients_list" : [],
            "enable": False
        },
        "email": {
            "recipients": "",
            "recipients_list" : [],
            "enable": False
        },
        "notification": {
            "recipients": "",
            "recipients_list" : [],
            "enable": False
        },
        "modem": {
            "recipients": "",
            "recipients_list" : [],
            "enable": False
        },
        "storage": {
            "recipients": "",
            "recipients_list" : [],
            "enable": False
        },
    }

    info = g_database_client.get_user_info(token['access'])
    if info is None:
        return None

    if info.get("email"):
        notifications["endpoints"]["email"]["recipients"] = info["email"]
        notifications["endpoints"]["email"]["recipients_list"].append({ "to": info["email"], "group": False })

    if info.get("email_verified"):
        notifications["endpoints"]["email"]["enable"] = info["email_verified"]

    if info.get("phone_number"):
        notifications["endpoints"]["mobile"]["recipients"] = info["phone_number"]
        notifications["endpoints"]["mobile"]["recipients_list"].append({ "to": info["phone_number"], "group": False })
        #notifications["endpoints"]["notification"]["recipients"] = info["phone_number"]
        #notifications["endpoints"]["notification"]["recipients_list"].append({ "to": info["phone_number"], "group": False })

    if type == "uart":
        if info.get("phone_number_verified"):
            notifications["endpoints"]["mobile"]["enable"] = info["phone_number_verified"]
            #notifications["endpoints"]["notification"]["enable"] = False

    return notifications


#
# GET UARTS
#
# - Request:
#   GET /devices/device/<devicename>/uarts
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 
#     'value': { 
#       'uarts': [
#         {'enabled': int}, 
#       ]
#     }
#   }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/uarts', methods=['GET'])
def get_uarts(devicename):
    api = 'get_uarts'

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    data = {}
    data['token'] = token
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username
    print('get_uarts {} devicename={}'.format(data['username'], data['devicename']))

    return g_messaging_requests.process(api, data)


#
# GET UART PROPERTIES
#
# - Request:
#   GET /devices/device/<devicename>/uart/properties
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': { 'baudrate': int, 'parity': int, 'flowcontrol': int, 'stopbits': int, 'databits': int } }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/uart/properties', methods=['GET'])
def get_uart_prop(devicename):
    api = 'get_uart_prop'

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    data = {}
    data['token'] = token
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username
    print('get_uart_prop {} devicename={}'.format(data['username'], data['devicename']))

    response, status_return = g_messaging_requests.process(api, data)
    if status_return != 200:
        return response, status_return


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username

    source = "uart"
    notification = g_database_client.get_device_notification(entityname, devicename, source)
    if notification is not None:
        if notification["endpoints"]["modem"].get("recipients_id"):
            notification["endpoints"]["modem"].pop("recipients_id")
        #print(notification)
        # notification recipients should be empty
        if notification["endpoints"]["notification"].get("recipients"):
            notification["endpoints"]["notification"]["recipients"] = ""
        response = json.loads(response)
        response['value']['notification'] = notification
        response = json.dumps(response)
    else:
        response = json.loads(response)
        response['value']['notification'] = build_default_notifications("uart", token)
        response = json.dumps(response)

    return response


#
# SET UART PROPERTIES
#
# - Request:
#   POST /devices/device/<devicename>/uart/properties
#   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
#   data: { 'baudrate': int, 'parity': int, 'flowcontrol': int, 'stopbits': int, 'databits': int }
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/uart/properties', methods=['POST'])
def set_uart_prop(devicename):
    api = 'set_uart_prop'

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = flask.request.get_json()
    #print(data)
    if data['baudrate'] is None or data['parity'] is None or data['databits'] is None or data['stopbits'] is None or data['flowcontrol'] is None or data['notification'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST
    #print(data['baudrate'])
    #print(data['parity'])
    #print(data['notification'])

    # get notifications and remove from list
    notification = data['notification']
    #print(notification)
    data.pop('notification')
    #print(notification)
    #print(data)

    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username
    print('set_uart_prop {} devicename={}'.format(data['username'], data['devicename']))

    response, status_return = g_messaging_requests.process(api, data)
    if status_return != 200:
        return response, status_return


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Set Uart: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username

    source = "uart"
    item = g_database_client.update_device_notification(entityname, devicename, source, notification)

    # update device configuration database for device bootup
    #print("data={}".format(data))
    item = g_database_client.update_device_peripheral_configuration(entityname, devicename, "uart", 1, None, None, None, data)

    return response


#
# ENABLE/DISABLE UART
#
# - Request:
#   POST /devices/device/DEVICENAME/uart/enable
#   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
#   data: { 'enable': int }
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/uart/enable', methods=['POST'])
def enable_uart(devicename):
    api = 'enable_uart'

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = flask.request.get_json()

    # check parameter input
    if data['enable'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username
    print('enable_uart {} devicename={}'.format(data['username'], data['devicename']))

    return g_messaging_requests.process(api, data)


#
# GET GPIOS
#
# - Request:
#   GET /devices/device/<devicename>/gpios
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 
#     'value': { 
#       'voltage': int,
#       'gpios': [
#         {'direction': int, 'status': int}, 
#         {'direction': int, 'status': int}, 
#         {'direction': int, 'status': int}, 
#         {'direction': int, 'status': int}
#       ]
#     }
#   }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/gpios', methods=['GET'])
def get_gpios(devicename):
    api = 'get_gpios'

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    data = {}
    data['token'] = token
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username
    print('get_gpios {} devicename={}'.format(data['username'], data['devicename']))

    return g_messaging_requests.process(api, data)


#
# GET GPIO PROPERTIES
#
# - Request:
#   GET /devices/device/<devicename>/gpio/<number>/properties
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': { 'direction': int, 'mode': int, 'alert': int, 'alertperiod': int } }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/gpio/<number>/properties', methods=['GET'])
def get_gpio_prop(devicename, number):
    api = 'get_gpio_prop'

    # check number parameter
    number = int(number)
    if number > 4 or number < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    data = {}
    data['token'] = token
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username
    data['number'] = number
    print('get_gpio_prop {} devicename={}'.format(data['username'], data['devicename']))

    response, status_return = g_messaging_requests.process(api, data)
    if status_return != 200:
        return response, status_return


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Get Gpio Props: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username

    source = "gpio{}".format(number)
    notification = g_database_client.get_device_notification(entityname, devicename, source)
    if notification is not None:
        response = json.loads(response)
        response['value']['notification'] = notification
        response = json.dumps(response)
    else:
        response = json.loads(response)
        response['value']['notification'] = build_default_notifications("gpio", token)
        response = json.dumps(response)

    return response


#
# SET GPIO PROPERTIES
#
# - Request:
#   POST /devices/device/<devicename>/gpio/<number>/properties
#   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
#   data: { 'direction': int, 'mode': int, 'alert': int, 'alertperiod': int }
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/gpio/<number>/properties', methods=['POST'])
def set_gpio_prop(devicename, number):
    api = 'set_gpio_prop'

    # check number parameter
    number = int(number)
    if number > 4 or number < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = flask.request.get_json()
    #print(data)
    if data['direction'] is None or data['mode'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST
    if data['direction'] == 0: # INPUT
        if data['alert'] is None or data['alertperiod'] is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
            print('\r\nERROR Invalid parameters\r\n')
            return response, status.HTTP_400_BAD_REQUEST
        if data['alertperiod'] < 5000:
            response = json.dumps({'status': 'NG', 'message': 'Invalid parameters: alert period should be >= 5000 milliseconds'})
            print('\r\nERROR Invalid parameters\r\n')
            return response, status.HTTP_400_BAD_REQUEST
    elif data['direction'] == 1: # OUTPUT
        # If OUTPUT, polarity must be present
        if data['polarity'] is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
            print('\r\nERROR Invalid parameters\r\n')
            return response, status.HTTP_400_BAD_REQUEST
        # If MODE is PULSE, width must be present
        # If MODE is CLOCK, mark and space must be present
        if data['mode'] == 1: # PULSE
            if data['width'] is None:
                response = json.dumps({'status': 'NG', 'message': 'Invalid parameters: width should be present'})
                print('\r\nERROR Invalid parameters\r\n')
                return response, status.HTTP_400_BAD_REQUEST
            if data['width'] == 0:
                response = json.dumps({'status': 'NG', 'message': 'Invalid parameters: width should be > 0 when mode is 1'})
                print('\r\nERROR Invalid parameters\r\n')
                return response, status.HTTP_400_BAD_REQUEST
        elif data['mode'] == 2: # CLOCK
            if data['mark'] is None or data['space'] is None or data['count'] is None:
                response = json.dumps({'status': 'NG', 'message': 'Invalid parameters: mark, space, count should be present'})
                print('\r\nERROR Invalid parameters\r\n')
                return response, status.HTTP_400_BAD_REQUEST
            if data['mark'] == 0 or data['space'] == 0 or data['count'] == 0:
                response = json.dumps({'status': 'NG', 'message': 'Invalid parameters: mark, space, count should be > 0 when mode is 2'})
                print('\r\nERROR Invalid parameters\r\n')
                return response, status.HTTP_400_BAD_REQUEST
    #print(data['direction'])
    #print(data['mode'])
    #print(data['alert'])
    #print(data['alertperiod'])
    #print(data['polarity'])
    #print(data['width'])
    #print(data['mark'])
    #print(data['space'])


    # get notifications and remove from list
    notification = data['notification']
    data.pop('notification')
    #print(data)
    #print(notification)

    #print(api)
    #print(data)
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username

    # note: python dict maintains insertion order so number will always be the last key
    data['number'] = number
    print('set_gpio_prop {} devicename={}'.format(data['username'], data['devicename']))

    response, status_return = g_messaging_requests.process(api, data)
    if status_return != 200:
        return response, status_return


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Set Gpio Props: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username

    source = "gpio{}".format(number)
    g_database_client.update_device_notification(entityname, devicename, source, notification)

    # update device configuration database for device bootup
    #print("data={}".format(data))
    data.pop('number')
    item = g_database_client.update_device_peripheral_configuration(entityname, devicename, "gpio", int(number), None, None, None, data)

    return response



#
# GET GPIO VOLTAGE
#
# - Request:
#   GET /devices/device/<devicename>/gpio/voltage
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': { 'voltage': int } }
#   { 'status': 'NG', 'message': string }
#   voltage is an index of the value in the list of voltages
#     ["3.3 V", "5 V"]
#
# GET ADC VOLTAGE
#
# - Request:
#   GET /devices/device/<devicename>/adc/voltage
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'value': { 'voltage': int } }
#   { 'status': 'NG', 'message': string }
#   voltage is an index of the value in the list of voltages
#     ["-5/+5V Range", "-10/+10V Range", "0/10V Range"]
#
@app.route('/devices/device/<devicename>/<xxx>/voltage', methods=['GET'])
def get_xxx_voltage(devicename, xxx):
    api = 'get_{}_voltage'.format(xxx)

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = {}
    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    data['username'] = g_database_client.get_username_from_token(data['token'])
    if data['username'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_{}_voltage {} devicename={}'.format(xxx, data['username'], data['devicename']))

    return g_messaging_requests.process(api, data)

#
# SET GPIO VOLTAGE
#
# - Request:
#   POST /devices/device/<devicename>/gpio/voltage
#   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
#   data: { 'voltage': int }
#   voltage is an index of the value in the list of voltages
#     ["3.3 V", "5 V"]
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
# SET ADC VOLTAGE
#
# - Request:
#   POST /devices/device/<devicename>/adc/voltage
#   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
#   data: { 'voltage': int }
#   voltage is an index of the value in the list of voltages
#     ["-5/+5V Range", "-10/+10V Range", "0/10V Range"]
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/<xxx>/voltage', methods=['POST'])
def set_xxx_voltage(devicename, xxx):
    api = 'set_{}_voltage'.format(xxx)

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get parameter inputs
    data = flask.request.get_json()

    # check parameter input
    if data['voltage'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST
    if data['voltage'] > 2:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    data['username'] = g_database_client.get_username_from_token(data['token'])
    if data['username'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('set_{}_voltage {} devicename={}'.format(xxx, data['username'], data['devicename']))

    return g_messaging_requests.process(api, data)


#
# ENABLE/DISABLE GPIO
#
# - Request:
#   POST /devices/device/DEVICENAME/gpio/NUMBER/enable
#   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
#   data: { 'enable': int }
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/gpio/<number>/enable', methods=['POST'])
def enable_gpio(devicename, number):
    api = 'enable_gpio'

    # check number parameter
    number = int(number)
    if number > 4 or number < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get parameter inputs
    data = flask.request.get_json()

    # check parameter input
    if data['enable'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username

    # note: python dict maintains insertion order so number will always be the last key
    data['number'] = number
    print('enable_gpio {} devicename={} number={}'.format(username, devicename, number))

    return g_messaging_requests.process(api, data)


#
# GET I2CS
#
# - Request:
#   GET /devices/device/<devicename>/i2cs
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 
#     'value': { 
#       'i2cs': [
#         {'enabled': int}, 
#         {'enabled': int}, 
#         {'enabled': int}, 
#         {'enabled': int}, 
#       ]
#     }
#   }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/i2cs', methods=['GET'])
def get_i2cs(devicename):
    api = 'get_i2cs'

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    data = {}
    data['token'] = token
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username
    print('get_i2cs {} devicename={}'.format(data['username'], data['devicename']))

    return g_messaging_requests.process(api, data)


########################################################################################################
#
# GET ALL I2C DEVICES
#
# - Request:
#   GET /devices/device/DEVICENAME/i2c/sensors
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string}, ...] }
#   { 'status': 'NG', 'message': string }
#
#
# GET ALL ADC DEVICES
# GET ALL 1WIRE DEVICES
# GET ALL TPROBE DEVICES
#
# - Request:
#   GET /devices/device/DEVICENAME/adc/sensors
#   GET /devices/device/DEVICENAME/1wire/sensors
#   GET /devices/device/DEVICENAME/tprobe/sensors
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'manufacturer': string, 'model': string, 'timestamp': string}, ...] }
#   { 'status': 'NG', 'message': string }
#
########################################################################################################
@app.route('/devices/device/<devicename>/<xxx>/sensors', methods=['GET'])
def get_all_xxx_sensors(devicename, xxx):

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get All {} Sensors: Invalid authorization header\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get All {} Sensors: Token expired\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_all_i2c_sensors {} devicename={}'.format(username, devicename))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get All {} Sensors: Empty parameter found\r\n'.format(xxx))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get All {} Sensors: Token expired [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get All {} Sensors: Token is invalid [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Get All Sensors: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username

    sensors = g_database_client.get_all_sensors(entityname, devicename, xxx)


    msg = {'status': 'OK', 'message': 'All Sensors queried successfully.', 'sensors': sensors}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\nGet All {} Sensors successful: {}\r\n{} sensors\r\n'.format(xxx, username, len(sensors)))
    return response


########################################################################################################
#
# GET ALL I2C INPUT/OUTPUT DEVICES
#
# - Request:
#   GET /devices/device/DEVICENAME/i2c/sensors/DEVICETYPE
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string}, ...] }
#   { 'status': 'NG', 'message': string }
#
########################################################################################################
@app.route('/devices/device/<devicename>/i2c/sensors/<devicetype>', methods=['GET'])
def get_all_i2c_type_sensors(devicename, devicetype):

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get All {} Sensors: Invalid authorization header\r\n'.format("i2c"))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get All {} Sensors: Token expired\r\n'.format("i2c"))
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_all_i2c_sensors {} devicename={}'.format(username, devicename))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get All {} Sensors: Empty parameter found\r\n'.format("i2c"))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get All {} Sensors: Token expired [{}]\r\n'.format("i2c", username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get All {} Sensors: Token is invalid [{}]\r\n'.format("i2c", username))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Get All Sensors: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username

    sensors = g_database_client.get_all_type_sensors(entityname, devicename, "i2c", devicetype)


    msg = {'status': 'OK', 'message': 'All Sensors queried successfully.', 'sensors': sensors}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\nGet All {} Sensors successful: {}\r\n{} sensors\r\n'.format("i2c", username, len(sensors)))
    return response


########################################################################################################
#
# GET I2C DEVICES
#
# - Request:
#   GET /devices/device/DEVICENAME/i2c/NUMBER/sensors
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string, 'enabled': int}, ...] }
#   { 'status': 'NG', 'message': string }
#
#
# GET ADC DEVICES
# GET 1WIRE DEVICES
# GET TPROBE DEVICES
#
# - Request:
#   GET /devices/device/DEVICENAME/adc/NUMBER/sensors
#   GET /devices/device/DEVICENAME/1wire/NUMBER/sensors
#   GET /devices/device/DEVICENAME/tprobe/NUMBER/sensors
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'manufacturer': string, 'model': string, 'timestamp': string, 'enabled': int}, ...] }
#   { 'status': 'NG', 'message': string }
#
########################################################################################################
@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors', methods=['GET'])
def get_xxx_sensors(devicename, xxx, number):

    # check number parameter
    if int(number) > 4 or int(number) < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get {} Sensors: Invalid authorization header\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensors: Token expired\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_{}_sensors {} devicename={} number={}'.format(xxx, username, devicename, number))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get {} Sensors: Empty parameter found\r\n'.format(xxx))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensors: Token expired [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get {} Sensors: Token is invalid [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Get Peripheral Sensors: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username


    # query peripheral sensors
    sensors = g_database_client.get_sensors(entityname, devicename, xxx, number)

    # set to query device
    api = "get_{}_devs".format(xxx)
    data = {}
    data['token'] = token
    data['devicename'] = devicename
    data['username'] = username
    data["number"] = int(number)

    # query device
    response, status_return = g_messaging_requests.process(api, data)

    if status_return == 200:
        # map queried result with database result
        #print("from device")
        response = json.loads(response)
        #print(response["value"])
        if xxx == "i2c":
            # if I2C
            #print("I2C")
            for sensor in sensors:
                found = False
                for item in response["value"]:
                    # match found for database result and actual device result
                    # set database record to configured and actual device item["enabled"]
                    if sensor["address"] == item["address"]:
                        # device is configured
                        g_database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], item["enabled"], 1)
                        sensor["enabled"] = item["enabled"]
                        sensor["configured"] = 1
                        found = True
                        break
                # no match found
                # set database record to unconfigured and disabled
                if found == False:
                    g_database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], 0, 0)
                    sensor["enabled"] = 0
                    sensor["configured"] = 0
        else:
            # if ADC/1WIRE/TPROBE
            #print("ADC/1WIRE/TPROBE")
            for sensor in sensors:
                found = False
                # check if this is the active sensor
                # if not the active sensor, then set database record to unconfigured and disabled
                #print(sensor)
#                if sensor['configured']:
                for item in response["value"]:
                    if item["class"] == g_utils.get_i2c_device_class(sensor["class"]):
                        g_database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], item["enabled"], 1)
                        sensor["enabled"] = item["enabled"]
                        sensor["configured"] = 1
                        found = True
                        break
                if found == False:
                    # set database record to unconfigured and disabled
                    g_database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], 0, 0)
                    sensor["enabled"] = 0
                    sensor["configured"] = 0
#                else:
#                    # set database record to unconfigured and disabled
#                    g_database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], 0, 0)
#                    sensor["enabled"] = 0
#                    sensor["configured"] = 0
        #print()
    else:
        # cannot communicate with device so set database record to unconfigured and disabled
        g_database_client.disable_unconfigure_sensors(entityname, devicename)
        for sensor in sensors:
            sensor["enabled"] = 0
            sensor["configured"] = 0

    # get sensor readings for enabled input devices
    for sensor in sensors:
        if sensor['type'] == 'input' and sensor['enabled']:
            address = None
            if sensor.get("address"):
                address = sensor["address"]
            source = "{}{}".format(xxx, number)
            sensor_reading = g_database_client.get_sensor_reading(entityname, devicename, source, address)
            if sensor_reading is not None:
                sensor['readings'] = sensor_reading

    if status_return == 200:
        msg = {'status': 'OK', 'message': 'Sensors queried successfully.', 'sensors': sensors}
    else:
        msg = {'status': 'OK', 'message': 'Sensors queried successfully but device is offline.', 'sensors': sensors}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\nGet {} Sensors successful: {}\r\n{} sensors\r\n'.format(xxx, username, len(sensors)))
    return response


#
# when deleting a sensor,
# make sure the sensor configurations, sensor readings and sensor registration are also deleted
#
def sensor_cleanup(entityname, devicename, deviceid, xxx, number, sensorname, sensor):

    print("\r\ndelete_sensor {}".format(sensorname))
    address = None
    if sensor.get("address"):
        address = sensor["address"]

    print("")

    # delete sensor notifications
    print("Deleting sensor notifications...")
    source = "{}{}{}".format(xxx, number, sensorname)
    #notification = g_database_client.get_device_notification(entityname, devicename, source)
    #print(notification)
    if deviceid:
        g_database_client.delete_device_notification_sensor_by_deviceid(deviceid, source)
    else:
        g_database_client.delete_device_notification_sensor(entityname, devicename, source)
    #notification = g_database_client.get_device_notification(entityname, devicename, source)
    #print(notification)
    #print("")

    # delete sensor configurations
    print("Deleting sensor configurations...")
    #config = g_database_client.get_device_peripheral_configuration(entityname, devicename, xxx, int(number), address)
    #print(config)
    if deviceid:
        g_database_client.delete_device_peripheral_configuration_by_deviceid(deviceid, xxx, int(number), address)
    else:
        g_database_client.delete_device_peripheral_configuration(entityname, devicename, xxx, int(number), address)
    #config = g_database_client.get_device_peripheral_configuration(entityname, devicename, xxx, int(number), address)
    #print(config)
    #print("")

    # delete sensor readings
    print("Deleting sensor readings...")
    source = "{}{}".format(xxx, number)
    #readings = g_database_client.get_sensor_reading(entityname, devicename, source, address)
    #print(readings)
    #readings_dataset = g_database_client.get_sensor_reading_dataset(entityname, devicename, source, address)
    #print(readings_dataset)
    if deviceid:
        g_database_client.delete_sensor_reading_by_deviceid(deviceid, source, address)
    else:
        g_database_client.delete_sensor_reading(entityname, devicename, source, address)
    #readings = g_database_client.get_sensor_reading(entityname, devicename, source, address)
    #print(readings)
    #readings_dataset = g_database_client.get_sensor_reading_dataset(entityname, devicename, source, address)
    #print(readings_dataset)
    #print("")

    # delete sensor from database
    print("Deleting sensor registration...")
    if deviceid:
        g_database_client.delete_sensor_by_deviceid(deviceid, xxx, number, sensorname)
    else:
        g_database_client.delete_sensor(entityname, devicename, xxx, number, sensorname)
    #result = g_database_client.get_sensor(entityname, devicename, xxx, number, sensorname)
    #print(result)
    #print("")


########################################################################################################
#
# ADD I2C DEVICE
#
# - Request:
#   POST /devices/device/<devicename>/i2c/NUMBER/sensors/sensor/<sensorname>
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: {'address': int, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'attributes': []}
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
# ADD ADC DEVICE
# ADD 1WIRE DEVICE
# ADD TPROBE DEVICE
#
# - Request:
#   POST /devices/device/<devicename>/adc/NUMBER/sensors/sensor/<sensorname>
#   POST /devices/device/<devicename>/1wire/NUMBER/sensors/sensor/<sensorname>
#   POST /devices/device/<devicename>/tprobe/NUMBER/sensors/sensor/<sensorname>
#   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
#   data: {'manufacturer': string, 'model': string, 'class': string, 'type': string, 'attributes': []}
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
#
# DELETE I2C DEVICE
#
# - Request:
#   DELETE /devices/device/<devicename>/i2c/NUMBER/sensors/sensor/<sensorname>
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
# DELETE ADC DEVICE
# DELETE 1WIRE DEVICE
# DELETE TPROBE DEVICE
#
# - Request:
#   DELETE /devices/device/<devicename>/adc/NUMBER/sensors/sensor/<sensorname>
#   DELETE /devices/device/<devicename>/1wire/NUMBER/sensors/sensor/<sensorname>
#   DELETE /devices/device/<devicename>/tprobe/NUMBER/sensors/sensor/<sensorname>
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>', methods=['POST', 'DELETE'])
def register_xxx_sensor(devicename, xxx, number, sensorname):

    # check number parameter
    if int(number) > 4 or int(number) < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Add/Delete {} Sensor: Invalid authorization header\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Add/Delete {} Sensor: Token expired\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    print('register_{}_sensor {} devicename={} number={} sensorname={}'.format(xxx, username, devicename, number, sensorname))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(devicename) == 0 or len(sensorname) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Add/Delete {} Sensor: Empty parameter found\r\n'.format(xxx))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Add/Delete {} Sensor: Token expired [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Add/Delete {} Sensor: Token is invalid [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username


    if flask.request.method == 'POST':
        if orgname is not None:
            # check authorization
            if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Add Peripheral Sensor: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED

        # get parameters
        data = flask.request.get_json()
        #print(data)
        if xxx == 'i2c':
            if data['address'] is None:
                response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
                print('\r\nERROR Add {} Sensor: Parameters not included [{},{}]\r\n'.format(xxx, entityname, devicename))
                return response, status.HTTP_400_BAD_REQUEST
            data["address"] = int(data["address"])
            if data["address"] == 0:
                response = json.dumps({'status': 'NG', 'message': 'Invalid address'})
                print('\r\nERROR Add {} Sensor: Invalid address [{},{}]\r\n'.format(xxx, entityname, devicename))
                return response, status.HTTP_400_BAD_REQUEST
            # check if sensor address is registered
            # address should be unique within a slot
            if g_database_client.get_sensor_by_address(entityname, devicename, xxx, number, data["address"]):
                response = json.dumps({'status': 'NG', 'message': 'Sensor address is already taken'})
                print('\r\nERROR Add {} Sensor: Sensor address is already taken [{},{},{}]\r\n'.format(xxx, entityname, devicename, data["address"]))
                return response, status.HTTP_409_CONFLICT

        if data["manufacturer"] is None or data["model"] is None or data["class"] is None or data["type"] is None or data["units"] is None or data["formats"] is None or data["attributes"] is None:
            response = json.dumps({'status': 'NG', 'message': 'Parameters not included'})
            print('\r\nERROR Add {} Sensor: Parameters not included [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_400_BAD_REQUEST
        #print(data["manufacturer"])
        #print(data["model"])

        # check if sensor is registered
        # name should be unique all throughout the slots
        if g_database_client.check_sensor(entityname, devicename, sensorname):
            response = json.dumps({'status': 'NG', 'message': 'Sensor name is already taken'})
            print('\r\nERROR Add {} Sensor: Sensor name is already taken [{},{},{}]\r\n'.format(xxx, entityname, devicename, sensorname))
            return response, status.HTTP_409_CONFLICT

        # can only register 1 device for adc/1wire/tprobe
        if xxx != 'i2c':
            if g_database_client.get_sensors_count(entityname, devicename, xxx, number) > 0:
                response = json.dumps({'status': 'NG', 'message': 'Cannot add more than 1 sensor for {}'.format(xxx)})
                print('\r\nERROR Add {} Sensor: Cannot add more than 1 sensor [{},{},{}]\r\n'.format(xxx, entityname, devicename, sensorname))
                return response, status.HTTP_400_BAD_REQUEST

        # add sensor to database
        result = g_database_client.add_sensor(entityname, devicename, xxx, number, sensorname, data)
        #print(result)
        if not result:
            response = json.dumps({'status': 'NG', 'message': 'Sensor could not be registered'})
            print('\r\nERROR Add {} Sensor: Sensor could not be registered [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_500_INTERNAL_SERVER_ERROR

        msg = {'status': 'OK', 'message': 'Sensor registered successfully.'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\n{} Sensor registered successful: {}\r\n{}\r\n'.format(xxx, entityname, response))
        return response

    elif flask.request.method == 'DELETE':
        if orgname is not None:
            # check authorization
            if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.DELETE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Delete Peripheral Sensor: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED

        # check if sensor is registered
        sensor = g_database_client.get_sensor(entityname, devicename, xxx, number, sensorname)
        if not sensor:
            response = json.dumps({'status': 'NG', 'message': 'Sensor is not registered'})
            print('\r\nERROR Delete {} Sensor: Sensor is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
            return response, status.HTTP_404_NOT_FOUND

        # delete necessary sensor-related database information
        sensor_cleanup(entityname, devicename, None, xxx, number, sensorname, sensor)

        msg = {'status': 'OK', 'message': 'Sensor unregistered successfully.'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\n{} Sensor unregistered successful: {}\r\n{}\r\n'.format(xxx, username, response))
        return response


########################################################################################################
#
# GET I2C DEVICE
#
# - Request:
#   GET /devices/device/<devicename>/i2c/NUMBER/sensors/sensor/<sensorname>
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'sensor': {'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string}}
#   {'status': 'NG', 'message': string}
#
# GET ADC DEVICE
# GET 1WIRE DEVICE
# GET TPROBE DEVICE
#
# - Request:
#   GET /devices/device/<devicename>/adc/NUMBER/sensors/sensor/<sensorname>
#   GET /devices/device/<devicename>/1wire/NUMBER/sensors/sensor/<sensorname>
#   GET /devices/device/<devicename>/tprobe/NUMBER/sensors/sensor/<sensorname>
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'sensor': {'sensorname': string, 'manufacturer': string, 'model': string, 'timestamp': string}}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>', methods=['GET'])
def get_xxx_sensor(devicename, xxx, number, sensorname):

    # check number parameter
    if int(number) > 4 or int(number) < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get {} Sensor: Invalid authorization header\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensor: Token expired\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_{}_sensor {} devicename={} number={} sensorname={}'.format(xxx, username, devicename, number, sensorname))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(devicename) == 0 or len(sensorname) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get {} Sensor: Empty parameter found\r\n'.format(xxx))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensor: Token expired [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get {} Sensor: Token is invalid [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Get Peripheral Sensor: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username


    # check if sensor is registered
    sensor = g_database_client.get_sensor(entityname, devicename, xxx, number, sensorname)
    if not sensor:
        response = json.dumps({'status': 'NG', 'message': 'Sensor is not registered'})
        print('\r\nERROR Get {} Sensor: Sensor is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
        return response, status.HTTP_404_NOT_FOUND


    msg = {'status': 'OK', 'message': 'Sensor queried successfully.', 'sensor': sensor}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\n{} Sensor queried successful: {}\r\n{}\r\n'.format(xxx, username, response))
    return response


########################################################################################################
#
# GET I2C DEVICE READINGS (per sensor)
#
# - Request:
#   GET /devices/device/<devicename>/i2c/NUMBER/sensors/sensor/<sensorname>/readings
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'sensor_readings': {'value': int, 'lowest': int, 'highest': int} }
#   {'status': 'NG', 'message': string }
#
# GET ADC DEVICE READINGS (per sensor)
# GET 1WIRE DEVICE READINGS (per sensor)
# GET TPROBE DEVICE READINGS (per sensor)
#
# - Request:
#   GET /devices/device/<devicename>/adc/NUMBER/sensors/sensor/<sensorname>/readings
#   GET /devices/device/<devicename>/1wire/NUMBER/sensors/sensor/<sensorname>/readings
#   GET /devices/device/<devicename>/tprobe/NUMBER/sensors/sensor/<sensorname>/readings
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'sensor_readings': {'value': int, 'lowest': int, 'highest': int} }
#   {'status': 'NG', 'message': string }
#
#
# DELETE I2C DEVICE READINGS (per sensor)
#
# - Request:
#   DELETE /devices/device/<devicename>/i2c/NUMBER/sensors/sensor/<sensorname>/readings
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string }
#   {'status': 'NG', 'message': string }
#
# DELETE ADC DEVICE READINGS (per sensor)
# DELETE 1WIRE DEVICE READINGS (per sensor)
# DELETE TPROBE DEVICE READINGS (per sensor)
#
# - Request:
#   DELETE /devices/device/<devicename>/adc/NUMBER/sensors/sensor/<sensorname>/readings
#   DELETE /devices/device/<devicename>/1wire/NUMBER/sensors/sensor/<sensorname>/readings
#   DELETE /devices/device/<devicename>/tprobe/NUMBER/sensors/sensor/<sensorname>/readings
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string }
#   {'status': 'NG', 'message': string }
#
########################################################################################################
@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>/readings', methods=['GET', 'DELETE'])
def get_xxx_sensor_readings(devicename, xxx, number, sensorname):

    # check number parameter
    if int(number) > 4 or int(number) < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get {} Sensor: Invalid authorization header\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensor: Token expired\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_{}_sensor_readings {} devicename={} number={} sensorname={}'.format(xxx, username, devicename, number, sensorname))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(devicename) == 0 or len(sensorname) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get {} Sensor: Empty parameter found\r\n'.format(xxx))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensor: Token expired [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get {} Sensor: Token is invalid [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username


    # check if sensor is registered
    sensor = g_database_client.get_sensor(entityname, devicename, xxx, number, sensorname)
    if not sensor:
        response = json.dumps({'status': 'NG', 'message': 'Sensor is not registered'})
        print('\r\nERROR Get {} Sensor: Sensor is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
        return response, status.HTTP_404_NOT_FOUND

    # check if sensor type is valid
    if sensor["type"] != "input":
        response = json.dumps({'status': 'NG', 'message': 'Sensor type is invalid'})
        print('\r\nERROR Get {} Sensor: Sensor type is invalid [{},{}]\r\n'.format(xxx, entityname, devicename))
        return response, status.HTTP_404_NOT_FOUND

    address = None
    if sensor.get("address"):
        address = sensor["address"]
    source = "{}{}".format(xxx, number)
    if flask.request.method == 'GET':
        if orgname is not None:
            # check authorization
            if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get Peripheral Sensor: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED

        # get sensor reading
        sensor_readings = g_database_client.get_sensor_reading(entityname, devicename, source, address)
        if not sensor_readings:
            # no readings yet
            sensor_readings = {}
            sensor_readings["value"] = "0"
            sensor_readings["lowest"] = "0"
            sensor_readings["highest"] = "0"

        msg = {'status': 'OK', 'message': 'Sensor reading queried successfully.', 'sensor_readings': sensor_readings}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nSensor reading queried successful: {}\r\n{}\r\n'.format(entityname, response))
        return response

    elif flask.request.method == 'DELETE':
        if orgname is not None:
            # check authorization
            if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.DELETE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Delete Peripheral Sensor: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED

        # delete sensor reading
        g_database_client.delete_sensor_reading(entityname, devicename, source, address)

        msg = {'status': 'OK', 'message': 'Sensor reading deleted successfully.'}
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\nSensor reading deleted successful: {}\r\n{}\r\n'.format(entityname, response))
        return response


########################################################################################################
#
# SET I2C DEVICE PROPERTIES
#
# - Request:
#   POST /devices/device/<devicename>/i2c/number/sensors/sensor/<sensorname>/properties
#   headers: {'Authorization': 'Bearer ' + token.access}
#   data: adsasdasdasdasdasdasdasd
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
#
# SET ADC DEVICE PROPERTIES
# SET 1WIRE DEVICE PROPERTIES
# SET TPROBE DEVICE PROPERTIES
#
# - Request:
#   POST /devices/device/<devicename>/adc/number/sensors/sensor/<sensorname>/properties
#   POST /devices/device/<devicename>/1wire/number/sensors/sensor/<sensorname>/properties
#   POST /devices/device/<devicename>/tprobe/number/sensors/sensor/<sensorname>/properties
#   headers: {'Authorization': 'Bearer ' + token.access}
#   data: adsasdasdasdasdasdasdasd
#
# - Response:
#   {'status': 'OK', 'message': string}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>/properties', methods=['POST'])
def set_xxx_dev_prop(devicename, xxx, number, sensorname):
    #print('set_{}_dev_prop'.format(xxx))

    # check number parameter
    if int(number) > 4 or int(number) < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Set {} Sensor: Invalid authorization header\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token} 
    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Set {} Sensor: Token expired\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    print('set_{}_dev_prop {} devicename={} number={} sensorname={}'.format(xxx, username, devicename, number, sensorname))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(devicename) == 0 or len(sensorname) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Set {} Sensor: Empty parameter found\r\n'.format(xxx))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Set {} Sensor: Token expired [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Set {} Sensor: Token is invalid [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = flask.request.get_json()
    if data is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Set Peripheral Sensor: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED

        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username


    # check if sensor is registered
    sensor = g_database_client.get_sensor(entityname, devicename, xxx, number, sensorname)
    if not sensor:
        response = json.dumps({'status': 'NG', 'message': 'Sensor is not registered'})
        print('\r\nERROR Get {} Sensor: Sensor is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
        return response, status.HTTP_404_NOT_FOUND

    api = 'set_{}_dev_prop'.format(xxx)
    #print('set_{}_dev_prop {}'.format(xxx, data))
    data['token'] = token
    data['devicename'] = devicename
    data['username'] = username
    if sensor.get('address'):
        data['address'] = sensor['address']
    data['class'] = int(g_utils.get_i2c_device_class(sensor['class']))
    if sensor.get('subclass'):
        # handle subclasses
        data['subclass'] = int(g_utils.get_i2c_device_class(sensor['subclass']))
    data['number'] = int(number)
    print('set_{}_dev_prop {} devicename={} number={}'.format(xxx, entityname, devicename, number))


    # no notification data
    if not data.get("notification"):
        #print("no notification data")

        response, status_return = g_messaging_requests.process(api, data)
        if status_return != 200:
            # set enabled to FALSE and configured to FALSE
            g_database_client.set_enable_configure_sensor(entityname, devicename, xxx, number, sensorname, 0, 0)
            return response, status_return

        # if ADC/1WIRE/TPROBE, set all other ADC/1WIRE/TPROBE to unconfigured and disabled
        if xxx != "i2c":
            g_database_client.disable_unconfigure_sensors_source(entityname, devicename, xxx, number)
        # set to disabled and configured
        g_database_client.set_enable_configure_sensor(entityname, devicename, xxx, number, sensorname, 0, 1)

        # update device configuration database for device bootup
        #print("data={}".format(data))
        data.pop('number')
        if data.get('address'):
            data.pop('address')
        if data.get('class'):
            data.pop('class')
        if data.get('subclass'):
            data.pop('subclass')

        address = None
        if sensor.get('address'):
            address = sensor['address']
        classid = None
        if sensor.get('class'):
            classid = int(g_utils.get_i2c_device_class(sensor['class']))
        subclassid = None
        if sensor.get('subclass'):
            subclassid = int(g_utils.get_i2c_device_class(sensor['subclass']))
        item = g_database_client.update_device_peripheral_configuration(entityname, devicename, xxx, int(number), address, classid, subclassid, data)

        return response


    # has notification parameter (for class and subclass)
    notification = data['notification']
    data.pop('notification')
    # handle subclasses
    if data.get("subattributes"):
        subattributes_notification = data['subattributes']['notification']
        data['subattributes'].pop('notification')
    else:
        subattributes_notification = None

    # query device
    response, status_return = g_messaging_requests.process(api, data)
    if status_return != 200:
        # set enabled to FALSE and configured to FALSE
        g_database_client.set_enable_configure_sensor(entityname, devicename, xxx, number, sensorname, 0, 0)
        return response, status_return

    # if ADC/1WIRE/TPROBE, set all other ADC/1WIRE/TPROBE to unconfigured and disabled
    if xxx != "i2c":
        g_database_client.disable_unconfigure_sensors_source(entityname, devicename, xxx, number)

    # set to disabled and configured
    g_database_client.set_enable_configure_sensor(entityname, devicename, xxx, number, sensorname, 0, 1)

    source = "{}{}{}".format(xxx, number, sensorname)
    #g_database_client.update_device_notification(entityname, devicename, source, notification)
    g_database_client.update_device_notification_with_notification_subclass(entityname, devicename, source, notification, subattributes_notification)

    # update device configuration database for device bootup
    #print("data={}".format(data))
    data.pop('number')
    if data.get('address'):
        data.pop('address')
    if data.get('class'):
        data.pop('class')
    if data.get('subclass'):
        data.pop('subclass')

    address = None
    if sensor.get('address'):
        address = sensor['address']
    classid = None
    if sensor.get('class'):
        classid = int(g_utils.get_i2c_device_class(sensor['class']))
    subclassid = None
    if sensor.get('subclass'):
        subclassid = int(g_utils.get_i2c_device_class(sensor['subclass']))
    item = g_database_client.update_device_peripheral_configuration(entityname, devicename, xxx, int(number), address, classid, subclassid, data)

    return response



########################################################################################################
#
# GET I2C DEVICE PROPERTIES
#
# - Request:
#   POST /devices/device/<devicename>/i2c/number/sensors/sensor/<sensorname>/properties
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'value': {}}
#   {'status': 'NG', 'message': string}
#
#
# GET ADC DEVICE PROPERTIES
# GET 1WIRE DEVICE PROPERTIES
# GET TPROBE DEVICE PROPERTIES
#
# - Request:
#   POST /devices/device/<devicename>/adc/number/sensors/sensor/<sensorname>/properties
#   POST /devices/device/<devicename>/1wire/number/sensors/sensor/<sensorname>/properties
#   POST /devices/device/<devicename>/tprobe/number/sensors/sensor/<sensorname>/properties
#   headers: {'Authorization': 'Bearer ' + token.access}
#
# - Response:
#   {'status': 'OK', 'message': string, 'value': {}}
#   {'status': 'NG', 'message': string}
#
########################################################################################################
@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>/properties', methods=['GET'])
def get_xxx_dev_prop(devicename, xxx, number, sensorname):
    #print('get_{}_dev_prop'.format(xxx))

    # check number parameter
    if int(number) > 4 or int(number) < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Get {} Sensor: Invalid authorization header\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token} 
    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensor: Token expired\r\n'.format(xxx))
        return response, status.HTTP_401_UNAUTHORIZED
    print('get_{}_dev_prop {} devicename={} number={} sensorname={}'.format(xxx, username, devicename, number, sensorname))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0 or len(devicename) == 0 or len(sensorname) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Get {} Sensor: Empty parameter found\r\n'.format(xxx))
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Get {} Sensor: Token expired [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Get {} Sensor: Token is invalid [{}]\r\n'.format(xxx, username))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.READ) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Get Peripheral Sensor: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED

        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username


    # check if sensor is registered
    sensor = g_database_client.get_sensor(entityname, devicename, xxx, number, sensorname)
    if not sensor:
        response = json.dumps({'status': 'NG', 'message': 'Sensor is not registered'})
        print('\r\nERROR Get {} Sensor: Sensor is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
        return response, status.HTTP_404_NOT_FOUND

    api = 'get_{}_dev_prop'.format(xxx)
    data = {}
    data['token'] = token
    data['devicename'] = devicename
    data['username'] = username
    if sensor.get('address'):
        data['address'] = sensor['address']
    data['class'] = int(g_utils.get_i2c_device_class(sensor['class']))
    data['number'] = int(number)
    print('get_{}_dev_prop {} devicename={} number={}'.format(xxx, entityname, devicename, number))

    # no notification object required
    if data["class"] < rest_api_utils.classes().I2C_DEVICE_CLASS_POTENTIOMETER:
        return g_messaging_requests.process(api, data)

    # has notification object required
    response, status_return = g_messaging_requests.process(api, data)
    if status_return != 200:
        return response, status_return

    source = "{}{}{}".format(xxx, number, sensorname)
    #notification = g_database_client.get_device_notification(entityname, devicename, source)
    (notification, subattributes_notification) = g_database_client.get_device_notification_with_notification_subclass(entityname, devicename, source)
    if notification is not None:
        response = json.loads(response)
        if response.get('value'):
            response['value']['notification'] = notification
        else:
            response['value'] = {}
            response['value']['notification'] = notification
        response = json.dumps(response)
    else:
        response = json.loads(response)
        if response.get('value'):
            response['value']['notification'] = build_default_notifications(xxx, token)
        else:
            response['value'] = {}
            response['value']['notification'] = build_default_notifications(xxx, token)
        response = json.dumps(response)

    # handle subclasses
    if subattributes_notification is not None:
        response = json.loads(response)
        if response.get('value'):
            if response['value'].get('subattributes'):
                response['value']['subattributes']['notification'] = subattributes_notification
        else:
            response['value'] = {}
            response['value']['subattributes']['notification'] = subattributes_notification
        response = json.dumps(response)
    else:
        response = json.loads(response)
        if response.get('value'):
            if response['value'].get('subattributes'):
                response['value']['subattributes']['notification'] = build_default_notifications(xxx, token)
        else:
            response['value'] = {}
            response['value']['subattributes']['notification'] = build_default_notifications(xxx, token)
        response = json.dumps(response)

    return response


########################################################################################################
#
# ENABLE/DISABLE I2C DEVICE
#
# - Request:
#   POST /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/SENSORNAME/enable
#   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
#   data: { 'enable': int }
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
#
# ENABLE/DISABLE ADC DEVICE
# ENABLE/DISABLE 1WIRE DEVICE
# ENABLE/DISABLE TPROBE DEVICE
#
# - Request:
#   POST /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/SENSORNAME/enable
#   POST /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/SENSORNAME/enable
#   POST /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/SENSORNAME/enable
#   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
#   data: { 'enable': int }
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
########################################################################################################
@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>/enable', methods=['POST'])
def enable_xxx_dev(devicename, xxx, number, sensorname):
    api = 'enable_{}_dev'.format(xxx)

    # check number parameter
    if int(number) > 4 or int(number) < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = flask.request.get_json()

    # check parameter input
    if data['enable'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.UPDATE) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Enable Peripheral Sensor: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED

        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username


    # check if sensor is registered
    sensor = g_database_client.get_sensor(entityname, devicename, xxx, number, sensorname)
    if not sensor:
        response = json.dumps({'status': 'NG', 'message': 'Sensor is not registered'})
        print('\r\nERROR Get {} Sensor: Sensor is not registered [{},{}]\r\n'.format(xxx, entityname, devicename))
        return response, status.HTTP_404_NOT_FOUND

    #print(sensor)
    if sensor["configured"] == 0:
        response = json.dumps({'status': 'NG', 'message': 'Sensor is not yet configured'})
        print('\r\nERROR Get {} Sensor: Sensor is yet configured [{},{}]\r\n'.format(xxx, entityname, devicename))
        return response, status.HTTP_400_BAD_REQUEST

    if sensor.get('address'):
        data['address'] = sensor['address']
    # note: python dict maintains insertion order so number will always be the last key
    data['number'] = int(number)
    print('enable_{}_dev {} devicename={} number={}'.format(xxx, entityname, devicename, number))

    do_enable = data['enable']

    # communicate with device
    response, status_return = g_messaging_requests.process(api, data)
    if status_return != 200:
        return response, status_return

    # set enabled to do_enable and configured to 1
    g_database_client.set_enable_configure_sensor(entityname, devicename, xxx, number, sensorname, do_enable, 1)

    # set enabled
    address = None
    if sensor.get('address'):
        address = sensor["address"]
    g_database_client.set_enable_device_peripheral_configuration(entityname, devicename, xxx, int(number), address, do_enable)

    return response


#
# ENABLE/DISABLE I2C
#
# - Request:
#   POST /devices/device/DEVICENAME/i2c/NUMBER/enable
#   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
#   data: { 'enable': int }
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
@app.route('/devices/device/<devicename>/i2c/<number>/enable', methods=['POST'])
def enable_i2c(devicename, number):
    api = 'enable_i2c'

    # check number parameter
    number = int(number)
    if number > 4 or number < 1:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED

    # get username from token
    data = flask.request.get_json()

    # check parameter input
    if data['enable'] is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
        print('\r\nERROR Invalid parameters\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    data['token'] = {'access': auth_header_token}
    data['devicename'] = devicename
    username = g_database_client.get_username_from_token(data['token'])
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    data['username'] = username

    # note: python dict maintains insertion order so number will always be the last key
    data['number'] = number
    print('enable_i2c {} devicename={} number={}'.format(username, devicename, number))

    return g_messaging_requests.process(api, data)


########################################################################################################
#
# DELETE PERIPHERAL SENSOR PROPERTIES
#
# - Request:
#   DELETE /devices/device/DEVICENAME/sensors/properties
#   headers: { 'Authorization': 'Bearer ' + token.access }
#
# - Response:
#   { 'status': 'OK', 'message': string }
#   { 'status': 'NG', 'message': string }
#
########################################################################################################
@app.route('/devices/device/<devicename>/sensors/properties', methods=['DELETE'])
def delete_all_device_sensors_properties(devicename):

    # get token from Authorization header
    auth_header_token = g_utils.get_auth_header_token()
    if auth_header_token is None:
        response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
        print('\r\nERROR Delete All Device Sensors Properties: Invalid authorization header\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    token = {'access': auth_header_token}

    # get username from token
    username = g_database_client.get_username_from_token(token)
    if username is None:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Delete All Device Sensors Properties: Token expired\r\n')
        return response, status.HTTP_401_UNAUTHORIZED
    print('delete_all_device_sensors_properties {} devicename={}'.format(username, devicename))

    # check if a parameter is empty
    if len(username) == 0 or len(token) == 0:
        response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
        print('\r\nERROR Delete All Device Sensors Properties: Empty parameter found\r\n')
        return response, status.HTTP_400_BAD_REQUEST

    # check if username and token is valid
    verify_ret, new_token = g_database_client.verify_token(username, token)
    if verify_ret == 2:
        response = json.dumps({'status': 'NG', 'message': 'Token expired'})
        print('\r\nERROR Delete All Device Sensors Properties: Token expired [{} {}]\r\n'.format(username, devicename))
        return response, status.HTTP_401_UNAUTHORIZED
    elif verify_ret != 0:
        response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
        print('\r\nERROR Delete All Device Sensors Properties: Token is invalid [{} {}]\r\n'.format(username, devicename))
        return response, status.HTTP_401_UNAUTHORIZED


    # get entity using the active organization
    orgname, orgid = g_database_client.get_active_organization(username)
    if orgname is not None:
        # check authorization
        if g_database_client.is_authorized(username, orgname, orgid, database_categorylabel.DEVICES, database_crudindex.DELETE) == False:
            response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
            print('\r\nERROR Delete All Device Sensors Properties: Authorization not allowed [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED

        # has active organization
        entityname = "{}.{}".format(orgname, orgid)
    else:
        # no active organization, just a normal user
        entityname = username

    g_database_client.delete_all_device_peripheral_configuration(entityname, devicename)


    msg = {'status': 'OK', 'message': 'Delete All Device Sensors Properties deleted successfully.',}
    if new_token:
        msg['new_token'] = new_token
    response = json.dumps(msg)
    print('\r\nDelete All Device Sensors Properties successful: {} {}\r\n'.format(username, devicename))
    return response



###################################################################################
# MQTT/AMQP callback functions
###################################################################################

def on_mqtt_message(client, userdata, msg):
    #global g_event_dict, g_queue_dict

    if CONFIG_PREPEND_REPLY_TOPIC != '':
        index = msg.topic.find(CONFIG_PREPEND_REPLY_TOPIC)
        if index == 0:
            try:
                #print("on_mqtt_message {}".format(msg.topic))
                event_response_available = g_event_dict[msg.topic]
                g_event_dict.pop(msg.topic)
                if CONFIG_USE_REDIS_FOR_MQTT_RESPONSE:
                    g_redis_client.mqtt_response_set_payload(msg.topic, msg.payload)
                else:
                    g_queue_dict[msg.topic] = msg.payload
                event_response_available.set()
            except:
                if CONFIG_USE_REDIS_FOR_MQTT_RESPONSE:
                    g_redis_client.mqtt_response_set_payload(msg.topic, msg.payload)
                else:
                    g_queue_dict[msg.topic] = msg.payload
                print("on_mqtt_message exception !!!")
            #print("RCV: {}".format(g_queue_dict))
    else:
        if CONFIG_USE_REDIS_FOR_MQTT_RESPONSE:
            g_redis_client.mqtt_response_set_payload(msg.topic, msg.payload)
        else:
            g_queue_dict[msg.topic] = msg.payload
        #print("RCV: {}".format(g_queue_dict))

def on_amqp_message(ch, method, properties, body):
    #print("RCV: {} {}".format(method.routing_key, body))
    g_queue_dict[method.routing_key] = body
    #print("RCV: {}".format(g_queue_dict))



###################################################################################
# Main entry point
###################################################################################

def initialize():

    global CONFIG_SEPARATOR
    global g_messaging_client
    global g_database_client
    global g_storage_client
    global g_redis_client

    global g_messaging_requests
    global g_identity_authentication
    global g_access_control
    global g_payment_accounting
    global g_device_locations
    global g_device_groups
    global g_device_otaupdates
    global g_device_hierarchies
    global g_device_histories
    global g_other_stuffs
    global g_utils


    CONFIG_SEPARATOR = "." if config.CONFIG_USE_AMQP==1 else "/"

    # Initialize Message broker client
    print("Using {} for webserver-messagebroker communication!".format("AMQP" if config.CONFIG_USE_AMQP else "MQTT"))
    if config.CONFIG_USE_AMQP:
        g_messaging_client = messaging_client(config.CONFIG_USE_AMQP, on_amqp_message, device_id=CONFIG_DEVICE_ID)
        g_messaging_client.set_server(config.CONFIG_HOST, config.CONFIG_AMQP_TLS_PORT)
    else:
        g_messaging_client = messaging_client(config.CONFIG_USE_AMQP, on_mqtt_message)
        g_messaging_client.set_server(config.CONFIG_HOST, config.CONFIG_MQTT_TLS_PORT)
    if config.CONFIG_USERNAME and config.CONFIG_PASSWORD:
        g_messaging_client.set_user_pass(config.CONFIG_USERNAME, config.CONFIG_PASSWORD)
    g_messaging_client.set_tls(config.CONFIG_TLS_CA, config.CONFIG_TLS_CERT, config.CONFIG_TLS_PKEY)
    while True:
        try:
            result = g_messaging_client.initialize(timeout=5)
            if not result:
                print("Could not connect to message broker!")
            else:
                break
        except Exception as e:
            print("Could not connect to message broker! exception! {}".format(e))

    # Initialize Database client
    g_database_client = database_client()
    g_database_client.initialize()

    # Initialize S3 client
    g_storage_client = s3_client()

    # Initialize Redis client
    g_redis_client = redis_client()
    g_redis_client.initialize()

    # Classes
    g_messaging_requests      = messaging_requests(g_database_client, g_messaging_client, g_redis_client, g_event_dict, g_queue_dict)
    g_identity_authentication = identity_authentication(g_database_client, g_redis_client)
    g_access_control          = access_control(g_database_client, g_messaging_client)
    g_payment_accounting      = payment_accounting(g_database_client, g_messaging_client, g_redis_client)
    g_device_locations        = device_locations(g_database_client)
    g_device_groups           = device_groups(g_database_client)
    g_device_otaupdates       = device_otaupdates(g_database_client, g_storage_client, g_messaging_requests)
    g_device_hierarchies      = device_hierarchies(g_database_client, g_messaging_requests)
    g_device_histories        = device_histories(g_database_client)
    g_other_stuffs            = other_stuffs(g_database_client, g_storage_client)
    g_utils                   = rest_api_utils.utils()


# Initialize globally so that no issue with GUnicorn integration
if os.name == 'posix':
    initialize()


if __name__ == '__main__':

    if os.name == 'nt':
        initialize()

    # Initialize HTTP server
    if config.CONFIG_HTTP_USE_TLS:
        context = (config.CONFIG_HTTP_TLS_CERT, config.CONFIG_HTTP_TLS_PKEY)
        port = config.CONFIG_HTTP_TLS_PORT
    else:
        context = None
        port = config.CONFIG_HTTP_PORT
    app.run(ssl_context = context,
        host     = config.CONFIG_HTTP_HOST, 
        port     = port, 
        threaded = True, 
        debug    = True)


