
from schematics import Model
from schematics.types import StringType, ModelType, IntType, ListType
from dashboards.models.gateway_attribute import AttributeValue

class AttributeResponse(Model):
    name = StringType()
    id = IntType()
    filters = ListType(ModelType(AttributeValue), default=[])