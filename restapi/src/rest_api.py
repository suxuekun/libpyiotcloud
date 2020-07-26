import os
import flask
#from example_module.app import ExampleApp
from flask_json import FlaskJSON, JsonError, json_response, as_json
from flask_cors import CORS
from flask_api import status
#from certificate_generator import certificate_generator
from messaging_client import messaging_client
from rest_api_config import config
from database import database_categorylabel, database_crudindex
from s3_client import s3_client
from redis_client import redis_client
from device_client import device_client
#import ssl
#import json
#import time
#import hmac
#import hashlib
#import base64
#import datetime
#import calendar
#import jwt
#from jose import jwk, jwt
#import http.client
#import threading
#import copy
#import statistics
from message_broker_api import message_broker_api
from rest_api_messaging_requests import messaging_requests
from rest_api_identity_authentication import identity_authentication
from rest_api_access_control import access_control
from rest_api_payment_accounting import payment_accounting
from rest_api_device import device
from rest_api_device_groups import device_groups
from rest_api_device_locations import device_locations
from rest_api_device_otaupdates import device_otaupdates
from rest_api_device_hierarchies import device_hierarchies
from rest_api_device_histories import device_histories
from rest_api_device_peripheral_properties import device_peripheral_properties
from rest_api_device_ldsbus import device_ldsbus
from rest_api_device_dashboard_old import device_dashboard_old
from rest_api_other_stuffs import other_stuffs
import rest_api_utils
from shared.client.clients.database_client import db_client
from shared.middlewares.default_middleware import DefaultMiddleWare
from dashboards.dashboards_app import DashboardsApp
from payment.app import PaymentApp



########################################################################################################
# Some configurations
########################################################################################################

CONFIG_DEVICE_ID            = "restapi_manager"
CONFIG_SEPARATOR            = '/'
CONFIG_PREPEND_REPLY_TOPIC  = "server"
CONFIG_USE_ECC              = True if int(os.environ["CONFIG_USE_ECC"]) == 1 else False
CONFIG_USE_REDIS_FOR_MQTT_RESPONSE  = True

########################################################################################################
# global variables
########################################################################################################

g_messaging_client          = None
g_database_client           = None
g_storage_client            = None
g_redis_client              = None
g_device_client             = None
g_queue_dict  = {} # no longer used; replaced by redis
g_event_dict  = {} # still used to trigger event from callback thread to rest api thread
app = flask.Flask(__name__)
CORS(app)
# app.wsgi_app = DefaultMiddleWare(app.wsgi_app)

########################################################################################################
# Class instances
########################################################################################################

g_messaging_requests           = None
g_identity_authentication      = None
g_access_control               = None
g_payment_accounting           = None
g_device                       = None
g_device_locations             = None
g_device_groups                = None
g_device_otaupdates            = None
g_device_hierarchies           = None
g_device_histories             = None
g_device_ldsbus                = None
g_device_peripheral_properties = None
g_device_dashboard_old         = None
g_other_stuffs                 = None
g_utils                        = None



########################################################################################################
# HTTP REST APIs
########################################################################################################

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


@app.route('/devicegroups/group/<devicegroupname>/location', methods=['GET'])
def get_devicegroup_locations(devicegroupname):
    return g_device_groups.get_devicegroup_locations(devicegroupname)

@app.route('/devicegroups/group/<devicegroupname>/location', methods=['POST'])
def set_devicegroup_locations(devicegroupname):
    return g_device_groups.get_devicegroup_locations(devicegroupname)

@app.route('/devicegroups/group/<devicegroupname>/location', methods=['DELETE'])
def delete_devicegroup_locations(devicegroupname):
    return g_device_groups.get_devicegroup_locations(devicegroupname)


@app.route('/devicegroups/group/<devicegroupname>/ota', methods=['GET'])
def get_devicegroup_ota_statuses(devicegroupname):
    return g_device_groups.get_devicegroup_ota_statuses(devicegroupname)


