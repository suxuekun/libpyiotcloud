

from shared.utils.mapper_util import formart_id_with_entity
from dashboards.dtos.chart_gateway_response import *
from dashboards.models.gateway_attribute import *
from dashboards.dtos.chart_gateway_query import ChartGatewayQuery


def map_chart_gateway_to_response(chartGateway, attributes: [], query: ChartGatewayQuery):

    if query.isMobile:
        return map_chart_gateway_to_mobile_response(chartGateway, attributes)
    
    return map_chart_gateway_to_web_response(chartGateway, attributes)
   

def map_chart_gateway_to_web_response(chartGateway, attributes: []):
    chartResponse = WebChartGatewayResponse()
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
        datasetResponse = DatasetResponse()
        datasetResponse.labels = [
            USED_STORAGE_VALUE, FREE_STORAGE_VALUE
        ]
        datasetResponse.data = [
            60, 40
        ]
        chartResponse.datasets = datasetResponse
        return chartResponse.to_primitive()

    if chartGateway["attributeId"] == ON_OFF_LINE_ID:
        datasetResponse = DatasetResponse()
        datasetResponse.labels = [
            ONLINE_VALUE, OFFLINE_VALUE
        ]
        datasetResponse.data = [
            55, 45
        ]
        chartResponse.datasets = datasetResponse
        return chartResponse.to_primitive()

    if chartGateway["attributeId"] == COUNT_OF_ALERTS_ID:
        datasetResponse = DatasetResponse()
        datasetResponse.labels = [
            SENT_VALUE, REMAINING_VALUE
        ]
        datasetResponse.data = [
            80, 20
        ]
        chartResponse.datasets = datasetResponse
        return chartResponse.to_primitive()

    if chartGateway["attributeId"] == BAND_WIDTH_ID:
        datasetResponse = DatasetResponse()
        datasetResponse.labels = [BAND_WIDTH_STORE_VALUE]
        datasetResponse.data = [
            80
        ]
        return chartResponse.to_primitive()

def map_chart_gateway_to_mobile_response(chartGateway, attributes: []):
    chartResponse = MobileChartGatewayResponse()
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
        chartResponse.datasetsEx = [
            DatasetExResponse(
                {
                    "label": USED_STORAGE_VALUE,
                    "data": 60
                }
            ),
            DatasetExResponse(
                {
                    "label": FREE_STORAGE_VALUE,
                    "data": 40
                }
            )
        ]
        return chartResponse.to_primitive()

    if chartGateway["attributeId"] == ON_OFF_LINE_ID:
        chartResponse.datasetsEx = [
            DatasetExResponse(
                {
                    "label": ONLINE_VALUE,
                    "data": 55
                }
            ),
            DatasetExResponse(
                {
                    "label": OFFLINE_VALUE,
                    "data": 45
                }
            )
        ]
        return chartResponse.to_primitive()

    if chartGateway["attributeId"] == COUNT_OF_ALERTS_ID:
        chartResponse.datasetsEx = [
            DatasetExResponse(
                {
                    "label": SENT_VALUE,
                    "data": 80
                }
            ),
            DatasetExResponse(
                {
                    "label": REMAINING_VALUE,
                    "data": 20
                }
            )
        ]
        return chartResponse.to_primitive()

    if chartGateway["attributeId"] == BAND_WIDTH_ID:
        chartResponse.datasetsEx = [
            DatasetExResponse(
                {
                    "label": BAND_WIDTH_STORE_VALUE,
                    "data": 80
                }
            ),
        ]

        return chartResponse.to_primitive()


def map_chart_gateway_to_ex_response(chartGateway, attributes: [],  query: ChartGatewayQuery):
    
    if query.isMobile:
        return map_chart_gateway_to_ex_mobile_response(chartGateway, attributes)

    return map_chart_gateway_to_ex_web_response(chartGateway, attributes)

def map_chart_gateway_to_ex_web_response(chartGateway, attributes: []):
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
    if chartGateway["attributeId"] == STORAGE_USAGE_ID:
        chartResponse.datasets = []
        chartResponse.datasets.append(DatasetAttributeResponse({
            "data": [
                60, 40
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
            chartResponse.datasets.append(DatasetAttributeResponse({
                "filterId": item["id"],
                "filterName": item["name"],
                "data": [
                    55, 45
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
            chartResponse.datasets.append(DatasetAttributeResponse({
                "filterId": item["id"],
                "filterName": item["name"],
                "data": [
                    35, 65
                ],
                "labels": [
                    SENT_VALUE, REMAINING_VALUE
                ]
            }))
        return chartResponse.to_primitive()

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


def map_chart_gateway_to_ex_mobile_response(chartGateway, attributes: []):
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
    if chartGateway["attributeId"] == STORAGE_USAGE_ID:
        chartResponse.datasetsEx = []
        chartResponse.datasetsEx.append(DatasetExAttributeResponse({
            "values": [
                DatasetExResponse(
                    {
                        "label": USED_STORAGE_VALUE,
                        "data": 60
                    }
                ),
                DatasetExResponse(
                    {
                        "label": FREE_STORAGE_VALUE,
                        "data": 40
                    }
                )
            ]
        }))
        return chartResponse.to_primitive()

    if chartGateway["attributeId"] == ON_OFF_LINE_ID:
        filters = chartResponse.attribute.filters
        chartResponse.datasetsEx = []
        for item in filters:
            chartResponse.datasetsEx.append(DatasetExAttributeResponse({
                "filterId": item["id"],
                "filterName": item["name"],
                "values": [
                    DatasetExResponse(
                        {
                            "label": ONLINE_VALUE,
                            "data": 55
                        }
                    ),
                    DatasetExResponse(
                        {
                            "label": OFFLINE_VALUE,
                            "data": 45
                        }
                    )
                ]
            }))
        return chartResponse.to_primitive()

    if chartGateway["attributeId"] == COUNT_OF_ALERTS_ID:
        filters = chartResponse.attribute.filters
        chartResponse.datasetsEx = []
        for item in filters:
            chartResponse.datasetsEx.append(DatasetExAttributeResponse({
                "filterId": item["id"],
                "filterName": item["name"],
                "values": [
                    DatasetExResponse(
                        {
                            "label": SENT_VALUE,
                            "data": 35
                        }
                    ),
                    DatasetExResponse(
                        {
                            "label": REMAINING_VALUE,
                            "data": 65
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


def map_attribute_to_attribute_response(attribute) -> AttributeResponse:
    response = AttributeResponse()
    response.id = attribute.get("_id")
    response.name = attribute.get("name")
    response.filters = attribute.get("filters")
    return response
