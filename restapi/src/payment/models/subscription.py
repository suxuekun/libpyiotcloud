import json
from bson import ObjectId
from schematics import Model
from schematics.types import StringType, ModelType, BooleanType

from payment.models.plan import Plan, Usage
from shared.client.db.mongo.test import TestMongoDB
from shared.core.model import UserMixin, BaseIotModel, DeviceMixin, PeriodMixin, MonthPeriodMixin
from shared.utils import timestamp_util

class SubScriptionStatus():
    NORMAL = "normal" # current = next , normal status
    CANCEL = "cancel" # current = paid plan subscription, next = free = None, in cancel status this month
    DOWNGRADE = "downgrade" # current = paid plan subscription != next = paid plan subscription , next.plan.price < current.plan.price, switch plan to a lower plan in ext month
    # DRAFT = "draft" # draft, submitted but not yet confirm paid from payment side

class SubScriptionCancelReason():
    USER_INTERNAL = 'user_internal'
    USER_EXTERNAL = 'user_external'
    SYSTEM = 'system'

class AbstractSubscription(BaseIotModel,DeviceMixin):
    status = StringType()
    cancel_reason = StringType()

class AbstractSubscriptionHistory(BaseIotModel,Usage,MonthPeriodMixin):
    pass

class SubscriptionItem(BaseIotModel):
    plan = ModelType(Plan)
    bt_sub = StringType()

    def get_braintree_subscription_id(self):
        return self.bt_sub

class SubscripionHistory(SubscriptionItem,AbstractSubscriptionHistory):
    pass

class CurrentSubscription(SubscripionHistory):
    pass

class NextSubscription(SubscriptionItem):
    pass

class Subscription(AbstractSubscription,UserMixin):
    current = ModelType(CurrentSubscription)
    next = ModelType(NextSubscription)
    draft = ModelType(NextSubscription)
    draft_status = BooleanType(default=False)

    def make_for_new_device(self,freeplan,validate=False):
        self.status = SubScriptionStatus.NORMAL
        self.draft_status = False
        self.current = CurrentSubscription()
        self.current.plan = freeplan
        self.next = NextSubscription()
        self.next.plan = freeplan
        if validate:
            self.current.validate()
            self.next.validate()
            self.validate()
        self.draft = None

    def cancel(self):
        self.status == SubScriptionStatus.CANCEL

    def __str__(self):
        return self.device.__str__()

if __name__ == "__main__":
    s = SubscriptionItem.get_mock_object()
    s.plan = Plan.get_mock_object()
    p = s.to_primitive()
    print(json.dumps(p,indent=4))
    res= TestMongoDB().db.test_sub.insert_one(s.to_primitive())

    # TestMongoDB().db.test_sub.find
    print (res.inserted_id)

    print(ObjectId(res.inserted_id))
    pass

