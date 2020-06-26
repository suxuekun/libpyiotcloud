from flask import Blueprint

from dashboards.ioc import init_gateway_attribute_service

# Init Dashboard Gateway Attributes services
gatewayAttributeService = init_gateway_attribute_service()
gatewayAttributeService.setup_attributes()

# Init routes
gateway_attributes_blueprint = Blueprint('gateway_attributes_blueprint', __name__)

#  Gateways attributes
@gateway_attributes_blueprint.route("/", methods=['GET'])
def get_attributes():
    response = gatewayAttributeService.gets()
    return response