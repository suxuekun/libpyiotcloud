from schematics import Model
from schematics.types import StringType, IntType, DecimalType


class BulkSomthingModel(Model):
    _id = StringType()
    string_attr = StringType()
    int_attr = IntType()
    decimal_attr = DecimalType()