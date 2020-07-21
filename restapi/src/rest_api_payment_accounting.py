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
from database import database_categorylabel, database_crudindex



CONFIG_SEPARATOR            = '/'
CONFIG_PREPEND_REPLY_TOPIC  = "server"
CONFIG_USE_REDIS_FOR_PAYPAL = False



class payment_accounting:

    def __init__(self, database_client, messaging_client, redis_client):
        self.database_client = database_client
        self.messaging_client = messaging_client
        self.redis_client = redis_client


    def compute_credits_by_amount(self, amount):
        return int(amount * 100)

    def sort_by_timestamp(self, elem):
        return elem['timestamp']

    ########################################################################################################
    #
    # GET SUBSCRIPTION
    #
    # - Request:
    #   GET /account/subscription
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #  {'status': 'OK', 'message': string, 'subscription': {'credits': string, 'type': string} }
    #  {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_subscription(self):
        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get Subscription: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Subscription: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_subscription {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get Subscription: Empty parameter found\r\n')
            # NOTE:
            # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get Subscription: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get Subscription: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.PAYMENTS, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Get Subscription: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        subscription = self.database_client.get_subscription(entityname)
        #print(subscription)
        msg = {'status': 'OK', 'message': 'User subscription queried successfully.', 'subscription': subscription}


        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\n{}: {}\r\n{}\r\n'.format(msg['message'], username, response))
        return response


    ########################################################################################################
    #
    # PAYPAL SETUP
    #
    # - Request:
    #   POST /account/payment/paypalsetup
    #   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
    #   data: { 'returnurl': string, 'cancelurl', string, 'amount': int }
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'payment': {'approvalurl': string, 'paymentid': string}}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def set_payment_paypal_setup(self):
        data = flask.request.get_json()
        if data.get("returnurl") is None or data.get("cancelurl") is None or data.get("amount") is None:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Paypal Setup: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST
        payment = {}
        payment["return_url"] = data["returnurl"]
        payment["cancel_url"] = data["cancelurl"]
        payment["item_price"] = data["amount"]
        payment["item_credits"] = self.compute_credits_by_amount(data["amount"])
        payment["item_sku"] = 'CREDS{}USD{}'.format(payment["item_credits"], payment["item_price"])

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Paypal Setup: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Paypal Setup: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('set_payment_paypal_setup {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Paypal Setup: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Paypal Setup: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Paypal Setup: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.PAYMENTS, database_crudindex.CREATE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Paypal Setup: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        #print(payment)
        approval_url, payment_id, token = self.database_client.transactions_paypal_set_payment(entityname, token, payment)
        msg = {'status': 'OK', 'message': 'Paypal payment setup successful.', 'payment': {'approvalurl': approval_url, 'paymentid': payment_id}}


        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\n{}: {}\r\n'.format(msg['message'], username))
        return response


    ########################################################################################################
    #
    # PAYPAL STORE PAYERID
    #
    # - Request:
    #   POST /account/payment/paypalpayerid/<paymentid>
    #   headers: {'Content-Type': 'application/json'}
    #   data: { 'payerid': string }
    #
    # - Response:
    #   {'status': 'OK', 'message': string}
    #   {'status': 'NG', 'message': string}
    #   // When the returnurl callback from PAYPAL SETUP is called, the web app shall call PAYPAL STORE PAYERID.
    #   // This callback contains the parameters: PayerID and paymentID, needed for payerid and PAYMENTID, respectively
    #   // These parameters should then be stored 
    #
    ########################################################################################################
    def store_payment_paypal_payerid(self, paymentid):
        payerid = None

        data = flask.request.get_json()
        if data.get("payerid"):
            payerid = data["payerid"]

        if CONFIG_USE_REDIS_FOR_PAYPAL:
            # redis
            g_redis_client.paypal_set_payerid(paymentid, payerid)
        else:
            self.database_client.paypal_set_payerid(paymentid, payerid)

        return json.dumps({'status': 'OK', 'message': "Paypal Store PayerID successful."})


    ########################################################################################################
    #
    # PAYPAL EXECUTE
    #
    # - Request:
    #   POST /account/payment/paypalexecute/<paymentid>
    #   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
    #   data: {'payerid': payerid}
    #   // payerid is optional (available for mobile app scenario)
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'subscription': {'type': string, 'credits': int, 'prevcredits': int}}
    #   {'status': 'NG', 'message': string}
    #   // When the callback window completes and exits, the web/mobile app shall call PAYPAL EXECUTE
    #   // This API will internally read the QUERY PAYERID given the PAYMENTID
    #   // and then proceed with execution of the payment transaction
    #   // NG is returned when transaction fails (due to user cancelled or closed the window, etc)
    #
    ########################################################################################################
    def set_payment_paypal_execute(self, paymentid):
        payment = {"paymentId": paymentid}
        data = flask.request.get_json()
        if data is not None and data.get("payerid"):
            # mobile app case
            payment["PayerID"] = data["payerid"]
        else:
            # web app case
            if CONFIG_USE_REDIS_FOR_PAYPAL:
                # redis
                payment["PayerID"] = g_redis_client.paypal_get_payerid(paymentid)
                if payment["PayerID"]:
                    self.redis_client.paypal_del_payerid(paymentid)
            else:
                payment["PayerID"] = self.database_client.paypal_get_payerid(paymentid)
        if payment["PayerID"] is None or payment["PayerID"] == "":
            response = json.dumps({'status': 'NG', 'message': 'Paypal payment execution failed.'})
            return response

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Paypal Execute: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Paypal Execute: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('set_payment_paypal_execute {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Paypal Execute: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Paypal Execute: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Paypal Execute: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.PAYMENTS, database_crudindex.UPDATE) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Paypal Execute: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        #print(payment)
        subscription = None
        status, payment_result = self.database_client.transactions_paypal_execute_payment(entityname, payment)
        if status:
            status, amount = self.database_client.transactions_paypal_verify_payment(entityname, payment)
            if status:
                msg = {'status': 'OK', 'message': 'Paypal payment verified successful.'}

                # get the credits
                credits = self.compute_credits_by_amount(float(amount))
                #print("amount: {} == credits: {}".format(amount, credits))

                # get the current subscription value
                subscription_old = self.database_client.get_subscription(entityname)
                #print("old: {}".format(subscription_old))

                # add the new subscription credits
                subscription = self.database_client.set_subscription(entityname, credits)
                #print("new: {}".format(subscription))
                if subscription:
                    subscription["prevcredits"] = subscription_old["credits"]
                    msg["subscription"] = subscription

                # record the paypal transaction
                transaction = self.database_client.record_paypal_payment(entityname, payment_result, credits, subscription["prevcredits"], subscription["credits"])
                #print(transaction)

                # send email receipt/invoice
                try:
                    pubtopic = CONFIG_PREPEND_REPLY_TOPIC + CONFIG_SEPARATOR + paymentid + CONFIG_SEPARATOR + "email" + CONFIG_SEPARATOR + "send_invoice"
                    payload  = json.dumps({})
                    self.messaging_client.publish(pubtopic, payload)
                    #print("publish xxxxxxxxxxxxx")
                except:
                    pass
            else:
                msg = {'status': 'NG', 'message': 'Paypal payment verified failed.'}
        else:
            msg = {'status': 'NG', 'message': 'Paypal payment execution failed.'}


        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\n{} {}\r\n'.format(msg["message"], username))
        return response


    ########################################################################################################
    #
    # PAYPAL VERIFY
    #
    # - Request:
    #   GET /account/payment/paypalverify/<paymentid>
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'transaction': {'id': string, 'amount': float, 'timestamp': int, 'credits': int, 'prevcredits': int, 'newcredits': int}}
    #   {'status': 'NG', 'message': string}
    #   // OK is successful, NG if failed
    #   // In the web app scenario, the url_callback is called with the different system browser.
    #   // So in order for the original browser to know if the transaction failed or NOT, this API is used.
    #   // When the transaction is completed and verified successfully, the API will return OK, together with the transaction details.
    #
    ########################################################################################################
    def set_payment_paypal_verify(self, paymentid):
        payment = {"paymentId": paymentid}

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Paypal Verify: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Paypal Verify: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('set_payment_paypal_verify {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Paypal Verify: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Paypal Verify: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Paypal Verify: Token is invalid [{}]\r\n'.format(username))
            # NOTE:
            # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.PAYMENTS, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Paypal Verify: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        #print(payment)
        status, amount = self.database_client.transactions_paypal_verify_payment(entityname, payment)
        if status:
            msg = {'status': 'OK', 'message': 'Paypal payment verification successful.'}

            # get record the paypal transaction
            transaction = self.database_client.get_paypal_payment(entityname, paymentid)
            #print(transaction)
            if transaction:
                msg["transaction"] = transaction
        else:
            msg = {'status': 'NG', 'message': 'Paypal payment verification failed.'}


        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\n{} {}\r\n'.format(msg["message"], username))
        return response


    ########################################################################################################
    #
    # GET PAYPAL TRANSACTIONS
    #
    # - Request:
    #   GET /account/payment/paypal
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'transactions': [{'id': string, 'amount': float, 'timestamp': int, 'credits': int}, ...]}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_payment_paypal_transactions(self):

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Paypal Get Transactions: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Paypal Get Transactions: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_payment_paypal_transactions {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Paypal Get Transactions: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Paypal Get Transactions: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Paypal Get Transactions: Token is invalid [{}]\r\n'.format(username))
            # NOTE:
            # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.PAYMENTS, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Paypal Get Transactions: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # get record the paypal transactions
        transactions = self.database_client.get_paypal_payments(entityname)
        transactions.sort(key=self.sort_by_timestamp, reverse=True)
        #print(transactions)


        msg = {'status': 'OK', 'message': 'Paypal Get Transactions successful.'}
        if transactions:
            msg["transactions"] = transactions
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\n{} {}\r\n'.format(msg["message"], username))
        return response


    ########################################################################################################
    #
    # RETRIEVE PAYPAL TRANSACTION
    #
    # - Request:
    #   GET /account/payment/paypal/<transactionid>
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'paypal': json_obj}
    #   {'status': 'NG', 'message': string}
    #
    ########################################################################################################
    def get_payment_paypal_transactions_detailed(self, transactionid):

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Paypal Verify: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Paypal Get Transaction: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_payment_paypal_transactions_detailed {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Paypal Get Transaction: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Paypal Get Transaction: Token expired [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Paypal Get Transaction: Token is invalid [{}]\r\n'.format(username))
            # NOTE:
            # No need to return error code status.HTTP_401_UNAUTHORIZED since this is a logout
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # check authorization
            if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.PAYMENTS, database_crudindex.READ) == False:
                response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                print('\r\nERROR Paypal Get Transaction: Authorization not allowed [{}]\r\n'.format(username))
                return response, status.HTTP_401_UNAUTHORIZED
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        paypal = None
        # get paymentid and payerid given the transactionid
        paymentid = self.database_client.get_paypal_payment_by_transaction_id(entityname, transactionid)
        #print(paymentid)
        if paymentid:
            #pubtopic = CONFIG_PREPEND_REPLY_TOPIC + CONFIG_SEPARATOR + paymentid + CONFIG_SEPARATOR + "send_invoice"
            #payload  = json.dumps({})
            #self.messaging_client.publish(pubtopic, payload)
            #print("publish xxxxxxxxxxxxx")

            # get record the paypal transactions
            paypal_param = self.database_client.transactions_paypal_get_payment(entityname, {'paymentId': paymentid})
            print(paypal_param)
            paypal = {}
            paypal["state"] = paypal_param["state"]
            paypal["payer"] = {}
            paypal["payer"]["payer_info"] = {}
            paypal["payer"]["payer_info"]["payer_id"]     = paypal_param["payer"]["payer_info"]["payer_id"]
            paypal["payer"]["payer_info"]["email"]        = paypal_param["payer"]["payer_info"]["email"]
            paypal["payer"]["payer_info"]["first_name"]   = paypal_param["payer"]["payer_info"]["first_name"]
            paypal["payer"]["payer_info"]["last_name"]    = paypal_param["payer"]["payer_info"]["last_name"]
            paypal["payer"]["payer_info"]["phone"]        = paypal_param["payer"]["payer_info"]["phone"]
            paypal["payer"]["payer_info"]["country_code"] = paypal_param["payer"]["payer_info"]["country_code"]
            paypal["payer"]["payer_info"]["shipping_address"] = {}
            paypal["payer"]["payer_info"]["shipping_address"]["recipient_name"] = paypal_param["payer"]["payer_info"]["shipping_address"]["recipient_name"]
            paypal["payer"]["payer_info"]["shipping_address"]["line1"]          = paypal_param["payer"]["payer_info"]["shipping_address"]["line1"]
            paypal["payer"]["payer_info"]["shipping_address"]["city"]           = paypal_param["payer"]["payer_info"]["shipping_address"]["city"]
            paypal["payer"]["payer_info"]["shipping_address"]["state"]          = paypal_param["payer"]["payer_info"]["shipping_address"]["state"]
            paypal["payer"]["payer_info"]["shipping_address"]["postal_code"]    = paypal_param["payer"]["payer_info"]["shipping_address"]["postal_code"]
            paypal["payer"]["payer_info"]["shipping_address"]["country_code"]   = paypal_param["payer"]["payer_info"]["shipping_address"]["country_code"]
            paypal["transactions"] = [{}]
            paypal["transactions"][0]["amount"] = {}
            paypal["transactions"][0]["amount"]["total"]      = paypal_param["transactions"][0]["amount"]["total"]
            paypal["transactions"][0]["amount"]["currency"]   = paypal_param["transactions"][0]["amount"]["currency"]
            paypal["transactions"][0]["payee"] = {}
            paypal["transactions"][0]["payee"]["merchant_id"] = paypal_param["transactions"][0]["payee"]["merchant_id"]
            paypal["transactions"][0]["payee"]["email"]       = paypal_param["transactions"][0]["payee"]["email"]
            paypal["transactions"][0]["description"]          = paypal_param["transactions"][0]["description"]
            paypal["transactions"][0]["item_list"] = {}
            paypal["transactions"][0]["item_list"]["items"]   = [{}]
            #paypal["transactions"][0]["item_list"]["items"][0][""] paypal_param["transactions"][0]["item_list"]["total"]
            print(paypal)
            #paypal = json.dumps(paypal_param, default=lambda x: getattr(x, '__dict__', str(x)))
            #print_json(paypal, is_json=False)


        msg = {'status': 'OK', 'message': 'Paypal Get Transaction successful.'}
        if paypal:
            msg["paypal"] = paypal
        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        print('\r\n{} {}\r\n'.format(msg["message"], username))
        return response
