import time
import hmac
import hashlib
import datetime
import random
from invoice_config import config
from pymongo import MongoClient
from cognito_client import cognito_client



class database_models:

    MONGODB    = 0
    AWSCOGNITO = 1
    POSTGRESQL = 2



##########################################################
# USER database   : AWS Cognito or MongoDB or PostgreSQL
# DEVICE database : MongoDB or PostgreSQL
##########################################################
class database_client:

    def __init__(self, model_users=database_models.AWSCOGNITO, model_devices=database_models.MONGODB, host=config.CONFIG_MONGODB_HOST, port=config.CONFIG_MONGODB_PORT):
        self.use_cognito = True if model_users==database_models.AWSCOGNITO else False

        # user database
        if model_users == database_models.AWSCOGNITO:
            self._users = database_client_cognito()
        #elif model_users == database_models.MONGODB:
        #    self._users = database_client_mongodb()
        #elif model_users == database_models.POSTGRESQL:
        #    self._users = database_client_postgresql()

        # device database
        if model_devices == database_models.MONGODB:
            self._devices = database_client_mongodb(host, port)
        elif model_devices == database_models.POSTGRESQL:
            self._devices = database_client_postgresql()

    def initialize(self):
        self._users.initialize()
        self._devices.initialize()

    def is_using_cognito(self):
        return self.use_cognito



    ##########################################################
    # transactions
    ##########################################################

    def record_paypal_payment(self, username, payment_result, credits, prevcredits, newcredits):
        return self._devices.record_paypal_payment(username, payment_result, credits, prevcredits, newcredits)

    def get_paypal_payments(self, username):
        return self._devices.get_paypal_payments(username)

    def get_paypal_payment(self, username, payment_id):
        return self._devices.get_paypal_payment(username, payment_id)

    def get_paypal_payment_by_transaction_id(self, username, transaction_id):
        return self._devices.get_paypal_payment_by_transaction_id(username, transaction_id)

    def get_paypal_payment_by_paymentid(self, payment_id):
        return self._devices.get_paypal_payment_by_paymentid(payment_id)



    def paypal_set_payerid(self, payment_id, payer_id):
        self._devices.paypal_set_payerid(payment_id, payer_id)

    def paypal_get_payerid(self, payment_id):
        return self._devices.paypal_get_payerid(payment_id)


    def transactions_paypal_set_payment(self, username, token, payment):
        return self._devices.paypal_set_payment(username, token, payment)

    def transactions_paypal_execute_payment(self, username, payment):
        return self._devices.paypal_execute_payment(username, payment)

    def transactions_paypal_verify_payment(self, username, payment):
        return self._devices.paypal_verify_payment(username, payment)

    def transactions_paypal_get_payment(self, username, payment):
        return self._devices.paypal_get_payment(username, payment)


    ##########################################################
    # users
    ##########################################################

    def get_registered_users(self):
        return self._users.get_registered_users()

    def find_user(self, username):
        return self._users.find_user(username)

    def find_user_ex(self, username):
        return self._users.find_user_ex(username)

    def find_email(self, email):
        return self._users.find_email(email)

    def get_user_info(self, access_token):
        return self._users.get_user_info(access_token)

    def login(self, username, password):
        return self._users.login(username, password)

    def logout(self, token):
        return self._users.logout(token)

    def verify_token(self, username, token):
        return self._users.verify_token(username, token)

    def delete_user(self, username):
        self._users.delete_user(username)

    def add_user(self, username, password, email, givenname, familyname):
        return self._users.add_user(username, password, email, givenname, familyname)

    def confirm_user(self, username, confirmationcode):
        return self._users.confirm_user(username, confirmationcode)

    def get_confirmationcode(self, username):
        return self._users.get_confirmationcode(username)

    def resend_confirmationcode(self, username):
        return self._users.resend_confirmationcode(username)

    def forgot_password(self, username):
        return self._users.forgot_password(username)

    def confirm_forgot_password(self, username, confirmation_code, new_password):
        return self._users.confirm_forgot_password(username, confirmation_code, new_password)

    def get_user_group(self, username):
        return self._users.get_user_group(username)

    def add_user_to_group(self, username):
        return self._users.add_user_to_group(username)

    def remove_user_from_group(self, username):
        return self._users.remove_user_from_group(username)


    ##########################################################
    # history
    ##########################################################

    def add_device_history(self, deviceid, topic, payload, direction):
        devices = self.get_registered_devices()
        if devices:
            for device in devices.find({'deviceid': deviceid},{'devicename':1, 'deviceid': 1}):
                self._devices.add_device_history(device['devicename'], deviceid, topic, payload, direction)
                break

            # limit device history to CONFIG_MAX_HISTORY_PER_DEVICE for each devices
            if config.CONFIG_ENABLE_MAX_HISTORY:
                devices_list = self._devices.get_device_history(deviceid, removeID=False)
                if devices_list:
                    devices_list.sort(key=self.sort_by_timestamp, reverse=True)
                    try:
                        while len(devices_list) > config.CONFIG_MAX_HISTORY_PER_DEVICE:
                            self._devices.delete_device_history(devices_list[-1]['deviceid'], devices_list[-1]['timestamp'], devices_list[-1]['_id'])
                            devices_list.remove(devices_list[-1])
                    except:
                        print("add_device_history Exception occurred")
                        pass

    def get_device_history(self, deviceid):
        return self._devices.get_device_history(deviceid)

    def sort_by_timestamp(self, elem):
        return elem['timestamp']

    def get_user_history(self, username):
        user_histories = []
        users = self._users.get_registered_users()
        devices = self._devices.get_registered_devices()
        if devices and devices.count():
            for device in devices.find({'username': username}):
                histories = self._devices.get_device_history(device["deviceid"])
                for history in histories:
                    history['timestamp'] = datetime.datetime.fromtimestamp(int(history['timestamp'])).strftime('%Y-%m-%d %H:%M:%S')
                if histories and len(histories) > 0:
                    user_histories += histories
        user_histories.sort(key=self.sort_by_timestamp, reverse=True)
        return user_histories


    ##########################################################
    # notifications
    ##########################################################

    def add_device_notification(self, username, devicename, source, notification):
        deviceid = self._devices.get_deviceid(username, devicename)
        return self._devices.add_device_notification(username, devicename, deviceid, source, notification)

    def update_device_notification(self, username, devicename, source, notification):
        deviceid = self._devices.get_deviceid(username, devicename)
        return self._devices.update_device_notification(username, devicename, deviceid, source, notification)

    def update_device_notification_by_deviceid(self, deviceid, source, notification):
        return self._devices.update_device_notification_by_deviceid(deviceid, source, notification)

    def delete_device_notification(self, username, devicename):
        return self._devices.delete_device_notification(username, devicename)

    def get_device_notification(self, username, devicename, source):
        return self._devices.get_device_notification(username, devicename, source)

    def get_device_notification_by_deviceid(self, deviceid, source):
        return self._devices.get_device_notification_by_deviceid(deviceid, source)


    ##########################################################
    # menos
    ##########################################################

    def add_menos_transaction(self, deviceid, recipient, message, type, source, sensorname, timestamp, condition, result):
        self._devices.add_menos_transaction(deviceid, recipient, message, type, source, sensorname, timestamp, condition, result)

    def delete_menos_transaction(self, deviceid):
        self._devices.delete_menos_transaction(deviceid)

    def get_menos_transaction(self, deviceid):
        return self._devices.get_menos_transaction(deviceid)


    ##########################################################
    # sensors
    ##########################################################

    def get_sensor_by_deviceid(self, deviceid, source, number, address):
        return self._devices.get_sensor_by_deviceid(deviceid, source, number, address)


    ##########################################################
    # mobile
    ##########################################################

    def add_mobile_device_token(self, username, devicetoken, service):
        self._devices.add_mobile_device_token(username, devicetoken, service)

    def delete_mobile_device_token(self, username):
        self._devices.delete_mobile_device_token(username)

    def get_mobile_device_token(self, username):
        return self._devices.get_mobile_device_token(username)

    def get_mobile_device_token_by_deviceid(self, deviceid):
        return self._devices.get_mobile_device_token(self._devices.get_username(deviceid))


    ##########################################################
    # devices
    ##########################################################

    def display_devices(self, username):
        self._devices.display_devices(username)

    def get_registered_devices(self):
        return self._devices.get_registered_devices()

    def get_devices(self, username):
        return self._devices.get_devices(username)

    def add_device(self, username, devicename, cert, pkey):
        return self._devices.add_device(username, devicename, cert, pkey)

    def delete_device(self, username, devicename):
        self._devices.delete_device(username, devicename)

    def find_device(self, username, devicename):
        return self._devices.find_device(username, devicename)

    def get_deviceid(self, username, devicename):
        return self._devices.get_deviceid(username, devicename)

    def add_device_heartbeat(self, deviceid):
        return self._devices.add_device_heartbeat(deviceid)

    def get_username(self, deviceid):
        return self._devices.get_username(deviceid)

    def get_devicename(self, deviceid):
        return self._devices.get_devicename(deviceid)


