import json
from decimal import Decimal

from schematics.types import StringType, DecimalType, ModelType, IntType, ListType
from shared.core.model import TimeStampMixin, BaseModel, UserMixin, MongoIdMixin, PeriodMixin
from shared.utils import timestamp_util


class PROMOTYPE():
    DISCOUNT = "discount"
    PERCENT_DISCOUNT = "p_discount"

class AbstractPromo(BaseModel,MongoIdMixin,PeriodMixin):
    name = StringType()
    type = StringType()
    value = DecimalType()
    sms = DecimalType(default=0)
    email = StringType(default=0)
    notification = StringType(default=0)
    storage = StringType(default=0)
    remark = StringType()

    period = IntType()  # 1 is one time, , x is last for x month
    plans = ListType(StringType())
    max_usage = IntType()

    def __str__(self):
        return self.name

class AbstractPromoCode(AbstractPromo):
    pass
    # code = StringType()
    # expire = StringType()
    #
    # def __str__(self):
    #     return self.code

# class Promo(AbstractPromo,TimeStampMixin):
#     pass

class PromoCode(AbstractPromoCode):
    # info = ModelType(Promo)
    # username = StringType()# related to username or orgid.orgname

    # @property
    # def expired(self):
    #     return self.expire < timestamp_util.get_timestamp()

    def within_validity(self,time):
        # print(self.start,self.end,time)
        if (self.start and int(self.start) > int(time)):
            return False
        if (self.end and int(self.end) < int(time)):
            return False
        return True

    def _get_discount_rate(self):
        if self.type == PROMOTYPE.PERCENT_DISCOUNT:
            return Decimal(self.value /100)
        return Decimal(0.00)

    def _get_rate(self):
        return Decimal(1) - Decimal(self._get_discount_rate())

    @property
    def discount_rate(self):
        return self._get_discount_rate()

    @property
    def rate(self):
        return self._get_rate()


    def _get_discount(self):
        if self.type == PROMOTYPE.DISCOUNT:
            return self.value
        return 0.00

    @property
    def discount(self):
        return self._get_discount()



    def get_discount(self,value):
        v = Decimal(value) * Decimal(self.discount_rate) + Decimal(self.discount)
        if v <0:
            return Decimal(0.00)
        return v

    def get_value_after_discount(self,value):
        v = Decimal(value * self.rate) - Decimal(self.discount)
        if v <0:
            return Decimal(0.00)
        return v

    def calc(self,value):
        pay = self.get_value_after_discount(value)
        discount = Decimal(value) - Decimal(pay)
        return pay,discount

    def allow_plan(self,plan_id):
        return plan_id in self.plans



if __name__ == "__main__":
    # print(json.dumps(Promo.get_mock_object().to_primitive(), indent=4))
    print(json.dumps(PromoCode.get_mock_object().to_primitive(), indent=4))



