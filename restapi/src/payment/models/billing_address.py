from decimal import Decimal

from schematics.types import StringType
from shared.core.model import TimeStampMixin, UserMixin, BaseModel, MongoIdMixin
from shared.utils import decimal_util


class CountryCode():
    SG = 'Singapore'

_GST = {
    CountryCode.SG.lower():7.00
}

class AbstractBillingAddress(BaseModel):
    name = StringType()
    billing_address = StringType()
    country = StringType()
    city = StringType()
    postal = StringType()
    region = StringType()

    def get_gst(self):
        if self.country:
            return _GST.get(self.country.lower()) or Decimal(0.00)
        return 0.00

    def __str__(self):
        return self.name

class BillingAddress(AbstractBillingAddress,MongoIdMixin,TimeStampMixin,UserMixin):
    pass

