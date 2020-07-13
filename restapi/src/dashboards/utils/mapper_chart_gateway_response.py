

from shared.utils.mapper_util import formart_id_with_entity
from dashboards.dtos.chart_gateway_response import *
from dashboards.models.gateway_attribute import *
from dashboards.dtos.chart_gateway_query import ChartGatewayQuery

def _found_report_with(attributeId: int, gatewayUUID: str, dictReports: {}):

    if attributeId not in dictReports:
        return None

    reportsByGateways = dictReports[attributeId]
    for report in reportsByGateways:
        if report["gatewayUUID"] == gatewayUUID:
            return report

    return None

def map_to_chart_gateway_to_response(chartGateway, dictReports: {}, attributes: [],  query: ChartGatewayQuery):
    if query.isMobile:
        return map_to_chart_gateway_to_mobile_response(chartGateway, dictReports, attributes)

    return map_to_chart_gateway_to_web_response(chartGateway, dictReports, attributes)

def map_to_chart_gateway_to_mobile_response(chartGateway, dictReports: {}, attributes: []):
    chartResponse = MobileChartGatewayExResponse()
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

    report = _found_report_with(
        chartGateway["attributeId"], chartResponse.device.uuid, dictReports)

    if chartGateway["attributeId"] == STORAGE_USAGE_ID:
        used = 0
        free = 0
        if report is not None:
            used = report[USED_STORAGE_VALUE]
            free = report[FREE_STORAGE_VALUE]
        chartResponse.datasetsEx = []
        chartResponse.datasetsEx.append(DatasetExAttributeResponse({
            "values": [
                DatasetExResponse(
                    {
                        "label": USED_STORAGE_VALUE,
                        "data": used
                    }
                ),
                DatasetExResponse(
                    {
                        "label": FREE_STORAGE_VALUE,
                        "data": free
                    }
                )
            ]
        }))
        return chartResponse.to_primitive()

    if chartGateway["attributeId"] == ON_OFF_LINE_ID:
        filters = chartResponse.attribute.filters
        chartResponse.datasetsEx = []
        for item in filters:
            online = 0
            offline = 100
            valueForTime = report[item["name"]]
            if valueForTime is not None:
                online = valueForTime[ONLINE_VALUE]
                offline = valueForTime[OFFLINE_VALUE]
            chartResponse.datasetsEx.append(DatasetExAttributeResponse({
                "filterId": item["id"],
                "filterName": item["name"],
                "values": [
                    DatasetExResponse(
                        {
                            "label": ONLINE_VALUE,
                            "data": online
                        }
                    ),
                    DatasetExResponse(
                        {
                            "label": OFFLINE_VALUE,
                            "data": offline
                        }
                    )
                ]
            }))
        return chartResponse.to_primitive()

    if chartGateway["attributeId"] == COUNT_OF_ALERTS_ID:
        filters = chartResponse.attribute.filters
        chartResponse.datasetsEx = []
        for item in filters:
            sent = 0
            remaining = 100
            valueForTime = report[item["name"]]
            if valueForTime is not None:
                sent = valueForTime[SENT_VALUE]
                remaining = valueForTime[REMAINING_VALUE]

            chartResponse.datasetsEx.append(DatasetExAttributeResponse({
                "filterId": item["id"],
                "filterName": item["name"],
                "values": [
                    DatasetExResponse(
                        {
                            "label": SENT_VALUE,
                            "data": sent
                        }
                    ),
                    DatasetExResponse(
                        {
                            "label": REMAINING_VALUE,
                            "data": remaining
                        }
                    )
                ]
            }))
        return chartResponse.to_primitive()

    if chartGateway["attributeId"] == BAND_WIDTH_ID:
        chartResponse.datasetsEx = []
        chartResponse.datasetsEx.append(DatasetExAttributeResponse({
            "values": [
                DatasetExResponse(
                    {
                        "label": BAND_WIDTH_STORE_VALUE,
                        "data": 80
                    }
                ),
            ]
        }))
        return chartResponse.to_primitive()

def map_to_chart_gateway_to_web_response(chartGateway, dictReports: {}, attributes: []):

    chartResponse = WebChartGatewayExResponse()
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
    report = _found_report_with(
        chartGateway["attributeId"], chartResponse.device.uuid, dictReports)

    if chartGateway["attributeId"] == STORAGE_USAGE_ID:
        used = 0
        free = 0
        if report is not None:
            used = report[USED_STORAGE_VALUE]
            free = report[FREE_STORAGE_VALUE]
        chartResponse.datasets = []
        chartResponse.datasets.append(DatasetAttributeResponse({
            "data": [
                used, free
            ],
            "labels": [
                USED_STORAGE_VALUE, FREE_STORAGE_VALUE
            ]
        }))
        return chartResponse.to_primitive()

    if chartGateway["attributeId"] == ON_OFF_LINE_ID:
        filters = chartResponse.attribute.filters
        chartResponse.datasets = []
        for item in filters:
            online = 0
            offline = 100
            valueForTime = report[item["name"]]
            if valueForTime is not None:
                online = valueForTime[ONLINE_VALUE]
                offline = valueForTime[OFFLINE_VALUE]
            chartResponse.datasets.append(DatasetAttributeResponse({
                "filterId": item["id"],
                "filterName": item["name"],
                "data": [
                    online, offline
                ],
                "labels": [
                    ONLINE_VALUE, OFFLINE_VALUE
                ]
            }))
        return chartResponse.to_primitive()

    if chartGateway["attributeId"] == COUNT_OF_ALERTS_ID:
        filters = chartResponse.attribute.filters

        chartResponse.datasets = []
        for item in filters:
            sent = 0
            remaining = 100

            print(report)
            valueForTime = report[item["name"]]
            print(report)
            if valueForTime is not None:
                sent = valueForTime[SENT_VALUE]
                remaining = valueForTime[REMAINING_VALUE]
            chartResponse.datasets.append(DatasetAttributeResponse({
                "filterId": item["id"],
                "filterName": item["name"],
                "data": [
                    sent, remaining
                ],
                "labels": [
                    SENT_VALUE, REMAINING_VALUE
                ]
            }))
        print(chartResponse.to_primitive())
        return chartResponse.to_primitive()

    if chartGateway["attributeId"] == BAND_WIDTH_ID:
        if chartGateway["attributeId"] == BAND_WIDTH_ID:
            chartResponse.datasets = []
        chartResponse.datasets.append(DatasetAttributeResponse({
            "data": [
                80
            ],
            "labels": [
                BAND_WIDTH_STORE_VALUE
            ]
        }))
        return chartResponse.to_primitive()
    return 0


def map_attribute_to_attribute_response(attribute) -> AttributeResponse:
    response = AttributeResponse()
    response.id = attribute.get("_id")
    response.name = attribute.get("name")
    response.filters = attribute.get("filters")
    return response
