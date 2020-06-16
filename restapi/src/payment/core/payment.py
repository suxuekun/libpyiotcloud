class PaymentClient(object):
    def _get_discounted_amount(self, plan_amount, remaining_days, total_days):
        if plan_amount<0:
            return 0
        prorated_amount = round(plan_amount * remaining_days / total_days, 2)
        discounted_amount = round(plan_amount - prorated_amount,2)
        return discounted_amount, prorated_amount
    
    def generate_client_token(self):
        client_token = self.gateway.client_token.generate()
        return client_token
    '''
    ' transaction
    '''
    def find_transaction(self,tid):
        raise NotImplementedError(self.find_transaction.__name__ +" is not implemented")
    
    def create_transaction(self, AMOUNT, payment_method_token, device_data = None,submit = True):
        raise NotImplementedError(self.create_transaction.__name__ +" is not implemented")
    
    def commit_transaction(self,tid):
        raise NotImplementedError(self.create_transaction.__name__ +" is not implemented")
    '''
    ' plan
    '''
    @property
    def plan(self):
        return None
    
    '''
    ' subscription
    '''
    def create_subscription(self,options,payment_method_token):
        raise NotImplementedError(self.create_subscription.__name__ +" is not implemented")
    
    def update_subscription(self,sub_id,options):
        raise NotImplementedError(self.update_subscription.__name__ +" is not implemented")
    
    def cancel_subscription(self,sub_id):
        raise NotImplementedError(self.cancel_subscription.__name__ +" is not implemented")
    
    '''
    ' customer
    '''
    def get_customer(self,id):
        raise NotImplementedError(self.get_customer.__name__ +" is not implemented")
    
    def create_customer(self,options=None):
        raise NotImplementedError(self.create_customer.__name__ +" is not implemented")
    
    def create_payment_method(self,customer_id,nonce):
        raise NotImplementedError(self.create_payment_method.__name__ +" is not implemented")
        
if __name__ == "__main__":
    p = PaymentClient()