class database_utils:

    def __init__(self):
        pass

    def compute_token(self, timestamp, username, password, email, givenname, familyname):
        key = timestamp.encode('utf-8')
        message = (username + password + email + givenname + familyname).encode('utf-8')
        token = hmac.new(key, message, hashlib.sha1).hexdigest()
        return token

    def compute_deviceid(self, timestamp, username, devicename):
        key = timestamp.encode('utf-8')
        message = (username + devicename).encode('utf-8')
        deviceid = hmac.new(key, message, hashlib.sha1).hexdigest()
        return deviceid


class database_client_cognito:

    def __init__(self):
        self.client = None

    def initialize(self):
        self.client = cognito_client()
        self.access_token = None


    ##########################################################
    # users
    ##########################################################

    def get_registered_users(self):
        (result, users) = self.client.admin_list_users()
        if not result:
            return None
        return users

    def find_user(self, username):
        (result, users) = self.client.admin_list_users()
        if result == False:
            return True
        if users:
            for user in users:
                if user["username"] == username:
                    return True
        return False

    def find_user_ex(self, username):
        (result, users) = self.client.admin_list_users()
        if result == False:
            return None
        if users:
            for user in users:
                if user["username"] == username:
                    return user
        return None

    def find_email(self, email):
        (result, users) = self.client.admin_list_users()
        if result == False:
            return None
        if users:
            for user in users:
                if user["email"] == email:
                    return user["username"]
        return None

    def get_user_info(self, access_token):
        (result, users) = self.client.get_user(access_token)
        if result == False:
            return None
        return users

    def login(self, username, password):
        (result, response) = self.client.login(username, password)
        if not result:
            return None
        self.access_token = response['AuthenticationResult']['AccessToken']
        return self.access_token

    def logout(self, token):
        (result, response) = self.client.logout(token)
        print("cognito logout = {}".format(result))

    def verify_token(self, username, token):
        valid = self.client.verify_token(token, username)
        return valid

    def get_confirmationcode(self, username):
        return None

    def resend_confirmationcode(self, username):
        (result, response) = self.client.resend_confirmation_code(username)
        return result

    def delete_user(self, username):
        pass

    def add_user(self, username, password, email, givenname, familyname):
        (result, response) = self.client.sign_up(username, password, email=email, given_name=givenname, family_name=familyname)
        return result

    def confirm_user(self, username, confirmationcode):
        (result, response) = self.client.confirm_sign_up(username, confirmationcode)
        return result

    def forgot_password(self, username):
        (result, response) = self.client.forgot_password(username)
        return result

    def confirm_forgot_password(self, username, confirmation_code, new_password):
        (result, response) = self.client.confirm_forgot_password(username, confirmation_code, new_password)
        return result

    def get_user_group(self, username):
        val = self.client.admin_list_groups_for_user(username)
        print(val[1])
        return val[1]

    def add_user_to_group(self, username):
        groupname = 'PaidSubscribers'
        val = self.client.admin_add_user_to_group(username, groupname)
        val = self.client.admin_list_groups_for_user(username)
        print(val[1])
        return val[1]

    def remove_user_from_group(self, username):
        groupname = 'PaidSubscribers'
        val = self.client.admin_remove_user_from_group(username, groupname)
        val = self.client.admin_list_groups_for_user(username)
        print(val[1])
        return val[1]


