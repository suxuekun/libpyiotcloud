from schematics import Model
from schematics.types import StringType, DecimalType, ListType, ModelType

from shared.core.model import UserMixin, BaseIotModel, TimeStampMixin, PeriodMixin

class TransactionStatus():
    PENDING = "pending"
    CANCEL = "cancel"
    COMPLETE = "complete"

class AbstractValueItem(BaseIotModel):
    name = StringType()
    value = DecimalType()
    remark = StringType()

class TransactionItem(AbstractValueItem):
    pass

class TransactionSubtotalItem(PeriodMixin,AbstractValueItem):
    items = ListType(ModelType(TransactionItem))

class AbstractTransaction(AbstractValueItem):
    date = StringType()
    status = StringType()
    receipt = StringType()
    bt_trans_id = StringType()
    items = ListType(ModelType(TransactionSubtotalItem))

    def pending(self):
        self.status = TransactionStatus.PENDING

    def cancel(self):
        self.status = TransactionStatus.CANCEL

    def complete(self):
        self.status = TransactionStatus.COMPLETE

class Transaction(AbstractTransaction,UserMixin,TimeStampMixin):
    pass