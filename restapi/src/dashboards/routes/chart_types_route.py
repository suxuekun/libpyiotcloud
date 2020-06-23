from flask import Blueprint

# Import config mongo
from shared.client.connection.mongo import DefaultMongoConnection
from shared.client.db.mongo.default import DefaultMongoDB

from dashboards.services.chart_type_service import ChartTypeService
from dashboards.repositories.chart_type_repository import ChartTypeRepository

#  Get config mongodb
mongo_client = DefaultMongoDB().conn
db = DefaultMongoDB().db

chartTypeRepository = ChartTypeRepository(mongoclient=mongo_client, db = db, collectionName="chartTypes")

# Init ChartTypeService
chartTypeService = ChartTypeService(chartTypeRepository)
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