class database_client_mongodb:

    def __init__(self, host, port):
        self.client = None
        self.host = host
        self.port = port

    def initialize(self):
        #mongo_client = MongoClient(self.host, self.port, username=config.CONFIG_MONGODB_USERNAME, password=config.CONFIG_MONGODB_PASSWORD)
        mongo_client = MongoClient(self.host, self.port)
        self.client = mongo_client[config.CONFIG_MONGODB_DB]


    ##########################################################
    # users
    ##########################################################

    def get_registered_users(self):
        return self.client[config.CONFIG_MONGODB_TB_PROFILES]

    def display_users(self):
        users = self.get_registered_users()
        if users:
            for user in users.find({},{'username': 1, 'password':1, 'token':1}):
                print(user)

    def find_user(self, username):
        users = self.get_registered_users()
        if users:
            for user in users.find({},{'username': 1}):
                #print(user)
                if user['username'] == username:
                    return True
        return False

    def find_email(self, email):
        users = self.get_registered_users()
        if users:
            for user in users.find({},{'email': 1}):
                #print(user)
                if user['email'] == email:
                    return user['username']
        return None

    def get_user_info(self, access_token):
        return None

    def login(self, username, password):
        users = self.get_registered_users()
        if users:
            for user in users.find({},{'username': 1, 'password':1, 'token':1}):
                if user['username'] == username and user['password'] == password:
                    return user['token']
        return None

    def logout(self, token):
        pass

    def verify_token(self, username, token):
        users = self.get_registered_users()
        if users:
            for user in users.find({},{'username': 1, 'token':1}):
                #print(user)
                if user['username'] == username and user['token'] == token:
                    return True
        return False

    def get_confirmationcode(self, username):
        users = self.get_registered_users()
        if users:
            for user in users.find({},{'username': 1, 'confirmationcode': 1}):
                #print(user)
                if user['username'] == username:
                    return user['confirmationcode']
        return None

    def resend_confirmationcode(self, username):
        pass

    def delete_user(self, username):
        users = self.get_registered_users()
        if users:
            myquery = { 'username': username }
            users.delete_one(myquery)

    def add_user(self, username, password, email, givenname, familyname):
        timestamp = str(int(time.time()))
        token = database_utils().compute_token(timestamp, username, password, email, givenname, familyname)
        confirmationcode = ''.join(["%s" % random.randint(0, 9) for num in range(0, 6)])
        profile = {}
        profile['username']         = username
        profile['password']         = password
        profile['email']            = email
        profile['givenname']        = givenname
        profile['familyname']       = familyname
        profile['timestamp']        = timestamp
        profile['token']            = token
        profile['status']           = "UNCONFIRMED"
        profile['confirmationcode'] = confirmationcode
        #print('post={}'.format(profile))
        self.client.profiles.insert_one(profile)
        return True

    def confirm_user(self, username, confirmationcode):
        users = self.get_registered_users()
        if users:
            for user in users.find({},{'username': 1, 'password': 1, 'email': 1, 'givenname': 1, 'familyname': 1, 'timestamp': 1, 'token': 1, 'status': 1, 'confirmationcode': 1 }):
                if user['username'] == username:
                    print(user)
                    if user['status'] == "UNCONFIRMED":
                        if user['confirmationcode'] == confirmationcode:
                            user['status'] = "CONFIRMED"
                            users.replace_one({'username': username}, user)
                            return True
                    elif user['status'] == "CONFIRMED":
                        return True
        return False

    def forgot_password(self, username):
        return False

    def confirm_forgot_password(self, username, confirmation_code, new_password):
        return False


    ##########################################################
    # transactions
    ##########################################################

    def get_paymentpayerid_db(self):
        return self.client[config.CONFIG_MONGODB_TB_PAYMENTPAYERIDS]

    def paypal_set_payerid(self, payment_id, payer_id):
        payerids = self.get_paymentpayerid_db()
        item = {}
        item['payment_id']     = payment_id
        item['payer_id']       = payer_id
        payerids.insert_one(item)

    def paypal_get_payerid(self, payment_id):
        payer = None
        payerids = self.get_paymentpayerid_db()
        if payerids:
            for payerid in payerids.find({'payment_id': payment_id}):
                payer = payerid["payer_id"]
                try:
                    payerids.delete_many({'payment_id': payment_id})
                except:
                    pass
                break
        return payer


    def get_paymenttransactions_db(self):
        return self.client[config.CONFIG_MONGODB_TB_PAYMENTTRANSACTIONS]

    def record_paypal_payment(self, username, payment_result, value, prevcredits, credits):
        transactions = self.get_paymenttransactions_db()
        item = {}
        item['username']       = username
        item['payment_id']     = self.paypal.get_payment_id(payment_result)
        item['payer_id']       = self.paypal.get_payer_id(payment_result)
        item['state']          = self.paypal.get_transaction_state(payment_result)

        item['id']             = self.paypal.get_transaction_id(payment_result)
        item['amount']         = self.paypal.get_transaction_amount(payment_result)
        item['value']          = value
        item['prevcredits']    = prevcredits
        item['credits']        = credits

        timestamp = self.paypal.get_transaction_time(payment_result)
        utc_time = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        item['timestamp'] = int((utc_time - datetime.datetime(1970, 1, 1)).total_seconds())

        transactions.insert_one(item)
        return item

    def get_paypal_payments(self, username):
        transactions_list = []
        transactions = self.get_paymenttransactions_db()
        if transactions:
            for transaction in transactions.find({'username': username}):
                transaction.pop('_id')
                #if isinstance(transaction['timestamp'], float)== True:
                #    transaction['timestamp'] = int(transaction['timestamp'])
                #    transactions.replace_one({'username': username, 'payment_id': transaction['payment_id']}, transaction)
                #transaction['value'] = transaction['credits']
                #if transaction.get('newcredits'):
                #    transaction['credits'] = transaction['newcredits']
                #    transaction.pop('newcredits')
                #else:
                #    transaction.pop('credits')
                #transactions.replace_one({'username': username, 'payment_id': transaction['payment_id']}, transaction)

                transaction.pop('username')
                transaction.pop('payment_id') # paymentid should be kept secret, to be used for accessing Paypal database only for backtracking purposes
                transaction.pop('payer_id')
                transaction.pop('state')
                transactions_list.append(transaction)
        return transactions_list

    def get_paypal_payment(self, username, payment_id):
        transactions = self.get_paymenttransactions_db()
        if transactions:
            for transaction in transactions.find({'username': username, 'payment_id': payment_id}):
                transaction.pop('_id')
                transaction.pop('username')
                transaction.pop('payment_id') # paymentid should be kept secret, to be used for accessing Paypal database only for backtracking purposes
                transaction.pop('payer_id')
                transaction.pop('state')
                return transaction
        return None

    def get_paypal_payment_by_paymentid(self, payment_id):
        transactions = self.get_paymenttransactions_db()
        if transactions:
            for transaction in transactions.find({'payment_id': payment_id}):
                transaction.pop('_id')
                transaction.pop('payment_id') # paymentid should be kept secret, to be used for accessing Paypal database only for backtracking purposes
                transaction.pop('state')
                return transaction
        return None

    def get_paypal_payment_by_transaction_id(self, username, transaction_id):
        transactions = self.get_paymenttransactions_db()
        if transactions:
            for transaction in transactions.find({'username': username, 'id': transaction_id}, {'payment_id': 1}):
                return transaction['payment_id']
        return None


    def paypal_set_payment(self, username, token, payment):
        return_url = payment['return_url']
        cancel_url = payment['cancel_url']
        item_price = payment['item_price']
        item_sku = payment['item_sku']
        item_quantity = config.CONFIG_TRANSACTION_QUANTITY
        item_currency = config.CONFIG_TRANSACTION_CURRENCY
        item_name = config.CONFIG_TRANSACTION_NAME
        item_description = config.CONFIG_TRANSACTION_DESCRIPTION

        payment_object = self.paypal.create_payment(return_url, cancel_url, item_price, item_currency, item_quantity, item_name, item_sku, item_description)
        #print(payment_object)
        (status, payment) = self.paypal.send_payment(payment_object)
        if not status:
            print("Payment creation failed! {}".format(payment.error))
            return
        approval_url = self.paypal.get_payment_link(payment)
        #print("\r\nPayment creation successful!\r\n")

        data = {
            "paymentId": payment["id"],
            "token": approval_url[approval_url.find("token=")+len("token="):],
            "create_time": payment["create_time"],
            "sku": item_sku,
        }
        #print(data)
        return approval_url, data["paymentId"], data["token"]

    def paypal_execute_payment(self, username, payment):
        payment_id = payment["paymentId"]
        payer_id = payment["PayerID"]

        result = self.paypal.execute_payment(payment_id, payer_id)
        if not result:
            print("Payment failed!")
            return False, None

        payment_result = self.paypal.fetch_payment(payment_id)
        status = self.paypal.get_payment_status(payment_result)
        if status != "approved":
            print("Payment not yet completed! {}".format(status))
            return False, None

        #print("Payment completed successfully!")
        #self.paypal.display_payment_result(payment_result)
        return True, payment_result

    def paypal_verify_payment(self, username, payment):
        payment_id = payment["paymentId"]
        if not payment_id:
            return False, 0

        payment_result = self.paypal.fetch_payment(payment_id)
        if not payment_result:
            return False, 0

        status = self.paypal.get_payment_status(payment_result)
        if status != "approved":
            print("Payment not yet completed! {}".format(status))
            return False, 0

        #print("Payment completed successfully!")
        #self.paypal.display_payment_result(payment_result)

        #print("\r\ninvoice")
        #invoice = self.paypal.get_invoice(self.paypal.get_cart_id(payment_result))
        #print(invoice)

        return True, self.paypal.get_transaction_amount(payment_result)

    def paypal_get_payment(self, username, payment):
        payment_id = payment["paymentId"]
        if not payment_id:
            print("xxxx")
            return None

        payment_result = self.paypal.fetch_payment(payment_id)
        if not payment_result:
            print("xx")
            return None

        return payment_result


    ##########################################################
    # history
    ##########################################################

    def get_history_document(self):
        return self.client[config.CONFIG_MONGODB_TB_HISTORY]

    def add_device_history(self, devicename, deviceid, topic, payload, direction):
        history = self.get_history_document();
        timestamp = int(time.time())
        item = {}
        item['timestamp'] = timestamp
        item['direction'] = direction
        item['deviceid'] = deviceid
        item['devicename'] = devicename
        item['topic'] = topic
        item['payload'] = payload
        history.insert_one(item);

    def get_device_history(self, deviceid, removeID=True):
        history_list = []
        histories = self.get_history_document();
        if histories:
            for history in histories.find({'deviceid': deviceid}):
                if removeID==True:
                    history.pop('_id')
                history_list.append(history)
        return history_list

    def delete_device_history(self, deviceid, timestamp, id):
        history = self.get_history_document();
        try:
            history.delete_one({'_id': id})
            #history.delete_one({'deviceid': deviceid, 'timestamp': timestamp })
        except:
            print("delete_device_history: Exception occurred")
            pass


    ##########################################################
    # notifications
    ##########################################################

    def get_notifications_document(self):
        return self.client[config.CONFIG_MONGODB_TB_NOTIFICATIONS]

    def add_device_notification(self, username, devicename, deviceid, source, notification):
        notifications = self.get_notifications_document();
        item = {}
        item['username'] = username
        item['devicename'] = devicename
        item['deviceid'] = deviceid
        item['source'] = source
        item['notification'] = notification
        notifications.insert_one(item)

    def update_device_notification(self, username, devicename, deviceid, source, notification):
        notifications = self.get_notifications_document();
        item = {}
        item['username'] = username
        item['devicename'] = devicename
        item['deviceid'] = deviceid
        item['source'] = source
        item['notification'] = notification
        #print("update_device_notification find_one")
        found = notifications.find_one({'username': username, 'devicename': devicename, 'source': source})
        if found is None:
            #print("update_device_notification insert_one")
            #print(found)
            notifications.insert_one(item)
        else:
            #print("update_device_notification replace_one")
            notifications.replace_one({'username': username, 'devicename': devicename, 'deviceid': deviceid, 'source': source}, item)

    def update_device_notification_by_deviceid(self, deviceid, source, notification):
        notifications = self.get_notifications_document()
        if notifications:
            found = notifications.find_one({'deviceid': deviceid, 'source': source})
            if found:
                found["notification"] = notification
                notifications.replace_one({'deviceid': deviceid, 'source': source}, found)

    def delete_device_notification(self, username, devicename):
        notifications = self.get_notifications_document();
        try:
            notifications.delete_many({'username': username, 'devicename': devicename})
        except:
            print("delete_device_notification: Exception occurred")
            pass

    def get_device_notification(self, username, devicename, source):
        notifications = self.get_notifications_document();
        if notifications:
            for notification in notifications.find({'username': username, 'devicename': devicename, 'source': source}):
                notification.pop('_id')
                #print(notification['notification'])
                return notification['notification']
        return None

    def get_device_notification_by_deviceid(self, deviceid, source):
        notifications = self.get_notifications_document();
        if notifications:
            for notification in notifications.find({'deviceid': deviceid, 'source': source}):
                notification.pop('_id')
                #print(notification['notification'])
                return notification['notification']
        return None


    ##########################################################
    # menos
    ##########################################################

    def get_menos_document(self):
        return self.client[config.CONFIG_MONGODB_TB_MENOS]

    def add_menos_transaction(self, deviceid, recipient, message, type, source, sensorname, timestamp, condition, result):
        menos = self.get_menos_document()
        item = {}
        item['deviceid'] = deviceid
        item['timestamp'] = timestamp
        item['recipient'] = recipient
        item['messagelen'] = len(message)
        item['type'] = type
        item['source'] = source
        if sensorname is not None:
            item['sensorname'] = sensorname
        if condition is not None:
            item['condition'] = condition
        item['result'] = result
        menos.insert_one(item)

    def delete_menos_transaction(self, deviceid):
        menos = self.get_menos_document()
        try:
            menos.delete_many({'deviceid': deviceid})
        except:
            print("delete_menos_transaction: Exception occurred")
            pass

    def get_menos_transaction(self, deviceid):
        menos_list = []
        menos = self.get_menos_document()
        if menos and menos.count():
            for menos_item in menos.find({'deviceid': deviceid}):
                menos_item.pop('_id')
                menos_list.append(menos_item)
        return menos_list


    ##########################################################
    # sensors
    ##########################################################

    def get_sensors_document(self):
        return self.client[config.CONFIG_MONGODB_TB_I2CSENSORS]

    def get_sensor_by_deviceid(self, deviceid, source, number, address):
        i2csensors = self.get_sensors_document();
        if i2csensors:
            if address is not None:
                #print("")
                #for i2csensor in i2csensors.find({'deviceid': deviceid, 'source': source, 'number': number}):
                #    print(i2csensor)
                #    print("")
                for i2csensor in i2csensors.find({'deviceid': deviceid, 'source': source, 'number': number, 'address': address}):
                    i2csensor.pop('_id')
                    #i2csensor.pop('username')
                    #i2csensor.pop('devicename')
                    return i2csensor
            else:
                for i2csensor in i2csensors.find({'deviceid': deviceid, 'source': source, 'number': number}):
                    i2csensor.pop('_id')
                    #i2csensor.pop('username')
                    #i2csensor.pop('devicename')
                    return i2csensor
        return None


    ##########################################################
    # mobile device tokens
    ##########################################################

    def get_mobile_devicetokens_document(self):
        return self.client[config.CONFIG_MONGODB_TB_DEVICETOKENS]

    def add_mobile_device_token(self, username, devicetoken, service):
        devicetokens = self.get_mobile_devicetokens_document()
        item = {}
        item['username'] = username
        item['devicetoken'] = [devicetoken]
        item['service'] = [service]

        print("add_mobile_device_token {} {}".format(devicetoken, service))
        found = devicetokens.find_one({'username': username})
        if found is None:
            devicetokens.insert_one(item)
        else:
            print(found)
            if devicetoken in found['devicetoken']:
                for x in range(len(found['devicetoken'])):
                    if devicetoken == found['devicetoken'][x]:
                        if service != found['service'][x]:
                            item['devicetoken'] += found['devicetoken']
                            item['service'] += found['service'] 
                            devicetokens.replace_one({'username': username}, item)
                            break
                        print("already in list")
                        break
            else:
                print("not in list")
                found['devicetoken'] += item['devicetoken']
                found['service'] += item['service']
                devicetokens.replace_one({'username': username}, item)

    def delete_mobile_device_token(self, username):
        devicetokens = self.get_mobile_devicetokens_document()
        try:
            devicetokens.delete_one({'username': username})
        except:
            print("delete_sensors_readings_dataset: Exception occurred")
            pass

    def get_mobile_device_token(self, username):
        response = {"service": [], "devicetoken": []}
        devicetokens = self.get_mobile_devicetokens_document()
        if devicetokens:
            for devicetoken in devicetokens.find({'username': username}):
                response["service"].append(devicetoken["service"])
                response["devicetoken"].append(devicetoken["devicetoken"])
        #print(response)
        return response


    ##########################################################
    # devices
    ##########################################################

    def get_registered_devices(self):
        return self.client[config.CONFIG_MONGODB_TB_DEVICES]

    def display_devices(self, username):
        devices = self.get_registered_devices()
        if devices:
            for device in devices.find({'username': username},{'username': 1, 'devicename':1, 'deviceid': 1, 'timestamp':1, 'cert':1, 'pkey':1}):
                print(device)

    def get_devices(self, username):
        device_list = []
        devices = self.get_registered_devices()
        if devices and devices.count():
            for device in devices.find({'username': username},{'username': 1, 'devicename':1, 'deviceid': 1, 'timestamp':1, 'cert':1, 'pkey':1}):
                device.pop('username')
                device.pop('timestamp')
                device.pop('_id')
                device_list.append(device)
                #device_list.append(str(device))
        return device_list

    def add_device(self, username, devicename, cert, pkey):
        timestamp = str(int(time.time()))
        deviceid = database_utils().compute_deviceid(timestamp, username, devicename)
        device = {}
        device['username']   = username
        device['devicename'] = devicename
        device['deviceid']   = deviceid
        device['timestamp']  = timestamp
        device['cert']       = cert
        device['pkey']       = pkey
        #print('post={}'.format(device))
        self.client.devices.insert_one(device)
        return deviceid

    def delete_device(self, username, devicename):
        devices = self.get_registered_devices()
        if devices:
            myquery = { 'username': username, 'devicename': devicename }
            devices.delete_one(myquery)

    def find_device(self, username, devicename):
        devices = self.get_registered_devices()
        if devices:
            for device in devices.find({'username': username, 'devicename': devicename},{'username': 1, 'devicename': 1, 'deviceid': 1, 'cert':1, 'pkey':1}):
                device.pop('username')
                device.pop('_id')
                return device
        return None

    def get_deviceid(self, username, devicename):
        devices = self.get_registered_devices()
        if devices:
            for device in devices.find({'username': username, 'devicename': devicename},{'deviceid': 1}):
                return device['deviceid']
        return None

    def add_device_heartbeat(self, deviceid):
        devices = self.get_registered_devices()
        if devices:
            for device in devices.find({'deviceid': deviceid},{'username': 1, 'devicename': 1, 'deviceid': 1, 'serialnumber':1, 'timestamp': 1, 'heartbeat': 1, 'version': 1}):
                if device.get('heartbeat'):
                    device['heartbeat'] = str(int(time.time()))
                    devices.replace_one({'deviceid': deviceid}, device)
                else:
                    print('add_device_heartbeat no heartbeat')
                    device['heartbeat'] = str(int(time.time()))
                    devices.replace_one({'deviceid': deviceid}, device)
                return device['heartbeat']
        return None

    def get_username(self, deviceid):
        devices = self.get_registered_devices()
        if devices:
            for device in devices.find({'deviceid': deviceid},{'username': 1}):
                return device['username']
        return None

    def get_devicename(self, deviceid):
        devices = self.get_registered_devices()
        if devices:
            for device in devices.find({'deviceid': deviceid},{'devicename': 1}):
                return device['devicename']
        return None


