from datetime import datetime, timezone, timedelta
from dashboards.dtos.chart_sensor_response import *
from dashboards.dtos.chart_sensor_query import ChartSensorQuery
import statistics


def setup_empty_int_arrays(size: int):
    arrays = []
    for i in range(size):
        arrays.append(0)
    return arrays


def setup_empty_mobile_dataset_sensor_response(size: int):
    arrays = []
    for i in range(size):
        item = MobileDatasetSensorResponse()
        item.x = 0
        item.y = 0
        item.low = 0
        item.y = 0
        arrays.append(item)
    return arrays


def map_to_sensor_dataset_mobile(dataset, query: ChartSensorQuery, customMinutes: int = 0):

    defaultTimeRangeInSecond = 5
    minutes = query.minutes
    if customMinutes != 0:
        minutes = customMinutes

    seconds = query.minutes * 60
    timeRange = seconds / query.points
    timeStart = datetime.fromtimestamp(
        query.timestamp) - timedelta(minutes=minutes)
    timeEnd = timeStart + timedelta(seconds=timeRange)

    datasetResponse = []
    for index in range(query.points):

        item = MobileDatasetSensorResponse()
        item.x = int(timeStart.timestamp())
        pointsValue = find_value_with_timestamp_in_range(
            dataset, int(timeStart.timestamp()), int(timeEnd.timestamp()))

        if len(pointsValue) > 0:
            if minutes == 5:
                data[index] = get_value_when_minutues_is_five(pointsValue)
                low[index] = 0
                high[index] = 0
            else:
                data[index] = round(statistics.mean(pointsValue), 2)
                low[index] = min(pointsValue)
                high[index] = max(pointsValue)
        else:
            item.y = 0
            item.low = 0
            item.high = 0

        # Renew plan for timeStart and timeEnd
        timeStart = timeEnd
        timeEnd = timeStart + timedelta(seconds=timeRange)
        datasetResponse.append(item)

    return datasetResponse

def map_to_sensor_dataset(dataset, query: ChartSensorQuery, customMinutes: int = 0):

    defaultTimeRangeInSecond = 5

    minutes = query.minutes
    if customMinutes != 0:
        minutes = customMinutes

    seconds = minutes * 60
    timeRange = seconds / query.points
    timeStart = datetime.fromtimestamp(
        query.timestamp) - timedelta(minutes=minutes)
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
            if minutes == 5:
                data[index] = get_value_when_minutues_is_five(pointsValue)
                low[index] = 0
                high[index] = 0
            else:
                data[index] = round(statistics.mean(pointsValue), 2)
                low[index] = min(pointsValue)
                high[index] = max(pointsValue)

        # Renew plan for timeStart and timeEnd
        timeStart = timeEnd
        timeEnd = timeStart + timedelta(seconds=timeRange)

    datasetResponse = DatasetSensorResponse()
    datasetResponse.data = data
    datasetResponse.low = low
    datasetResponse.high = high
    datasetResponse.labels = timeArrays
    return datasetResponse

def find_value_with_timestamp_in_range(readings, timeStart: int, timeEnd: int):
    values = []
    for reading in readings:
        if reading["timestamp"] >= timeStart and reading["timestamp"] <= timeEnd:
            values.append(reading["value"])
        else:
            if reading["timestamp"] > timeEnd:
                return values
    return values


def get_value_when_minutues_is_five(values: []):

    if len(values) == 0:
        return 0

    # It'mean time range is 10 seconds has 2 value, we will get lastest value
    if len(values) == 2:
        return values[1]

    return values[0]


def map_to_charts_sensor_response(charts, dictSensors: {}, query: ChartSensorQuery):
    response = list(map(lambda chart: map_to_chart_sensor_response(
        chart, dictSensors.get(chart.get("deviceId")), query), charts))
    return response


def map_to_chart_sensor_response(chart, sensor, query: ChartSensorQuery, customMinutes: int = 0) -> SensorResponse:

    device = SensorResponse()
    device.id = sensor["sensorId"]
    device.source = sensor["source"]
    device.number = sensor["number"]
    device.sensorName = sensor["sensorname"]
    device.port = sensor["port"]
    device.name = sensor["name"]
    device.sensorClass = sensor["class"]
    device.gatewayUUID = sensor["gatewayUUID"]

    sensorReadings = sensor["sensor_readings"]
    readingsResponse = ReadingSensorResponse()
    if sensor["sensor_readings"] is not None:
        readingsResponse.value = sensorReadings["value"]
        readingsResponse.highest = sensorReadings["highest"]
        readingsResponse.lowest = sensorReadings["lowest"]
    else:
        readingsResponse.value = 0
        readingsResponse.highest = 0
        readingsResponse.lowest = 0

    # Minutes
    minutes = query.minutes
    if customMinutes != 0:
        minutes = customMinutes

    if query.isMobile:
        mobileResponse = MobileChartSensorResponse()
        mobileResponse.selectedMinutes = minutes
        mobileResponse.id = chart["_id"]
        mobileResponse.chartTypeId = chart["chartTypeId"]
        mobileResponse.device = device
        mobileResponse.readings = readingsResponse
        mobileResponse.datasetsEx = []
        if sensor["dataset"] is not None:
            mobileResponse.datasetsEx = (
                map_to_sensor_dataset_mobile(sensor["dataset"], query, minutes))

        return mobileResponse.to_primitive()

    response = WebChartSensorResponse()
    response.id = chart["_id"]
    response.chartTypeId = chart["chartTypeId"]
    response.device = device
    response.readings = readingsResponse
    response.selectedMinutes = minutes

    dataset = DatasetSensorResponse()
    if sensor["dataset"] is not None:
        dataset = map_to_sensor_dataset(
            sensor["dataset"], query, customMinutes=minutes)

    response.dataset = dataset

    return response.to_primitive()
