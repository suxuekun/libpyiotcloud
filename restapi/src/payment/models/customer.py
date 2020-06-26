from schematics.types import StringType
from shared.core.model import BaseIotModel, UserMixin

class UserCustomer(BaseIotModel,UserMixin):
    bt_customer_id = StringType()
    pass