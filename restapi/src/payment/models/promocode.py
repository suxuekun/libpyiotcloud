import json
from decimal import Decimal

from schematics.types import StringType, DecimalType, ModelType, IntType
from shared.core.model import TimeStampMixin, BaseModel, UserMixin, MongoIdMixin
from shared.utils import timestamp_util


class PROMOTYPE():
    DISCOUNT = "discount"
    PERCENT_DISCOUNT = "price"

_DISCOUNT_MAPPING={

}

class AbstractPromo(BaseModel,MongoIdMixin):
    name = StringType()
    type = StringType()
    period = IntType()  # 1 is one time, , x is last for x month
    value = DecimalType()
    remark = StringType()

    def __str__(self):
        return self.name

class AbstractPromoCode(BaseModel):
    code = StringType()
    expire = StringType()

    def __str__(self):
        return self.code

class Promo(AbstractPromo,TimeStampMixin):
    pass

class PromoCode(AbstractPromoCode,UserMixin):
    info = ModelType(Promo)
    # username = StringType()# related to username or orgid.orgname

    @property
    def expired(self):
        return self.expire < timestamp_util.get_timestamp()

    def _get_discount_rate(self):
        if self.info.type == PROMOTYPE.PERCENT_DISCOUNT:
            return Decimal(self.info.value /100)
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
        if self.info.type == PROMOTYPE.DISCOUNT:
            return self.info.value
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



if __name__ == "__main__":
    print(json.dumps(Promo.get_mock_object().to_primitive(), indent=4))
    print(json.dumps(PromoCode.get_mock_object().to_primitive(), indent=4))



