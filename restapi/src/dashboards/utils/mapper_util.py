

from dashboards.dtos.dashboard_summary_response import DashboardSummaryResponse
import json

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

