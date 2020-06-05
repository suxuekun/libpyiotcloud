from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType
from schematics import Model

class DashboardDto(Model):
    name = StringType(required=True, max_length=15, min_length=5)
    color = StringType()