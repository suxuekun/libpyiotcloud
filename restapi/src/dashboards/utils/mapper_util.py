

from dashboards.dtos.dashboard_summary_response import DashboardSummaryResponse
import json
from dashboards.dtos.chart_gateway_response import ChartGatewayResponse, DataSetResponse, AttributeResponse, DeviceResponse
from dashboards.models.gateway_attribute import *
from shared.utils.mapper_util import formart_id_with_entity

def map_entity_to_summary_response(entity):
    response = DashboardSummaryResponse()
    response.id = entity["_id"]
    response.name = entity["name"]
    response.color = entity["option"]["color"] if entity["option"] is not None and entity["option"]["color"] is not None else ""
    response.createdAt = entity["createdAt"]
    response.modifiedAt = entity["modifiedAt"]
    return response.to_primitive()


def map_entities_to_summaries_response(entities):
    responses = list(
        map(lambda e: map_entity_to_summary_response(e), entities))
    return responses


def map_attribute_to_attribute_response(attribute):
    response = AttributeResponse()
    response.id = attribute.get("_id")
    response.name = attribute.get("name")
    response.filters = attribute.get("filters")
    return response


def map_chart_gateway_to_response(chartGateway, attributes: []):
    chartResponse = ChartGatewayResponse()
    chartResponse.chartTypeId = chartGateway["chartTypeId"]
    chartResponse.id = chartGateway["_id"]
    chartResponse.device = DeviceResponse({
        "name": chartGateway["device_info"]["devicename"],
        "uuid": chartGateway["device_info"]["deviceid"]
    })
    foundedAttribute = list(
        filter(lambda a: a["_id"] == chartGateway["attributeId"], attributes))[0]
    chartResponse.attribute = map_attribute_to_attribute_response(
        foundedAttribute)

    if chartGateway["attributeId"] == STORAGE_USAGE_ID:
        datasetResponse = DataSetResponse()
        datasetResponse.labels = [
            USED_STORAGE_VALUE, FREE_STORAGE_VALUE
        ]
        datasetResponse.data = [
            60, 50
        ]
        chartResponse.datasets = datasetResponse
        return chartResponse.to_primitive()

    if chartGateway["attributeId"] == ON_OFF_LINE_ID:
        datasetResponse = DataSetResponse()
        datasetResponse.labels = [
            ONLINE_VALUE, OFFLINE_VALUE
        ]
        datasetResponse.data = [
            55, 45
        ]
        chartResponse.datasets = datasetResponse
        return chartResponse.to_primitive()

    if chartGateway["attributeId"] == COUNT_OF_ALERTS_ID:
        datasetResponse = DataSetResponse()
        datasetResponse.labels = [
            SENT_VALUE, REMAINING_VALUE
        ]
        datasetResponse.data = [
            80, 20
        ]
        chartResponse.datasets = datasetResponse
        return chartResponse.to_primitive()
        
    if chartGateway["attributeId"] == BAND_WIDTH_ID:
        datasetResponse = DataSetResponse()
        datasetResponse.labels = [
            SENT_VALUE, REMAINING_VALUE
        ]
        datasetResponse.data = [
            80, 20
        ]
        return chartResponse.to_primitive()
