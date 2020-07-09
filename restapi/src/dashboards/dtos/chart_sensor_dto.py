
from schematics import Model
from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType


class ChartSensorDto(Model):

    source = StringType(required=True)
    number = StringType(required=True)
    chartTypeId = IntType(required=True)