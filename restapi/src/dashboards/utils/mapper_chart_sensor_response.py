from datetime import datetime, timezone, timedelta
from dashboards.dtos.chart_sensor_response import *
from dashboards.dtos.chart_sensor_query import ChartSensorQuery
import statistics


def setup_empty_int_arrays(size: int):
    arrays = []
    for i in range(size):
        arrays.append(0)
    return arrays


def map_to_sensor_dataset(dataset, query: ChartSensorQuery):

    defaultTimeRangeInSecond = 5
    seconds = query.minutes * 60
    timeRange = seconds / query.points

    timeStart = datetime.fromtimestamp(query.timestamp) - timedelta(minutes=query.minutes)
    timeEnd = timeStart + timedelta(seconds=timeRange)

    data = setup_empty_int_arrays(query.points)
    low = setup_empty_int_arrays(query.points)
    high = setup_empty_int_arrays(query.points)
    timeArrays = []
    for index in range(query.points):
        timeArrays.append(int(timeStart.timestamp()))
        pointsValue = find_value_with_timestamp_in_range(
            dataset, int(timeStart.timestamp()), int(timeEnd.timestamp()))
        if len(pointsValue):
            data[index] = round(statistics.mean(pointsValue), 1)
            low[index] = min(pointsValue)
            high[index] = max(pointsValue)

        # Renew plan for timeStart and timeEnd
        timeStart = timeEnd
        timeEnd = timeStart + timedelta(seconds=timeRange)

    dataset = DatasetSensorResponse()
    dataset.data = data
    dataset.low = low
    dataset.high = high
    dataset.labels = timeArrays
    return dataset


def find_value_with_timestamp_in_range(readings, timeStart: int, timeEnd: int):
    values = []
    for reading in readings:
        if reading["timestamp"] >= timeStart and reading["timestamp"] < timeEnd:
            values.append(reading["value"])
        else:
            if reading["timestamp"] > timeEnd:
                return values
    return values

def map_to_charts_sensor_response(charts, dictSensors: {}, query: ChartSensorQuery):
    response = list(map(lambda chart: map_to_chart_sensor_response(
        chart, dictSensors[chart["deviceId"]], query), charts))
    return response

def map_to_chart_sensor_response(chart, sensor, query: ChartSensorQuery) -> SensorResponse:

    response = ChartSensorReponse()
    response.id = chart["_id"]
    response.chartTypeId = chart["chartTypeId"]

    device = SensorResponse()
    device.id = sensor["sensorId"]
    device.source = sensor["source"]
    device.number = sensor["number"]
    device.sensorName = sensor["sensorname"]
    device.port = sensor["port"]
    device.name = sensor["name"]
    device.sensorClass = sensor["class"]
    response.device = device

    dataset = map_to_sensor_dataset(
        sensor["dataset"], query)
    response.dataset = dataset

    sensorReadings = sensor["sensor_readings"]
    readingsResponse = ReadingSensorResponse()
    readingsResponse.value = sensorReadings["value"]
    readingsResponse.highest = sensorReadings["highest"]
    readingsResponse.lowest = sensorReadings["lowest"]
    response.readings = readingsResponse

    return response.to_primitive()