g_device_groups_list = [
    { "name": "GET DEVICE GROUPS",             "func": get_device_group_list,             "api": "/devicegroups",                                             "method": "GET"    },
    { "name": "ADD DEVICE GROUP",              "func": register_devicegroups,             "api": "/devicegroups/group/<devicegroupname>",                     "method": "POST"   },
    { "name": "DELETE DEVICE GROUP",           "func": register_devicegroups,             "api": "/devicegroups/group/<devicegroupname>",                     "method": "DELETE" },
    { "name": "GET DEVICE GROUP",              "func": register_devicegroups,             "api": "/devicegroups/group/<devicegroupname>",                     "method": "GET"    },
    { "name": "UPDATE DEVICE GROUP NAME",      "func": update_devicegroupname,            "api": "/devicegroups/group/<devicegroupname>/name",                "method": "POST"   },
    { "name": "ADD DEVICE TO GROUP",           "func": register_device_to_devicegroups,   "api": "/devicegroups/group/<devicegroupname>/device/<devicename>", "method": "POST"   },
    { "name": "DELETE DEVICE FROM GROUP",      "func": unregister_device_to_devicegroups, "api": "/devicegroups/group/<devicegroupname>/device/<devicename>", "method": "DELETE" },
    { "name": "SET DEVICES IN DEVICE GROUP",   "func": set_devices_to_devicegroups,       "api": "/devicegroups/group/<devicegroupname>/devices",             "method": "POST"   },
    { "name": "GET DEVICE GROUP DETAILED",     "func": get_devicegroup_detailed,          "api": "/devicegroups/group/<devicegroupname>/devices",             "method": "GET"    },
    { "name": "GET UNGROUPED DEVICES",         "func": get_ungroupeddevices,              "api": "/devicegroups/ungrouped",                                   "method": "GET"    },
    { "name": "GET MIXED DEVICES",             "func": get_mixeddevices,                  "api": "/devicegroups/mixed",                                       "method": "GET"    },
    { "name": "GET DEVICE GROUP LOCATION",     "func": get_devicegroup_locations,         "api": "/devicegroups/group/<devicegroupname>/location",            "method": "GET"    },
    { "name": "SET DEVICE GROUP LOCATION",     "func": set_devicegroup_locations,         "api": "/devicegroups/group/<devicegroupname>/location",            "method": "POST"   },
    { "name": "DELETE DEVICE GROUP LOCATION",  "func": delete_devicegroup_locations,      "api": "/devicegroups/group/<devicegroupname>/location",            "method": "DELETE" },
    { "name": "GET DEVICE GROUP OTA STATUSES", "func": get_devicegroup_ota_statuses,      "api": "/devicegroups/group/<devicegroupname>/ota",                 "method": "GET"    },
]


########################################################################################################
#
# DEVICE LOCATIONS
#
########################################################################################################

@app.route('/devices/location', methods=['POST'])
def set_deviceslocations():
    return g_device_locations.get_deviceslocations()

@app.route('/devices/device/<devicename>/location', methods=['POST'])
def set_devicelocation(devicename):
    return g_device_locations.get_devicelocation(devicename)

@app.route('/devices/location', methods=['GET'])
def get_deviceslocations():
    return g_device_locations.get_deviceslocations()

@app.route('/devices/location', methods=['DELETE'])
def delete_deviceslocations():
    return g_device_locations.get_deviceslocations()

@app.route('/devices/device/<devicename>/location', methods=['GET'])
def get_devicelocation(devicename):
    return g_device_locations.get_devicelocation(devicename)

@app.route('/devices/device/<devicename>/location', methods=['DELETE'])
def delete_devicelocation(devicename):
    return g_device_locations.get_devicelocation(devicename)

