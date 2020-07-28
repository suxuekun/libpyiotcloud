
from typing import List

from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType
from shared.core.model import BaseModel, TimeStampMixin

class GatewayAttribute(BaseModel):
    name = StringType()
    lables = ListType(StringType(), default=[])
    filters = ListType(StringType(), default=[])