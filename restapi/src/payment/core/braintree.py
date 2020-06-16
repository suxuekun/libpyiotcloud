import braintree
from payment.config import braintree_config
from payment.core.payment import PaymentClient
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
    def generate_client_token(self):
        client_token = self.gateway.client_token.generate()
        return client_token
    '''
    ' transaction
    '''
    def find_transaction(self,tid):
        return self.gateway.transaction.find(tid)
    
    def create_transaction(self, AMOUNT, payment_method_token, device_data = None,submit = True):
        options = {
            'amount': str(AMOUNT),
            'payment_method_token': payment_method_token,
            'options': {
                "submit_for_settlement": submit
            }
        }
        if device_data:
            options['device_data'] = device_data
        result = self.gateway.transaction.sale(options)
        return result
    def commit_transaction(self,tid):
        return self.gateway.transaction.submit_for_settlement(tid)
    '''
    ' plan
    '''
    @property
    def plan(self):
        plans = self.gateway.plan.all()
        return plans
    
    '''
    ' subscription
    '''
    def create_subscription(self,options,payment_method_token):
        '''
        option = {
            'payment_method_token': payment_method_token, 
            'plan_id': plan,
            'amount' : amount,
        }
        '''
        result = self.gateway.subscription.create(options)
        return result
    
    def update_subscription(self,sub_id,options):
        result = self.gateway.subscription.update(sub_id,options)
        return result
    
    def cancel_subscription(self,sub_id):
        result = self.gateway.subscription.cancel(sub_id)
        return result
    
    '''
    ' customer
    '''
    def get_customer(self,id):
        result = self.gateway.customer.find(id)
        if result.is_success:
            return result.customer
        return None
    
    def create_customer(self,options=None):
        result = self.gateway.customer.create(options)
        if result.is_success:
            return result.customer
        return None
    
    def create_payment_method(self,customer_id,nonce):
        return self.gateway.payment_method.create({
            "customer_id": customer_id,
            "payment_method_nonce": nonce
        })
    
        