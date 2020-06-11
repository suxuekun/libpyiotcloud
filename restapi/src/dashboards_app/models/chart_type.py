

from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType
from shared.core.model import BaseModel, TimeStampMixin


PIE_CHART = "PIE"
PIE_CHART_ID = 0

DONUT_CHART = "DONUT"
DONUT_CHART_ID = 1

BAR_CHART = "BAR"
BAR_CHART_ID = 2

LINE_CHART = "LINE"
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
    
    