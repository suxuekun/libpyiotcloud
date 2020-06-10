
from typing import List

from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType
from shared.core.model import BaseModel, TimeStampMixin


class GatewayAttributeModel(BaseModel):
    name = StringType()
    lables = ListType(StringType(), default=[])
    filters = ListType(StringType(), default=[])
    
class GatewayAttribute():
    
    def __init__(self, model: GatewayAttributeModel):
        self.model = model
    