
from schematics import Model
from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType

class ChartGatewayQuery(Model):
    isMobile = BooleanType()
    attributeId = StringType()
    filterId = StringType()
    