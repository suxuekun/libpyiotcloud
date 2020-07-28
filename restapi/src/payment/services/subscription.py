from payment.core import payment_client
from payment.models.device import DeviceLinkModel
from payment.models.subscription import SubScriptionStatus, SubScriptionCancelReason, NextSubscription, PaymentStatus, \
    CurrentSubscription, Subscription, NoticeObject
from shared.simple_api.service import BaseMongoService, throw_bad_db_query
from shared.utils import timestamp_util


class SubscriptionService(BaseMongoService):
    def __init__(self,device_repo,plan_service,payment_client,*args,**kwargs):
        super(SubscriptionService,self).__init__(*args,**kwargs)
        self.device_repo = device_repo
        self.plan_service = plan_service
        self.payment_client = payment_client

    def _match_device_subscription(self,devices,subscriptions):
        sub_idx = dict([(x.deviceid,x)for x in subscriptions])
        dev_idx = dict([(x.deviceid,x)for x in devices])

        #update device name
        for key in dev_idx:
            dev = dev_idx[key]
            sub = sub_idx.get(key)
            if (sub and sub.devicename!= dev.devicename):
                sub.devicename = dev.devicename
                self.repo.update(sub._id,sub)

        add_devs = list(filter(lambda x:not sub_idx.get(x.deviceid),devices))
        remove_subs = list(filter(lambda x:not dev_idx.get(x.deviceid),subscriptions))
        return add_devs,remove_subs

    def create_free_sub_for_new_device_by_device_id(self,device_id):
        one = self.device_repo.get_one({'deviceid':device_id})
        if one:
            device_model = DeviceLinkModel(one,strict=False)
            return self.create_free_sub_for_new_device(device_model)
        else:
            return None


    def create_free_sub_for_new_device(self,device):
        entity = self.model(device.to_primitive(),strict=False)
        freeplan = self.plan_service.get_free_plan()
        entity.make_for_new_device(freeplan,validate=True)
        print(entity.to_primitive())
        new_id = self.create(entity)
        entity._id = str(new_id)
        return entity

    @throw_bad_db_query()
    def get_current_subscriptions(self, query):# remove subscriptions with no device and add free subscription to new add devices
        devices = self.device_repo.gets(query)
        device_models = [DeviceLinkModel(x,strict=False) for x in devices]
        result = self.repo.gets(query)
        subscriptions =[self.model(x,strict=False) for x in result]

        add_devs,remove_subs = self._match_device_subscription(device_models,subscriptions)
        [self._cancel_braintree_subscription(x) for x in remove_subs]
        [self.delete(str(x._id)) for x in remove_subs]
        add_list = [self.create_free_sub_for_new_device(x) for x in add_devs]
        current_list = [item for item in subscriptions if item not in remove_subs]
        current_list = current_list + add_list
        return current_list

    @throw_bad_db_query(False)
    def delete(self, id):
        print('delete', id)
        res = self.repo.delete(id)
        return res

    def cancel_braintree_subscription(self, subscription):
        return self._cancel_braintree_subscription(subscription)

    def _cancel_braintree_subscription(self,subscription):
        print('cancel',subscription.to_primitive())
        if (subscription.next and subscription.next.bt_sub):
            try:
                res = payment_client.cancel_subscription(subscription.next.bt_sub)
                if res:
                    return True
                return False
            except Exception as e:
                print (e)
                return False
        return True

    def cleanup(self,deviceid):
        print('inter subscription delete')
        subscription = self.get_one({'deviceid': deviceid})
        print('cleanup', subscription.to_primitive())
        self.cancel_braintree_subscription(subscription)
        self.delete(subscription._id)

    def get_subscription_by_bt_id(self,bt_sub_id):
        query = {'next.bt_sub':bt_sub_id}
        obj = self.repo.get_one(query)
        if (obj):
            item = Subscription(obj,strict=False)
            return item
        print('failed to find with id')
        return None

    def cancel_subscription_by_bt_id(self,bt_sub_id):
        sub = self.get_subscription_by_bt_id(bt_sub_id)
        if (sub):
            return self.cancel_subscription_immediately(sub,SubScriptionCancelReason.SYSTEM)
        return sub

    def subscription_recurring_paid_by_bt_id(self,bt_sub_id):
        sub = self.get_subscription_by_bt_id(bt_sub_id)
        res = self.subscription_recurring_paid(sub)
        if res:
            return sub
        return None

    def subscription_recurring_fail_by_bt_id(self,bt_sub_id):
        sub = self.get_subscription_by_bt_id(bt_sub_id)
        res = self.subscription_recurring_fail(sub)
        if res:
            return sub
        return None

    def subscription_recurring_overdue_by_bt_id(self,bt_sub_id):
        sub = self.get_subscription_by_bt_id(bt_sub_id)
        return self.subscription_recurring_overdue(sub)

    def cancel_subscription_immediately(self,subscription,reason):
        subscription.current.plan = self.plan_service.get_free_plan()
        subscription.current.bt_sub = None
        subscription.current.validate()
        subscription.payment_status = PaymentStatus.FAIL
        return self.cancel_subscription(subscription,reason)

    def cancel_subscription(self,subscription,reason):
        subscription.status = SubScriptionStatus.CANCEL
        subscription.cancel_reason = reason
        subscription.next = next = NextSubscription()
        next.plan = self.plan_service.get_free_plan()
        # next_month_first_day = timestamp_util.get_next_month_first_day()
        # next.start = timestamp_util.get_next_month_first_day_timestamp()
        # next.end = timestamp_util.get_last_day_of_month_timestamp(timestamp_util.get_next_month_first_day())
        next.validate()
        subscription.validate()
        res = self.repo.update(subscription._id, subscription.to_primitive())
        return res

    def subscription_recurring_paid(self,subscription):
        subscription.payment_status = PaymentStatus.SUCCESS
        subscription.validate()
        res = self.repo.update(subscription._id, subscription.to_primitive())
        return res

    def subscription_recurring_fail(self,subscription):
        subscription.retry_count = (subscription.retry_count or 0) +1
        if (subscription.is_max_retry()):
            res = self.cancel_subscription_immediately(subscription,SubScriptionCancelReason.SYSTEM)
        else:
            subscription.validate()
            res = self.repo.update(subscription._id, subscription.to_primitive())
        return res

    def subscription_recurring_overdue(self,subscription):
        subscription.payment_status = PaymentStatus.OVERDUE
        subscription.validate()
        res = self.repo.update(subscription._id, subscription.to_primitive())
        return res

    def subscription_reset_usage(self,subscription):
        subscription.current.reset_email_notification()
        subscription.current.validate()
        res = self.repo.update(subscription._id, subscription.to_primitive())
        return res

    def move_subscription_to_next_month(self,subscription):
        sms = subscription.current.sms
        storage = subscription.current.storage
        sms_100_flag = False
        storage_100_flag = False
        if subscription.current.notice:
            sms_100_flag = subscription.current.notice.sms
            storage_100_flag = subscription.current.notice.storage

        subscription.current = CurrentSubscription(subscription.next.to_primitive())
        subscription.current.start = timestamp_util.get_first_day_of_month_timestamp()
        subscription.current.end = timestamp_util.get_last_day_of_month_timestamp()
        subscription.current.sms = sms
        subscription.current.storage = storage
        subscription.current.notice = NoticeObject()
        subscription.current.notice.sms=sms_100_flag
        subscription.current.notice.storage = storage_100_flag
        subscription.current.notice.validate()
        subscription.current.validate()
        subscription.reset()
        subscription.validate()
        self.repo.update(subscription._id,subscription.to_primitive())
if __name__ == "__main__":
    pass




