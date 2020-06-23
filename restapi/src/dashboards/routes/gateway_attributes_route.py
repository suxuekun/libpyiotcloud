from flask import Blueprint

# Import config mongo
from shared.client.connection.mongo import DefaultMongoConnection
from shared.client.db.mongo.default import DefaultMongoDB

from dashboards.repositories.gateway_attribute_repository import GatewayAttributeRepository
from dashboards.services.gateway_attribute_service import GatewayAttributeService

#  Get config mongodb
mongo_client = DefaultMongoDB().conn
db = DefaultMongoDB().db

attributeRepository = GatewayAttributeRepository(mongoclient=mongo_client, db = db, collectionName="gatewayAttributes")

# Init Dashboard Gateway Attributes services
gatewayAttributeService = GatewayAttributeService(attributeRepository)
gatewayAttributeService.setup_attributes()

# Init routes
gateway_attributes_blueprint = Blueprint('gateway_attributes_blueprint', __name__)

#  Gateways attributes
@gateway_attributes_blueprint.route("/", methods=['GET'])
def get_attributes():
    response = gatewayAttributeService.gets()
    return response