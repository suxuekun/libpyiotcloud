from schematics import Model
from schematics.types import StringType, DecimalType, ListType, ModelType, IntType

from shared.core.model import UserMixin, BaseIotModel, TimeStampMixin, PeriodMixin

class TransactionStatus():
    PENDING = "pending"
    CANCEL = "cancel"
    COMPLETE = "complete"
    FAIL = "fail"

class AbstractValueItem(BaseIotModel):
    name = StringType()
    value = DecimalType()
    remark = StringType()

class TransactionItem(PeriodMixin,AbstractValueItem):
    quantity = IntType()
    unit = DecimalType()
    pass

class TransactionSubtotalItem(AbstractValueItem):
    subscriptionID = StringType()
    items = ListType(ModelType(TransactionItem))

class AbstractTransaction(AbstractValueItem):
    date = StringType() #payment date
    status = StringType()
    receipt = StringType()
    bt_trans_id = StringType()
    items = ListType(ModelType(TransactionSubtotalItem))
    gst = DecimalType()
    exchangeRate = DecimalType() # USD to SGD

    def pending(self):
        self.status = TransactionStatus.PENDING

    def cancel(self):
        self.status = TransactionStatus.CANCEL

    def complete(self):
        self.status = TransactionStatus.COMPLETE

class Transaction(AbstractTransaction,UserMixin,TimeStampMixin):
    companyName = StringType()
    billingAddress = StringType()
    btCustomerId = StringType()
    invoiceDate = StringType() # invoice generated date
    pass