from payment.core import payment_client
from payment.models.device import DeviceLinkModel
from payment.models.subscription import SubScriptionStatus
from shared.client.clients.database_client import db_client
from shared.simple_api.service import BaseMongoService, throw_bad_db_query


class SubscriptionService(BaseMongoService):
    def __init__(self,device_repo,plan_service,*args,**kwargs):
        super(SubscriptionService,self).__init__(*args,**kwargs)
        self.device_repo = device_repo
        self.plan_service = plan_service

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
        return self.repo.get_one({'next':{'bt_sub':bt_sub_id}})

    def cancel_subscription_by_bt_id(self,bt_sub_id):
        sub = self.get_subscription_by_bt_id(bt_sub_id)
        # sub.status = SubScriptionStatus.CANCEL

    def cancel_subscription(self,subscription):
        #TODO
        # subscription.status = SubScriptionStatus.CANCEL
        pass

    def subscription_recurring_paid(self,subscription):
        #TODO
        pass

    def subscription_recurring_fail(self,subscription):
        #TODO
        pass
    def subscription_recurring_overdue(self,subscrption):
        #TODO
        pass












if __name__ == "__main__":
    pass




