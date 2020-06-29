from schematics.types import StringType, DecimalType, ListType, ModelType

from shared.core.model import UserMixin, BaseIotModel, TimeStampMixin, PeriodMixin

class TransactionStatus():
    PENDING = "pending"
    CANCEL = "cancel"
    COMPLETE = "complete"

class AbstractTransaction(BaseIotModel,PeriodMixin):
    name = StringType()
    value = DecimalType()
    remark = StringType()
    date = StringType()
    status = StringType()
    receipt = StringType()
    bt_trans_id = StringType()

    def pending(self):
        self.status = TransactionStatus.PENDING

    def cancel(self):
        self.status = TransactionStatus.CANCEL

    def complete(self):
        self.status = TransactionStatus.COMPLETE

class TransactionItem(BaseIotModel):
    name = StringType()
    remark = StringType()
    value = DecimalType()

class Transaction(AbstractTransaction,UserMixin,TimeStampMixin):
    items = ListType(ModelType(TransactionItem))