

from dashboards.dtos.dashboard_summary_response import DashboardSummaryResponse
import json
from dashboards.dtos.chart_gateway_response import ChartGatewayResponse, DataSetResponse, AttributeResponse
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
    chartResponse.typeId = chartGateway["typeId"]
    chartResponse.id = chartGateway["_id"]
    chartResponse.deviceName = chartGateway["device_info"]["devicename"]
    chartResponse.deviceUUID = chartGateway["device_info"]["deviceid"]
    
    foundedAttribute = list(
        filter(lambda a: a["_id"] == chartGateway["attributeId"], attributes))[0]
    chartResponse.attribute = map_attribute_to_attribute_response(foundedAttribute)
    
    if chartGateway["attributeId"] == STORAGE_USAGE_ID:
        chartResponse.datasets = [
            DataSetResponse({
                "id": USED_STORAGE_ID,
                "name": USED_STORAGE_VALUE,
                "value": 60
            }),
            DataSetResponse({
                "id": FREE_STORAGE_ID,
                "name": FREE_STORAGE_VALUE,
                "value": 40
            })
        ]
        return chartResponse.to_primitive()

    if chartGateway["attributeId"] == ON_OFF_LINE_ID:
        chartResponse.datasets = [
            DataSetResponse({
                "id": ONLINE_ID,
                "name": ONLINE_VALUE,
                "value": 55
            }),
            DataSetResponse({
                "id": OFFLINE_ID,
                "name": OFFLINE_VALUE,
                "value": 45
            })
        ]
        return chartResponse.to_primitive()

    if chartGateway["attributeId"] == COUNT_OF_ALERTS_ID:
        chartResponse.datasets = [
            DataSetResponse({
                "id": SENT_ID,
                "name": SENT_VALUE,
                "value": 80
            }),
            DataSetResponse({
                "id": REMAINING_ID,
                "name": REMAINING_VALUE,
                "value": 20
            })
        ]
        return chartResponse.to_primitive()
        
    if chartGateway["attributeId"] == BAND_WIDTH_ID:
        chartResponse.datasets = [
            DataSetResponse({
                "id": BAND_WIDTH_STORE_ID,
                "name": BAND_WIDTH,
                "value": 80
            })
        ]
        return chartResponse.to_primitive()