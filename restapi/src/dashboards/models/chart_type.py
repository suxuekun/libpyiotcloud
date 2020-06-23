

from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType
from shared.core.model import BaseModel, TimeStampMixin


PIE_CHART = "Pie"
PIE_CHART_ID = 0

DONUT_CHART = "Donut"
DONUT_CHART_ID = 1

BAR_CHART = "Bar"
BAR_CHART_ID = 2

LINE_CHART = "Line"
LINE_CHART_ID = 3

class ChartTypeModel(BaseModel):
    _id = IntType()
    name = StringType(required=True)
    parrentId = StringType()

class FactoryChartTypeModel:
    
    @staticmethod
    def create(type: str):
        if type == PIE_CHART:
            model = ChartTypeModel()
            model._id = PIE_CHART_ID
            model.name = PIE_CHART
            return model
        if type == DONUT_CHART:
            model = ChartTypeModel()
            model._id = DONUT_CHART_ID
            model.name = DONUT_CHART 
            return model
        if type == BAR_CHART:
            model = ChartTypeModel()
            model._id = BAR_CHART_ID
            model.name = BAR_CHART
            return model
        if type == LINE_CHART:
            model = ChartTypeModel()
            model._id = LINE_CHART_ID
            model.name = LINE_CHART
            return model
    
        return ChartTypeModel()
    
    