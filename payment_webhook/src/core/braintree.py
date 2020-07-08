from decimal import Decimal

import braintree
import config as braintree_config
from core.payment import PaymentClient
from shared.utils.decimal_util import two_decimal_str


class BrainTreeClient(PaymentClient):
    def __init__(self):
        mode = braintree.Environment.Production if braintree_config.CONFIG_MODE == "live" else braintree.Environment.Sandbox
        self.configuration = braintree.Configuration(
            mode,
            merchant_id = braintree_config.CONFIG_MERCHANT_ID,
            public_key = braintree_config.CONFIG_PUBLIC_KEY,
            private_key = braintree_config.CONFIG_PRIVATE_KEY
        )
        self.gateway = braintree.BraintreeGateway(self.configuration)
    '''
    ' authentication
    '''
    def generate_client_token(self,option=None):
        client_token = self.gateway.client_token.generate(option)
        return client_token
    '''
    ' transaction
    '''
    def find_transaction(self,tid):
        return self.gateway.transaction.find(tid)
    
    def create_transaction(self, amount, payment_method_token, descriptor=None, device_data = None,submit = True):
        str(Decimal(amount))
        options = {
            'amount': two_decimal_str(amount),
            'payment_method_token': payment_method_token,
            'options': {
                "submit_for_settlement": submit
            }
        }
        print(options)
        if device_data:
            options['device_data'] = device_data
        if descriptor:
            options['descriptor'] = descriptor
        result = self.gateway.transaction.sale(options)
        if (result.is_success):
            return result.transaction
        else:
            print(result)
        return None
    def commit_transaction(self,tid):
        return self.gateway.transaction.submit_for_settlement(tid)
    '''
    ' plan
    '''
    @property
    def plans(self):
        plans = self.gateway.plan.all()
        return plans
    
    '''
    ' subscription
    '''
    def create_subscription(self,options):
        '''
        option = {
            'id': "create id", # if needed
            'payment_method_token': "payment_method_token",
            'plan_id': "new_plan",
            'price' : "14.00",
        }
        '''
        result = self.gateway.subscription.create(options)
        print("--create--",result)
        if result.is_success:
            return result.subscription
        print(result)
        return None
    
    def update_subscription(self,sub_id,options):
        '''
        options = {
            "id": "new_id",# if change
            "payment_method_token": "new_payment_method_token",
            "price": "14.00",
            "plan_id": "new_plan",
        }
        '''
        result = self.gateway.subscription.update(sub_id,options)
        print("--update--", result)
        if result.is_success:
            return result.subscription
        print(result)
        return None
    
    def cancel_subscription(self,sub_id):
        result = self.gateway.subscription.cancel(sub_id)
        if result.is_success:
            return result.subscription
        print(result)
        return None
    
    '''
    ' customer
    '''
    def get_customer(self,id):
        result = self.gateway.customer.find(id)
        if result.is_success:
            return result.customer
        print(result)
        return None
    
    def create_customer(self,options=None):
        '''
        options={
            'id':'id',
            'first_name':user.username
        }
        '''
        result = self.gateway.customer.create(options)
        if result.is_success:
            return result.customer
        print(result)
        return None
    
    def create_payment_method(self,customer_id,nonce):
        result = self.gateway.payment_method.create({
            "customer_id": customer_id,
            "payment_method_nonce": nonce
        })
        if result.is_success:
            return result.payment_method
        print(result)
        return None
    
    
        