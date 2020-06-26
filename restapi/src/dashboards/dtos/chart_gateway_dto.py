from schematics import Model
from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType

class ChartGatewayDto(Model):
    deviceId = StringType(required=True, min_length=1)
    attributeId = IntType(required=True)
    chartTypeId = IntType(required=True)