g_device_locations_list = [
    { "name": "SET DEVICES LOCATIONS",    "func": set_deviceslocations,    "api": "/devices/location",                     "method": "POST"   },
    { "name": "SET DEVICE LOCATION",      "func": set_devicelocation,      "api": "/devices/device/<devicename>/location", "method": "POST"    },

    { "name": "GET DEVICES LOCATIONS",    "func": get_deviceslocations,    "api": "/devices/location",                     "method": "GET"    },
    { "name": "DELETE DEVICES LOCATIONS", "func": delete_deviceslocations, "api": "/devices/location",                     "method": "DELETE" },
    { "name": "GET DEVICE LOCATION",      "func": get_devicelocation,      "api": "/devices/device/<devicename>/location", "method": "POST"   },
    { "name": "DELETE DEVICE LOCATION",   "func": delete_devicelocation,   "api": "/devices/device/<devicename>/location", "method": "DELETE" },
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
# DEVICES
#
########################################################################################################

@app.route('/devices', methods=['GET'])
def get_device_list():
    return g_device.get_device_list()

@app.route('/devices/filter/<filter>', methods=['GET'])
def get_device_list_filtered(filter):
    return g_device.get_device_list_filtered(filter)

@app.route('/devices/device/<devicename>', methods=['POST'])
def register_device(devicename):
    return g_device.register_device(devicename)

@app.route('/devices/device/<devicename>', methods=['DELETE'])
def unregister_device(devicename):
    return g_device.register_device(devicename)

@app.route('/devices/device/<devicename>', methods=['GET'])
def get_device(devicename):
    return g_device.get_device(devicename)

@app.route('/devices/device/<devicename>/descriptor', methods=['GET'])
def get_device_descriptor(devicename):
    return g_device.get_device_descriptor(devicename)

@app.route('/devices/device/<devicename>/name', methods=['POST'])
def update_devicename(devicename):
    return g_device.update_devicename(devicename)


@app.route('/devices/status', methods=['GET'])
def get_statuses():
    return g_device.get_statuses()

@app.route('/devices/device/<devicename>/status', methods=['GET'])
def get_status(devicename):
    return g_device.get_status(devicename)

@app.route('/devices/device/<devicename>/status', methods=['POST'])
def set_status(devicename):
    return g_device.set_status(devicename)

@app.route('/devices/device/<devicename>/settings', methods=['GET'])
def get_settings(devicename):
    return g_device.get_settings(devicename)

@app.route('/devices/device/<devicename>/settings', methods=['POST'])
def set_settings(devicename):
    return g_device.set_settings(devicename)


@app.route('/devices/device/<devicename>/<xxx>/sensors', methods=['GET'])
def get_all_xxx_sensors(devicename, xxx):
    return g_device.get_all_xxx_sensors(devicename, xxx)

@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors', methods=['GET'])
def get_xxx_sensors(devicename, xxx, number):
    return g_device.get_xxx_sensors(devicename, xxx, number)

@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>', methods=['POST', 'DELETE'])
def register_xxx_sensor(devicename, xxx, number, sensorname):
    return g_device.register_xxx_sensor(devicename, xxx, number, sensorname)

@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>', methods=['GET'])
def get_xxx_sensor(devicename, xxx, number, sensorname):
    return g_device.get_xxx_sensor(devicename, xxx, number, sensorname)


@app.route('/devices/device/<devicename>/sensordata', methods=['POST'])
def download_device_sensor_data(devicename):
    return g_device.download_device_sensor_data(devicename)

@app.route('/devices/device/<devicename>/sensordata', methods=['DELETE'])
def clear_device_sensor_data(devicename):
    return g_device.download_device_sensor_data(devicename)


g_device_list = [
    { "name": "GET DEVICES",                  "func": get_device_list,           "api": "/devices",                                "method": "GET"    },
    { "name": "GET DEVICES (FILTERED)",       "func": get_device_list_filtered,  "api": "/devices/filter/<filter>",                "method": "GET"    },
    { "name": "REGISTER DEVICE",              "func": register_device,           "api": "/devices/device/<devicename>",            "method": "POST"   },
    { "name": "UNREGISTER DEVICE",            "func": unregister_device,         "api": "/devices/device/<devicename>",            "method": "DELETE" },
    { "name": "GET DEVICE",                   "func": get_device,                "api": "/devices/device/<devicename>",            "method": "GET"    },
    { "name": "GET DEVICE DESCRIPTOR",        "func": get_device_descriptor,     "api": "/devices/device/<devicename>/descriptor", "method": "GET"    },
    { "name": "UPDATE DEVICE NAME",           "func": update_devicename,         "api": "/devices/device/<devicename>/name",       "method": "GET"    },

    { "name": "GET DEVICES STATUSES",         "func": get_statuses,              "api": "/devices/status",                         "method": "GET"    },
    { "name": "GET DEVICE STATUS",            "func": get_status,                "api": "/devices/device/<devicename>/status",     "method": "GET"    },
    { "name": "SET DEVICE STATUS",            "func": set_status,                "api": "/devices/device/<devicename>/status",     "method": "POST"   },
    { "name": "GET DEVICE SETTINGS",          "func": get_settings,              "api": "/devices/device/<devicename>/settings",   "method": "GET"    },
    { "name": "SET DEVICE SETTINGS",          "func": set_settings,              "api": "/devices/device/<devicename>/settings",   "method": "POST"   },

    { "name": "GET ALL PERIPHERAL SENSORS",   "func": get_all_xxx_sensors,       "api": "/devices/device/<devicename>/<xxx>/sensors",                              "method": "GET"    },
    { "name": "GET PERIPHERAL SENSORS",       "func": get_xxx_sensors,           "api": "/devices/device/<devicename>/<xxx>/<number>/sensors",                     "method": "GET"    },
    { "name": "REGISTER PERIPHERAL SENSOR",   "func": register_xxx_sensor,       "api": "/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>", "method": "POST"   },
    { "name": "UNREGISTER PERIPHERAL SENSOR", "func": register_xxx_sensor,       "api": "/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>", "method": "DELETE" },
    { "name": "GET PERIPHERAL SENSOR",        "func": get_xxx_sensor,            "api": "/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>", "method": "GET"    },

    { "name": "DOWNLOAD DEVICE SENSOR DATA",  "func": download_device_sensor_data, "api": "/devices/device/<devicename>/sensordata", "method": "POST"   },
    { "name": "CLEAR DEVICE SENSOR DATA",     "func": clear_device_sensor_data,    "api": "/devices/device/<devicename>/sensordata", "method": "DELETE" },
]


########################################################################################################
#
# DEVICE LDS BUS
#
########################################################################################################

@app.route('/devices/device/<devicename>/ldsbus/<portnumber>', methods=['GET'])
def get_lds_bus(devicename, portnumber):
    return g_device_ldsbus.get_lds_bus(devicename, portnumber)

@app.route('/devices/device/<devicename>/ldsbus/<portnumber>', methods=['DELETE'])
def delete_lds_bus(devicename, portnumber):
    return g_device_ldsbus.get_lds_bus(devicename, portnumber)

@app.route('/devices/device/<devicename>/ldsbus/<portnumber>/<component>', methods=['GET'])
def get_lds_bus_component(devicename, portnumber, component):
    return g_device_ldsbus.get_lds_bus_component(devicename, portnumber, component)

@app.route('/devices/device/<devicename>/ldsbus/<portnumber>', methods=['POST'])
def scan_lds_bus(devicename, portnumber):
    return g_device_ldsbus.scan_lds_bus(devicename, portnumber)

@app.route('/devices/device/<devicename>/ldsu/<ldsuuuid>', methods=['GET'])
def get_ldsu(devicename, ldsuuuid):
    return g_device_ldsbus.get_ldsu(devicename, ldsuuuid)

@app.route('/devices/device/<devicename>/ldsu/<ldsuuuid>', methods=['DELETE'])
def delete_ldsu(devicename, ldsuuuid):
    return g_device_ldsbus.get_ldsu(devicename, ldsuuuid)

@app.route('/devices/device/<devicename>/ldsu/<ldsuuuid>/name', methods=['POST'])
def change_ldsu_name(devicename, ldsuuuid):
    return g_device_ldsbus.change_ldsu_name(devicename, ldsuuuid)

@app.route('/devices/device/<devicename>/ldsu/<ldsuuuid>/identify', methods=['POST'])
def identify_ldsu(devicename, ldsuuuid):
    return g_device_ldsbus.identify_ldsu(devicename, ldsuuuid)

# for automation
@app.route('/devices/device/<devicename>/ldsu/<ldsuuuid>/sensors/enable', methods=['POST'])
def enable_ldsu_sensors(devicename, ldsuuuid):
    return g_device_ldsbus.enable_ldsu_sensors(devicename, ldsuuuid)

# for automation
@app.route('/devices/device/<devicename>/ldsu/<ldsuuuid>/sensors/properties', methods=['POST'])
def set_ldsu_sensors_properties(devicename, ldsuuuid):
    return g_device_ldsbus.set_ldsu_sensors_properties(devicename, ldsuuuid)

g_device_ldsbus_list = [
    { "name": "GET LDS BUS",           "func": get_lds_bus,           "api": "/devices/device/<devicename>/ldsbus/<portnumber>",             "method": "GET"    },
    { "name": "DELETE LDS BUS",        "func": get_lds_bus,           "api": "/devices/device/<devicename>/ldsbus/<portnumber>",             "method": "DELETE" },
    { "name": "GET LDS BUS COMPONENT", "func": get_lds_bus_component, "api": "/devices/device/<devicename>/ldsbus/<portnumber>/<component>", "method": "GET"    },
    { "name": "SCAN LDS BUS",          "func": scan_lds_bus,          "api": "/devices/device/<devicename>/ldsbus/<portnumber>",             "method": "POST"   },
    { "name": "GET LDSU",              "func": get_ldsu,              "api": "/devices/device/<devicename>/ldsu/<ldsuuuid>",                 "method": "GET"    },
    { "name": "DELETE LDSU",           "func": delete_ldsu,           "api": "/devices/device/<devicename>/ldsu/<ldsuuuid>",                 "method": "DELETE" },
    { "name": "CHANGE LDSU NAME",      "func": change_ldsu_name,      "api": "/devices/device/<devicename>/ldsu/<ldsuuuid>/name",            "method": "POST"   },
    { "name": "IDENTIFY",              "func": identify_ldsu,         "api": "/devices/device/<devicename>/ldsu/<ldsuuuid>/identify",        "method": "POST"   },
]


########################################################################################################
#
# DEVICE PERIPHERAL PROPERTIES
#
########################################################################################################

#@app.route('/devices/device/<devicename>/uarts', methods=['GET'])
#def get_uarts(devicename):
#    return g_device_peripheral_properties.get_uarts(devicename)

@app.route('/devices/device/<devicename>/uart/properties', methods=['GET'])
def get_uart_prop(devicename):
    return g_device_peripheral_properties.get_uart_prop(devicename)

@app.route('/devices/device/<devicename>/uart/properties', methods=['POST'])
def set_uart_prop(devicename):
    return g_device_peripheral_properties.set_uart_prop(devicename)

@app.route('/devices/device/<devicename>/uart/enable', methods=['POST'])
def enable_uart(devicename):
    return g_device_peripheral_properties.enable_uart(devicename)


@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>/properties', methods=['GET'])
def get_xxx_dev_prop(devicename, xxx, number, sensorname):
    return g_device_peripheral_properties.get_xxx_dev_prop(devicename, xxx, number, sensorname)

@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>/properties', methods=['POST'])
def set_xxx_dev_prop(devicename, xxx, number, sensorname):
    return g_device_peripheral_properties.set_xxx_dev_prop(devicename, xxx, number, sensorname)

@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>/properties', methods=['DELETE'])
def delete_xxx_dev_prop(devicename, xxx, number, sensorname):
    return g_device_peripheral_properties.delete_xxx_dev_prop(devicename, xxx, number, sensorname)


@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>/enable', methods=['POST'])
def enable_xxx_dev(devicename, xxx, number, sensorname):
    return g_device_peripheral_properties.enable_xxx_dev(devicename, xxx, number, sensorname)

@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>/name', methods=['POST'])
def change_xxx_dev_name(devicename, xxx, number, sensorname):
    return g_device_peripheral_properties.change_xxx_dev_name(devicename, xxx, number, sensorname)


@app.route('/devices/device/<devicename>/sensors/properties', methods=['DELETE'])
def delete_all_device_sensors_properties(devicename):
    return g_device_peripheral_properties.delete_all_device_sensors_properties(devicename)


@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>/readings', methods=['GET'])
def get_xxx_dev_readings(devicename, xxx, number, sensorname):
    return g_device_peripheral_properties.get_xxx_dev_readings(devicename, xxx, number, sensorname)


g_device_peripheral_properties_list = [
#    { "name": "GET UARTS",                    "func": get_uarts,           "api": "/devices/device/<devicename>/uarts",           "method": "GET"    },
    { "name": "GET UART PROPERTIES",          "func": get_uart_prop,       "api": "/devices/device/<devicename>/uart/properties", "method": "POST"   },
    { "name": "SET UART PROPERTIES",          "func": set_uart_prop,       "api": "/devices/device/<devicename>/uart/properties", "method": "GET"    },
    { "name": "ENABLE UART",                  "func": enable_uart,         "api": "/devices/device/<devicename>/uart/enable",     "method": "POST"   },

    { "name": "GET LDS DEVICE PROPERTIES",    "func": get_xxx_dev_prop,    "api": "/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>/properties", "method": "GET"    },
    { "name": "SET LDS DEVICE PROPERTIES",    "func": set_xxx_dev_prop,    "api": "/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>/properties", "method": "POST"   },
    { "name": "DELETE LDS DEVICE PROPERTIES", "func": delete_xxx_dev_prop, "api": "/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>/properties", "method": "DELETE" },

    { "name": "ENABLE LDS DEVICE",            "func": enable_xxx_dev,      "api": "/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>/enable",     "method": "POST"   },
    { "name": "CHANGE LDS DEVICE NAME",       "func": change_xxx_dev_name, "api": "/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>/name",       "method": "POST"   },

    { "name": "ENABLE LDS DEVICE PROPERTIES", "func": delete_all_device_sensors_properties, "api": "/devices/device/<devicename>/sensors/properties",                   "method": "DELETE" },

    { "name": "GET LDS DEVICE READINGS",      "func": get_xxx_dev_readings,"api": "/devices/device/<devicename>/<xxx>/<number>/sensors/sensor/<sensorname>/readings",   "method": "GET"    },

]


########################################################################################################
#
# DASHBOARD
#
########################################################################################################

@app.route('/devices/sensors/readings/dataset', methods=['POST'])
def get_all_device_sensors_enabled_input_readings_dataset_filtered():
    return g_device_dashboard_old.get_all_device_sensors_enabled_input_readings_dataset_filtered()

@app.route('/devices/sensors/readings/dataset', methods=['DELETE'])
def delete_all_device_sensors_enabled_input_readings_dataset_filtered():
    return g_device_dashboard_old.get_all_device_sensors_enabled_input_readings_dataset_filtered()


@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/readings', methods=['GET'])
def get_xxx_sensors_readings(devicename, xxx, number):
    return g_device_dashboard_old.get_xxx_sensors_readings(devicename, xxx, number)

@app.route('/devices/device/<devicename>/<xxx>/<number>/sensors/readings', methods=['DELETE'])
def delete_xxx_sensors_readings(devicename, xxx, number):
    return g_device_dashboard_old.get_xxx_sensors_readings(devicename, xxx, number)


g_device_dashboard_old_list = [
    { "name": "", "func": get_all_device_sensors_enabled_input_readings_dataset_filtered,    "api": "/devices/sensors/readings/dataset",                            "method": "POST"   },
    { "name": "", "func": delete_all_device_sensors_enabled_input_readings_dataset_filtered, "api": "/devices/sensors/readings/dataset",                            "method": "DELETE" },

    { "name": "", "func": get_xxx_sensors_readings,                                          "api": "/devices/device/<devicename>/<xxx>/<number>/sensors/readings", "method": "GET"    },
    { "name": "", "func": delete_xxx_sensors_readings,                                       "api": "/devices/device/<devicename>/<xxx>/<number>/sensors/readings", "method": "DELETE" },
]


########################################################################################################
#
# OTHERS
#
########################################################################################################

@app.route('/mobile/devicetoken', methods=['POST'])
def register_mobile_device_token():
    return g_other_stuffs.register_mobile_device_token()

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


# This is for the device simulator. 
# This can be easily blocked by removing entry in nginx.conf.
@app.route('/devicesimulator/devicepassword', methods=['POST'])
def compute_device_password():
    return g_other_stuffs.compute_device_password()

# This is for the device simulator. 
# This can be easily blocked by removing entry in nginx.conf.
@app.route('/devicesimulator/userpasstoken', methods=['POST'])
def compute_userpass_token():
    return g_other_stuffs.compute_userpasstoken()

# This is for the device simulator. 
# This can be easily blocked by removing entry in nginx.conf.
@app.route('/devicesimulator/otaauthcode', methods=['POST'])
def compute_ota_authcode():
    return g_other_stuffs.compute_ota_authcode()



g_other_stuffs_list = [
    { "name": "REGISTER MOBILE TOKEN", "func": register_mobile_device_token, "api": "/mobile/devicetoken",     "method": "POST"   },
    { "name": "SEND FEEDBACK",         "func": send_feedback,                "api": "/others/feedback",        "method": "POST"   },
    { "name": "GET ITEM",              "func": get_item,                     "api": "/others/<item>",          "method": "GET"    },
    { "name": "GET SUPPORTED SENSORS", "func": get_supported_sensors,        "api": "/others/sensordevices",   "method": "GET"    },
    { "name": "GET FIRMWARE UPDATES",  "func": get_device_firmware_updates,  "api": "/others/firmwareupdates", "method": "GET"    },
]



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
    global g_device_client

    global g_messaging_requests
    global g_identity_authentication
    global g_access_control
    global g_payment_accounting
    global g_device
    global g_device_locations
    global g_device_groups
    global g_device_otaupdates
    global g_device_hierarchies
    global g_device_histories
    global g_device_ldsbus
    global g_device_peripheral_properties
    global g_device_dashboard_old
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
    g_database_client = db_client

    # Initialize S3 client
    g_storage_client = s3_client

    # Initialize Redis client
    g_redis_client = redis_client()
    g_redis_client.initialize()

    # Initialize device client
    g_device_client = device_client()
    g_device_client.initialize()

    # Classes
    g_messaging_requests           = messaging_requests(g_database_client, g_messaging_client, g_redis_client, g_event_dict, g_queue_dict)
    g_identity_authentication      = identity_authentication(g_database_client, g_messaging_client, g_redis_client)
    g_access_control               = access_control(g_database_client, g_messaging_client)
    g_device_locations             = device_locations(g_database_client)
    g_device_groups                = device_groups(g_database_client)
    g_device_otaupdates            = device_otaupdates(g_database_client, g_storage_client, g_messaging_requests)
    g_device_hierarchies           = device_hierarchies(g_database_client, g_messaging_requests)
    g_device_histories             = device_histories(g_database_client)
    g_device                       = device(g_database_client, g_messaging_requests, g_messaging_client, g_device_client)
    g_device_ldsbus                = device_ldsbus(g_database_client, g_messaging_requests, g_messaging_client, g_device_client)
    g_device_peripheral_properties = device_peripheral_properties(g_database_client, g_messaging_requests)
    g_other_stuffs                 = other_stuffs(g_database_client, g_storage_client)
    g_utils                        = rest_api_utils.utils()

    dashboardsApp = DashboardsApp(app)
    paymentapp = PaymentApp(app)
    #exampleapp = ExampleApp(app,prefix = "/example")
    # To be replaced
    g_payment_accounting           = payment_accounting(g_database_client, g_messaging_client, g_redis_client)
    g_device_dashboard_old         = device_dashboard_old(g_database_client, g_messaging_requests)


# Initialize globally so that no issue with GUnicorn integration
if os.name == 'posix':
    initialize()


if __name__ == '__main__':

    if config.debugging:
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
        debug    = (config.debugging==1))


