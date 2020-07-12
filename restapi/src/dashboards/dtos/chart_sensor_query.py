
from schematics import Model
from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType
from datetime import datetime
from dashboards.exceptions.chart_sensor_query_exception import ChartSensorQueryException

class BaseChartSensorQuery(Model):
    minutes = IntType()
    timestamp = IntType()
    points = IntType()
    isMobile = BooleanType()
    timeSpan = IntType()
    
    def validate(self, partial=False, convert=True, app_data=None, **kwargs):
        super().validate(partial=partial, convert=convert, app_data=app_data, **kwargs)
        if self.points != 30 and self.points != 60:
            raise ChartSensorQueryException("Points should be 30 or 60 points")

class ChartSensorQuery(BaseChartSensorQuery):
    selectedMinutes = ListType(IntType)
    chartsId = ListType(StringType)

    def check_id_in_chartsId(self, chartId: str):
 
        for id in self.chartsId:
            if id == chartId:
                return True
        
        return False

    def validate(self, partial=False, convert=True, app_data=None, **kwargs):
        super().validate(partial=partial, convert=convert, app_data=app_data, **kwargs)
        
        if len(self.selectedMinutes) != len(self.chartsId):
                return ChartSensorQueryException("Sorry selected_minutes & chartsId should be a same size")
    
class ChartComparisonQuery(BaseChartSensorQuery):
    chartsId = ListType(StringType, min_size=2, max_size=3)