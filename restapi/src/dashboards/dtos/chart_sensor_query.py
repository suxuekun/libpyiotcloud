
from schematics import Model
from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType
from datetime import datetime
from dashboards.exceptions.chart_sensor_query_exception import ChartSensorQueryException

RULE_OF_MININUTES = [5, 10, 15, 30, 60, 1440, 10080]

def check_list_minutes_in_rule(listMinutes):
    for minutes in listMinutes:
        if check_minutes_in_rule(minutes) == False:
            return False
    return True

def check_minutes_in_rule(minutes):
    for i in RULE_OF_MININUTES:
        if i == minutes:
            return True
    return False

class BaseChartSensorQuery(Model):

    minutes = IntType()
    timestamp = IntType()
    points = IntType()
    isMobile = BooleanType()
    timeSpan = IntType()
    isRealtime = BooleanType()

    def validate(self, partial=False, convert=True, app_data=None, **kwargs):
        super().validate(partial=partial, convert=convert, app_data=app_data, **kwargs)
        if self.points != 30 and self.points != 60:
            raise ChartSensorQueryException("Points should be 30 or 60 points")

        if check_minutes_in_rule(self.minutes) == False:
            raise ChartSensorQueryException("Minutes should be in 5, 15, 30, 60, 1440, 10080")

        if self.timeSpan < 1 or self.timeSpan > 3:
            raise ChartSensorQueryException(
                "Time span just only support in 1 to 3")


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
            raise ChartSensorQueryException(
                "Sorry selected_minutes & chartsId should be a same size")

        if len(self.selectedMinutes) > 0 and check_list_minutes_in_rule(self.selectedMinutes) == False:
            raise ChartSensorQueryException("Selected Minutes should be in 5, 15, 30, 60, 1440, 10080")
        
class ChartComparisonQuery(BaseChartSensorQuery):
    chartsId = ListType(StringType, min_size=2, max_size=3)

    def validate(self, partial=False, convert=True, app_data=None, **kwargs):
        super().validate(partial=partial, convert=convert, app_data=app_data, **kwargs)
