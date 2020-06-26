from schematics.types import StringType, DecimalType

from shared.core.model import UserMixin, BaseIotModel, TimeStampMixin, PeriodMixin

class TransactionStatus():
    PENDING = "pending"
    CANCEL = "cancel"
    COMPLETE = "complete"

class AbstractTransaction(BaseIotModel,TimeStampMixin,PeriodMixin):
    name = StringType()
    value = DecimalType()
    remark = StringType()
    date = StringType()
    status = StringType()

    def pending(self):
        self.status = TransactionStatus.PENDING

    def cancel(self):
        self.status = TransactionStatus.CANCEL

    def complete(self):
        self.status = TransactionStatus.COMPLETE

class Transaction(AbstractTransaction,UserMixin):
    bt_trans_id = StringType()