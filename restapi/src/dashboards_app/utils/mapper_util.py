

from dashboards_app.dtos.dashboard_summary_response import DashboardSummaryResponse
import json
from dashboards_app.dtos.chart_gateway_response import ChartGatewayResponse
from dashboards_app.models.gateway_attribute import STORAGE_USAGE_ID, ON_OFF_LINE_ID, COUNT_OF_ALERTS_ID, USED_STORAGE_VALUE, FREE_STORAGE_VALUE, USED_STORAGE_ID, FREE_STORAGE_ID, ONLINE_ID, OFFLINE_ID, ONLINE_VALUE, OFFLINE_VALUE, SENT_ID, SENT_VALUE, REMAINING_ID, REMAINING_VALUE


def map_entity_to_summary_response(entity):
    response = DashboardSummaryResponse()
    response.id = entity["_id"]
    response.name = entity["name"]
    response.color = entity["option"]["color"] if entity["option"] is not None and entity["option"]["color"] is not None else ""
    response.createdAt = entity["createdAt"]
    response.modifiedAt = entity["modifiedAt"]
    return vars(response)


def map_entities_to_summaries_response(entities):
    responses = list(
        map(lambda e: map_entity_to_summary_response(e), entities))
    return responses


def map_charts_gateway_to_response(chartGateway, attributes: []):
    chartResponse = ChartGatewayResponse()
    chartResponse.userId = chartGateway["userId"]
    chartResponse.dashboardId = chartGateway["dashboardId"]
    chartResponse.typeId = chartGateway["typeId"]
    chartResponse.attribute = list(
        filter(lambda a: a["_id"] == chartGateway["attributeId"], attributes))[0]
    if chartGateway["attributeId"] == STORAGE_USAGE_ID:
        chartResponse.dataset = [
            {
                "id": USED_STORAGE_ID,
                "name": USED_STORAGE_VALUE,
                "value": 60
            },
            {
                "id": FREE_STORAGE_ID,
                "name": FREE_STORAGE_VALUE,
                "value": 40
            }
        ]
        return vars(chartResponse)

    if chartGateway["attributeId"] == ON_OFF_LINE_ID:
        chartResponse.dataset = [
            {
                "id": ONLINE_ID,
                "name": ONLINE_VALUE,
                "value": 55
            },
            {
                "id": OFFLINE_ID,
                "name": OFFLINE_VALUE,
                "value": 45
            }
        ]
        return vars(chartResponse)

    if chartGateway["attributeId"] == COUNT_OF_ALERTS_ID:
        chartResponse.dataset = [
            {
                "id": SENT_ID,
                "name": SENT_VALUE,
                "value": 80
            },
            {
                "id": REMAINING_ID,
                "name": REMAINING_VALUE,
                "value": 20
            }
        ]
        return vars(chartResponse)
