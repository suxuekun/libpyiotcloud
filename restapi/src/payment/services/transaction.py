from payment.models.transaction import Transaction, TransactionStatus, TransactionItem, TransactionSubtotalItem
from shared.simple_api.service import BaseMongoService
from shared.utils import timestamp_util


class TransactionService(BaseMongoService):
    def __init__(self,billing_address_service,customer_service,*args,**kwargs):
        super(TransactionService,self).__init__(*args,**kwargs)
        self.billing_address_service = billing_address_service
        self.customer_service = customer_service

    def create_record_by_btraintree_transaction_object(self,item,subscription,timestamp,fail = False):
        transaction = Transaction()
        transaction.bt_trans_id = item.id
        transaction.date = timestamp
        transaction.value = item.amount
        transaction.status = TransactionStatus.FAIL if fail else TransactionStatus.PENDING
        transaction.gst = subscription.gst
        transaction.name = "Recurring Payment - " + subscription.current.plan.name;
        transaction.remark = 'Recurring Payment - ' + subscription.current.plan.name + " - "+ subscription.devicename +'(' + subscription.deviceid +')'
        transaction.username = subscription.username
        billing_address = self.billing_address_service.get_one({'username':subscription.username})
        customer = self.customer_service.get_one({'username':subscription.username})
        transaction.billingAddress = billing_address.billing_address
        transaction.companyName = billing_address.companyName
        transaction.btCustomerId =customer.bt_customer_id

        plan_item = TransactionItem()
        plan_item.name = subscription.current.plan.name
        plan_item.value = item.amount
        plan_item.unit = item.amount
        plan_item.quantity = 1
        plan_item.remark = subscription.deviceid
        plan_item.start = subscription.current.start
        plan_item.end = subscription.current.end
        print('04')
        plan_item.validate()

        sub_item = TransactionSubtotalItem()
        sub_item.items=[plan_item]
        sub_item.subscriptionID = subscription._id
        sub_item.value = item.amount
        sub_item.remark = subscription.devicename
        print('05')

        sub_item.validate()

        transaction.items = [sub_item]
        tid = self.create(transaction)
        return tid
