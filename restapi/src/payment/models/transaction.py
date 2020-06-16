from schematics import Model
from schematics.types import StringType, DecimalType

from shared.core.model import BaseMongoModel, UserMixin, BaseModel, BaseIotModel


class AbstractTransaction(BaseIotModel):
    name = StringType()
    value = DecimalType()
    remark = StringType()
    start = StringType()
    end = StringType()
    date = StringType()

class Transaction(AbstractTransaction,UserMixin):
    bt_trans_id = StringType()