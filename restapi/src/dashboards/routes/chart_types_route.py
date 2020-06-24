from flask import Blueprint
from dashboards.ioc import init_chart_type_service

chartTypeService = init_chart_type_service()
chartTypeService.setup_chart_types()

# Init routes
chart_types_blueprint = Blueprint('chart_types_blueprint', __name__)

#  Chart Types
@chart_types_blueprint.route("/gateway", methods=['GET'])
def get_charrts_types_for_gateway():
    response = chartTypeService.gets_for_gateway()
    return response

@chart_types_blueprint.route("/sensor", methods=['GET'])
def get_charts_tyoes_for_sensor():
    response = chartTypeService.gets_for_sensor()
    return response
