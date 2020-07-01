from datetime import datetime, timezone, timedelta
from dashboards.dtos.chart_sensor_response import *
import statistics


def setup_empty_int_arrays(size: int):
    arrays = []
    for i in range(size):
        arrays.append(0)
    return arrays


def mapping_sensor_dataset(dataset, timestamp, totalPoint, minutes):

    defaultTimeRangeInSecond = 5
    seconds = minutes * 60
    timeRange = seconds / totalPoint

    timeStart = datetime.fromtimestamp(timestamp) - timedelta(minutes=minutes)
    timeEnd = timeStart + timedelta(seconds=timeRange)

    data = setup_empty_int_arrays(totalPoint)
    low = setup_empty_int_arrays(totalPoint)
    high = setup_empty_int_arrays(totalPoint)
    timeArrays = []
    for index in range(totalPoint):
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


def map_chart_sensor_response(chart, deviceResponse: SensorResponse):

    response = ChartSensorReponse()
    response.id = chart["_id"]
    response.chartTypeId = chart["chartTypeId"]
    response.device = deviceResponse
    return response.to_primitive()


def map_charts_sensor_response(charts, dictSensors: {}, timestamp: int, totalPoint: int, minutes: int):
    response = list(map(lambda chart: map_chart_sensor_response(
        chart, dictSensors[chart["deviceId"]], timestamp, totalPoint, minutes), charts))
    return response


def map_chart_sensor_response(chart, sensor, timestamp: int, totalPoint: int, minutes: int) -> SensorResponse:

    response = ChartSensorReponse()
    response.id = chart["_id"]
    response.chartTypeId = chart["chartTypeId"]

    device = SensorResponse()
    device.id = sensor["_id"]
    device.source = sensor["source"]
    device.number = sensor["number"]
    device.sensorName = sensor["sensorname"]
    device.port = sensor["port"]
    device.name = sensor["name"]
    device.sensorClass = sensor["class"]
    response.device = device

    dataset = mapping_sensor_dataset(
        sensor["dataset"], timestamp, totalPoint, minutes)
    response.dataset = dataset

    readings = sensor["readings"]
    if len(readings):
        readingsResponse = ReadingSensorResponse(
            readings[0]["sensor_readings"])
        response.readings = readingsResponse

    return response.to_primitive()
