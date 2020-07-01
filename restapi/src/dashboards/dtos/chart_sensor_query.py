

class ChartSensorQuery:
    minutes: int
    timestamp: int
    points: int



class ChartComparisonQuery(ChartSensorQuery):
    chartsId: []