from decimal import Decimal

from bson import ObjectId

from payment.models.plan import Plan
from payment.models.subscription import NextSubscription, Subscription, CurrentSubscription, SubScriptionStatus, \
    SubScriptionCancelReason
from payment.models.transaction import Transaction, TransactionStatus
from shared.simple_api.service import throw_bad_db_query
from shared.utils import timestamp_util
from shared.utils.decimal_util import two_decimal_str
from shared.utils.timestamp_util import percent_of_month_left
from payment.core import payment_client

class PaymentService():
    def __init__(self,plan_repo,plan_service,subscription_repo,transaction_repo,billing_address_service,promocode_service,customer_service):
        self.plan_service = plan_service
        self.plan_repo = plan_repo
        self.subscription_repo = subscription_repo
        self.transaction_repo = transaction_repo
        self.billing_address_service = billing_address_service
        self.promocode_service = promocode_service
        self.customer_service = customer_service

    def get_client_token(self,username = None):
        customer_id = None
        if (username):
            customer = self.get_user_customer(username)
            customer_id = customer.bt_customer_id
        option = {
            'customer_id':customer_id
        }
        token = payment_client.generate_client_token(option)
        return token

    def get_user_customer(self, username):
        customer = self.customer_service.get_or_create_one({'username':username})
        if not customer.bt_customer_id:
            customer.bt_customer_id = str(ObjectId())
            customer.validate()
            option = {
                'id':customer.bt_customer_id,
                'first_name':username,
            }
            res = payment_client.create_customer(option)
            if not res:
                return None
            self.customer_service.update(customer._id,customer)
        return customer

    def make_transaction(self,amount, payment_method_token,descriptor):
        return payment_client.create_transaction(amount, payment_method_token,descriptor, None, True)

    def _assign_draft(self,subscription,plan):
        draft = NextSubscription()
        draft.bt_sub = str(ObjectId())
        draft.plan = plan
        next_month_first_day = timestamp_util.get_next_month_first_day()
        draft.start = timestamp_util.get_next_month_first_day_timestamp()
        draft.end = timestamp_util.get_last_day_of_month_timestamp(timestamp_util.get_next_month_first_day())
        draft.validate()

        subscription.draft = draft
        subscription.draft_status = True
        subscription.validate()
        self.subscription_repo.update(subscription._id,subscription.to_primitive())

    def _confirm_subscription_plan_change(self, subscription, commit=False):
        subscription.next = subscription.draft
        subscription.draft = None
        subscription.draft_status = False
        subscription.validate()
        if commit:
            self.subscription_repo.update(subscription._id,subscription.to_primitive())

    def _new_subscription(self,payment_method_token,subscription,plan,promocode,gst):
        prorate_dict,_ = self._prorate_without_gst(subscription.next.plan,plan,promocode)
        prorate = prorate_dict.get('prorate')
        self._assign_draft(subscription, plan)
        option = {
            'id':subscription.draft.get_braintree_subscription_id(),
            'payment_method_token': payment_method_token,
            'plan_id': plan.bt_plan_id,
            'price': plan.get_price_str(gst),
        }
        print('new_sub',option,subscription.draft)
        bt_subscription = payment_client.create_subscription(option)
        if (promocode):
            self.promocode_service.add_promocode_usage(subscription._id, promocode)
        if (bt_subscription):
            subscription.current = CurrentSubscription(subscription.draft.to_primitive())
            subscription.current.start = timestamp_util.get_timestamp()
            subscription.current.end = timestamp_util.get_last_day_of_month_timestamp()
            subscription.current.validate()
            subscription.status = SubScriptionStatus.NORMAL
            self._confirm_subscription_plan_change(subscription,commit=True)
            return prorate
        return -1


    def _cancel_subscription(self,subscription):
        sub_id = subscription.next.get_braintree_subscription_id()
        free_plan = self.plan_service.get_free_plan()
        self._assign_draft(subscription,free_plan)
        payment_client.cancel_subscription(sub_id)
        subscription.status = SubScriptionStatus.CANCEL
        subscription.cancel_reason = SubScriptionCancelReason.USER_INTERNAL
        print(subscription.to_primitive())
        self._confirm_subscription_plan_change(subscription, commit=True)
        return True

    def _upgrade_subscription(self,payment_method_token,subscription,plan,promocode,gst):
        prorate_dict,_ = self._prorate_without_gst(subscription.next.plan,plan,promocode)
        prorate = prorate_dict.get('prorate')
        sub_id = subscription.next.get_braintree_subscription_id()
        self._assign_draft(subscription, plan)
        option = {
            'payment_method_token': payment_method_token,
            'plan_id': plan.bt_plan_id,
            'price': plan.get_price_str(gst),
        }
        print('upgrade sub', option)
        bt_subscription = payment_client.update_subscription(sub_id,option)
        if (promocode):
            self.promocode_service.add_promocode_usage(subscription._id, promocode)
        if bt_subscription:
            subscription.current.import_data(subscription.draft.to_primitive())
            subscription.status = SubScriptionStatus.NORMAL
            subscription.current.validate()
            self._confirm_subscription_plan_change(subscription, commit=True)
            return prorate
        return -1

    def _downgrade_subscription(self,payment_method_token,subscription,plan):
        sub_id = subscription.next.get_braintree_subscription_id()
        self._assign_draft(subscription, plan)
        option = {
            'payment_method_token': payment_method_token,
            'plan_id': plan.bt_plan_id,
            'price': plan.get_price_str(),
        }
        print('downgrade sub', option)
        bt_subscription= payment_client.update_subscription(sub_id, option)
        if bt_subscription:
            subscription.status = SubScriptionStatus.DOWNGRADE
            subscription.current.validate()
            self._confirm_subscription_plan_change(subscription, commit=True)
        return True

    def cancel_subscription(self,subscription_id):
        subscription = Subscription(self.subscription_repo.getById(subscription_id),strict=False)
        return self._cancel_subscription(subscription)

    def change_subscription(self,payment_token,subscription_id,plan_id,promocode,gst):
        print('change subscription')
        subscription = Subscription(self.subscription_repo.getById(subscription_id),strict=False)
        subscription.validate()
        plan = Plan(self.plan_repo.getById(plan_id),strict=False)
        plan.validate()
        prorate = Decimal('0.00')
        if (subscription.next.plan.is_free()):
            if (not plan.is_free()):# new_subscription
                prorate = self._new_subscription(payment_token,subscription,plan,promocode,gst)
            else:# free -> free no change
                pass
        else:
            if (plan.is_free()):#paid to free , cancel
                self._cancel_subscription(subscription)
            else:
                if (plan.price >= subscription.next.plan.price):
                    prorate = self._upgrade_subscription(payment_token,subscription,plan,promocode,gst)
                else:
                    self._downgrade_subscription(payment_token,subscription,plan)

        return prorate

    def get_payment_method_token(self,bt_customer_id, nonce):
        payment_method = payment_client.create_payment_method(bt_customer_id, nonce)
        return payment_method.token

    def record_transaction(self,transaction):
        self.transaction_repo.create(transaction.to_primitive())

    # @throw_bad_db_query()
    def checkout(self,username,nonce,changes):
        customer = self.get_user_customer(username)
        bt_customer_id = customer.bt_customer_id
        payment_token = self.get_payment_method_token(bt_customer_id, nonce)
        if not payment_token:
            return None
        bill = Decimal(0.00)
        b = self.billing_address_service.get_or_create_one({'username':username})
        gst = b.get_gst()
        transaction = Transaction()
        for change in changes:
            prorate = Decimal(self.change_subscription(**change.to_primitive(),payment_token= payment_token,gst=gst))
            print(prorate,isinstance(prorate,str))
            if (prorate < 0 ):
                #error
                #should stop
                pass
            else:
                bill += Decimal(prorate)
        print('changes done bill is : ', bill)
        if (bill > 0):
            descriptor= {
                'name': "brt*subscription",
            }
            bt_transaction = self.make_transaction(bill, payment_token,descriptor)
            print(bt_transaction)
            print('after make transaction')
            transaction.bt_trans_id = bt_transaction.id
            transaction.date = timestamp_util.get_timestamp()
            transaction.value = bill
            transaction.status = TransactionStatus.PENDING
            transaction.name = "First Month Payment"
            transaction.remark = 'First Month Payments For Device Plan Subscription'
            transaction.username = username
            self.record_transaction(transaction)
            print('after record transaction')
        return True

    def _prorate_without_gst(self,current_plan,next_plan,promocode):
        if (not current_plan._id):
            return None,'bad old plan id'
        if (not next_plan._id):
            return None,'bad new plan id'
        # print(current_plan,next_plan,promocode)

        _, remain, total = percent_of_month_left()
        rate = 1
        # plan_gap_amount = (next_plan.price - current_plan.price) * rate

        _discount, total_payable = payment_client._get_discounted_amount(next_plan.price, remain, total)
        _, plan_rebate = payment_client._get_discounted_amount(current_plan.price, remain, total)
        prorate = total_payable - plan_rebate
        promo_discount = 0.00
        message = ""
        if prorate <= 0:
            prorate = 0
            total_discount = plan_rebate = total_payable
        else:
            total_discount = plan_rebate
            if promocode:
                promoModel = self.promocode_service.get(promocode)
                if promoModel:
                    payable, promo_discount = promoModel.calc(prorate)
                    prorate = payable
                    total_discount += promo_discount
                else:
                    message = "bad promocode"
        res = {
            'price': next_plan.price,
            'total_payable': total_payable,
            'plan_rebate': plan_rebate,
            'total_discount': total_discount,
            'promo_discount':two_decimal_str(promo_discount),
            'prorate': two_decimal_str(prorate),
            'remaining_days': remain,
            'total_days': total,
        }
        return res,message


    @throw_bad_db_query()
    def prorate(self,old_plan_id,new_plan_id,promocode,query):
        current_plan = Plan(self.plan_repo.getById(old_plan_id), strict=False)
        current_plan.validate()
        next_plan = Plan(self.plan_repo.getById(new_plan_id), strict=False)
        next_plan.validate()
        res,message = self._prorate_without_gst(current_plan,next_plan,promocode)
        try:
            b = self.billing_address_service.get_or_create_one(query)
            res['gst'] = b.get_gst();
        except Exception as _:
            print(_)
        return res,message


    def test(self):
        option = {
            'payment_method_token': 'nkq3yr2',
            'plan_id': "Basic10",
            'price': "10.00",
        }
        print('new_sub', option)
        bt_subscription = payment_client.create_subscription(option)

