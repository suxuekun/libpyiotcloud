import json
from bson import ObjectId
from schematics import Model
from schematics.types import StringType, ModelType, BooleanType, IntType, DecimalType

from payment.models.plan import Plan, Usage
from shared.client.db.mongo.test import TestMongoDB
from shared.core.model import UserMixin, BaseIotModel, DeviceMixin, PeriodMixin, MonthPeriodMixin
from shared.utils import timestamp_util

class SubScriptionStatus():
    NORMAL:str = "normal" # current = next , normal status
    CANCEL: str = "cancel" # current = paid plan subscription, next = free = None, in cancel status this month
    DOWNGRADE:str = "downgrade" # current = paid plan subscription != next = paid plan subscription , next.plan.price < current.plan.price, switch plan to a lower plan in ext month
    # DRAFT = "draft" # draft, submitted but not yet confirm paid from payment side

class SubScriptionCancelReason():
    USER_INTERNAL = 'user_internal'
    USER_EXTERNAL = 'user_external'
    SYSTEM = 'system'

class PaymentStatus():
    OVERDUE:str = "over due"
    PENDING:str = "pending"
    SUCCESS:str = "success"
    FAIL:str = "fail"

class PaymentSettings():
    MAX_RETRY = 2

class AbstractSubscription(BaseIotModel,DeviceMixin):
    paymentCode = StringType()  # for verify payment
    status = StringType()
    payment_status = StringType()
    retry_count = IntType(default = 0)
    cancel_reason = StringType()

    def renew_paymentcode(self):
        self.paymentCode = str(ObjectId())
        return

    def is_max_retry(self):
        return self.retry_count >= PaymentSettings.MAX_RETRY

    def reset(self):
        self.status = SubScriptionStatus.NORMAL
        self.payment_status = PaymentStatus.PENDING
        self.retry_count = 0
        self.cancel_reason = ""

class SubscriptionItem(BaseIotModel):
    plan = ModelType(Plan)
    bt_sub = StringType()
    def get_braintree_subscription_id(self):
        return self.bt_sub

class AbstractSubscriptionHistory(Usage,MonthPeriodMixin,SubscriptionItem):
    transactionID = StringType()
    pass

class SubscripionHistory(AbstractSubscriptionHistory):
    pass

class NoticeObject(Model):
    sms = BooleanType(default=False)
    email = BooleanType(default=False)
    notification = BooleanType(default=False)
    storage = BooleanType(default=False)

class CurrentSubscription(SubscripionHistory):
    notice = ModelType(NoticeObject)
    pass

class NextSubscription(SubscriptionItem):
    pass

class Subscription(AbstractSubscription,UserMixin):
    gst = DecimalType()
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
        self.status = SubScriptionStatus.CANCEL

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