class database_client_postgresql:

    def __init__(self):
        self.client = None

    def initialize(self):
        #self.client = psycopg2.connect("dbname={} user=postgres password=1234".format(config.CONFIG_POSTGRESQL_DB))
        pass


class database_viewer:

    def __init__(self):
        self.client = database_client()
        self.client.initialize()

    def epoch_to_datetime(self, epoch):
        return datetime.datetime.fromtimestamp(int(epoch)).strftime('%Y-%m-%d %H:%M:%S')

    def show(self):
        users = self.client.get_registered_users()
        if users:
            if not self.client.is_using_cognito:
                for user in users.find({},{'username': 1, 'password': 1, 'email': 1, 'givenname': 1, 'familyname': 1, 'timestamp': 1, 'token': 1, 'status': 1, 'confirmationcode': 1}):
                    print("USERNAME   : {}".format(user["username"]))
                    print("PASSWORD   : {}".format(user["password"]))
                    print("EMAIL      : {}".format(user["email"]))
                    print("GIVENNAME  : {}".format(user["givenname"]))
                    print("FAMILYNAME : {}".format(user["familyname"]))
                    print("timestamp  : {}".format(self.epoch_to_datetime(user["timestamp"])))
                    print("token      : {}".format(user["token"]))
                    print("status     : {}".format(user["status"]))
                    print("confirmationcode : {}".format(user["confirmationcode"]))
                    print("devices    :")
                    devices = self.client.get_registered_devices()
                    if devices and devices.count():
                        for device in devices.find():
                            if device['username'] == user["username"]:
                                print("\r\n    DEVICENAME    : {}".format(device["devicename"]))
                                print("        deviceid  : {}".format(device["deviceid"]))
                                print("        timestamp : {}".format(self.epoch_to_datetime(device["timestamp"])))
                                if False:
                                    print("        cert      : {}...".format(device["cert"][28:68]))
                                    print("        pkey      : {}...".format(device["pkey"][28:68]))
                                else:
                                    print("        cert      : \r\n{}".format(device["cert"]))
                                    print("        pkey      : \r\n{}".format(device["pkey"]))
                    print("")
            else:
                for user in users:
                    print("USERNAME     : {}".format(user["username"]))
                    print("EMAIL        : {}".format(user["email"]))
                    print("GIVENNAME    : {}".format(user["given_name"]))
                    print("FAMILYNAME   : {}".format(user["family_name"]))
                    print("creationdate : {}".format(user["creationdate"]))
                    print("modifieddate : {}".format(user["modifieddate"]))
                    print("enabled      : {}".format(user["enabled"]))
                    print("status       : {}".format(user["status"]))
                    print("devices      :")
                    devices = self.client.get_registered_devices()
                    if devices and devices.count():
                        for device in devices.find({'username': user["username"]}):
                            if device['username'] == user["username"]:
                                print("\r\n    DEVICENAME    : {}".format(device["devicename"]))
                                print("        deviceid  : {}".format(device["deviceid"]))
                                print("        timestamp : {}".format(self.epoch_to_datetime(device["timestamp"])))
                                if False:
                                    print("        cert      : {}...".format(device["cert"][28:68]))
                                    print("        pkey      : {}...".format(device["pkey"][28:68]))
                                else:
                                    print("        cert      : \r\n{}".format(device["cert"]))
                                    print("        pkey      : \r\n{}".format(device["pkey"]))
                                print("histories")
                                histories = self.client.get_device_history(device["deviceid"])
                                for history in histories:
                                    #print(history)
                                    #print(history["deviceid"])
                                    print("        {}".format(history["topic"]))
                                    print("        {}".format(history["payload"]))
                                    print("        {}".format(history["direction"]))
                                    print("        {}".format(history["timestamp"]))
                                    print("")
                    print("")


    def reset(self):
        users = self.client.get_registered_users()
        for user in users:
            devices = self.client.get_registered_devices()
            if devices:
                for device in devices.find({},{'username': 1, 'devicename':1}):
                    if device['username'] == user["username"]:
                        self.client.delete_device(device['username'], device["devicename"])
                        print("Deleted device {}".format(device["devicename"]))
            self.client.delete_user(user["username"])
            print("Deleted user {}".format(user["username"]))


