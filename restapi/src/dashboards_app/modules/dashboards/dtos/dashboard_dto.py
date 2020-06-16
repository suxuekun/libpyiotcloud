from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType
from schematics import Model

class DashboardDto(Model):
    name = StringType(required=True, max_length=100, min_length=2)
    color = StringType()