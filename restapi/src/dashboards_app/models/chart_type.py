

from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType
from shared.core.model import BaseModel, TimeStampMixin
from shared.core.model import BaseModel, TimeStampMixin, MongoIdMixin


PIE_CHART = "PIE"
DONUT_CHART = "DONUT"
BAR_CHART = "BAR"
LINE_CHART = "LINE"


class ChartTypeModel(BaseModel):
    _id = IntType()
    name = StringType(required=True)
    parrentId = StringType()
    
class ChartType:
    
    def __init__(self, model: ChartTypeModel):
        self.model = model
        
    @staticmethod
    def create(id: int, name: str):
        model = ChartTypeModel()
        model.name = name
        model._id = id
        return ChartType(model)
    
    
    