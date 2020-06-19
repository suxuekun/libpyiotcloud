
import json
from charts.dtos.chart_gateway_response import ChartGatewayResponse
from charts.models.gateway_attribute import STORAGE_USAGE_ID, ON_OFF_LINE_ID, COUNT_OF_ALERTS_ID, USED_STORAGE_VALUE, FREE_STORAGE_VALUE, USED_STORAGE_ID, FREE_STORAGE_ID, ONLINE_ID, OFFLINE_ID, ONLINE_VALUE, OFFLINE_VALUE, SENT_ID, SENT_VALUE, REMAINING_ID, REMAINING_VALUE
from shared.utils.mapper_util import formart_id_with_entity


def map_chart_gateway_to_response(chartGateway, attributes: []):
    chartResponse = ChartGatewayResponse()
    chartResponse.userId = chartGateway["userId"]
    chartResponse.dashboardId = chartGateway["dashboardId"]
    chartResponse.typeId = chartGateway["typeId"]
    chartResponse.id = chartGateway["_id"]
    chartResponse.deviceName = chartGateway["device_info"]["devicename"]
    chartResponse.deviceUUID = chartGateway["device_info"]["deviceid"]
    chartResponse.attribute = list(
        filter(lambda a: a["_id"] == chartGateway["attributeId"], attributes))[0]
    
    chartResponse.attribute = formart_id_with_entity(chartResponse.attribute)
    if chartGateway["attributeId"] == STORAGE_USAGE_ID:
        chartResponse.datasets = [
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
        chartResponse.datasets = [
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
        chartResponse.datasets = [
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
