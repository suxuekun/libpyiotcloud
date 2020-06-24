
from schematics import Model
from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType


class ChartSensorDto(Model):
    deviceId = StringType(required=True, min_length=1)
    chartTypeId = IntType(required=True)