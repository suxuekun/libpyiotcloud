

from dashboards.dtos.dashboard_summary_response import DashboardSummaryResponse
import json
from dashboards.dtos.chart_gateway_response import *
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
        datasetResponse = DatasetResponse()
        datasetResponse.labels = [
            USED_STORAGE_VALUE, FREE_STORAGE_VALUE
        ]
        datasetResponse.data = [
            60, 40
        ]
        chartResponse.datasets = datasetResponse
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
        datasetResponse = DatasetResponse()
        datasetResponse.labels = [
            ONLINE_VALUE, OFFLINE_VALUE
        ]
        datasetResponse.data = [
            55, 45
        ]
        chartResponse.datasets = datasetResponse
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
        datasetResponse = DatasetResponse()
        datasetResponse.labels = [
            SENT_VALUE, REMAINING_VALUE
        ]
        datasetResponse.data = [
            80, 20
        ]
        chartResponse.datasets = datasetResponse
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
        datasetResponse = DatasetResponse()
        datasetResponse.labels = [BAND_WIDTH_STORE_VALUE]
        datasetResponse.data = [
            80
        ]

        chartResponse.datasetsEx = [
            DatasetExResponse(
                {
                    "label": BAND_WIDTH_STORE_VALUE,
                    "data": 80
                }
            ),
        ]

        return chartResponse.to_primitive()


def map_chart_gateway_to_ex_response(chartGateway, attributes: []):
    chartResponse = ChartGatewayExResponse()
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
        chartResponse.datasetsEx = []
        chartResponse.datasets.append(DatasetAttributeResponse({
            "data": [
                60, 40
            ],
            "labels": [
                USED_STORAGE_VALUE, FREE_STORAGE_VALUE
            ]
        }))
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
        chartResponse.datasets = []
        chartResponse.datasetsEx = []
        print("Con me may")
        print(filters)
        for item in filters:
            print("Fukcing")
            print(item)
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
        chartResponse.datasets = []
        chartResponse.datasetsEx = []
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
        chartResponse.datasets = []
        chartResponse.datasetsEx = []
        chartResponse.datasets.append(DatasetAttributeResponse({
            "data": [
                80
            ],
            "labels": [
                BAND_WIDTH_STORE_VALUE
            ]
        }))
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
