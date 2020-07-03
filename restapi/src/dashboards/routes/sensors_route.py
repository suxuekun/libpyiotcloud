
from flask import Blueprint, request

from dashboards.ioc import init_sensor_repository
from shared.core.response import Response

# Import middleware and Auth
from shared.middlewares.default_middleware import default_middleware
from shared.middlewares.request.permission.login import login_required
from shared.utils.mapper_util import formart_id_with_entitites


sensorRepository = init_sensor_repository()

sensors_blueprint = Blueprint('sensors_blueprint', __name__)


@sensors_blueprint.route("", methods=['GET'])
@default_middleware
@login_required()
def gets(gatewayId: str):
    query = {
        "deviceid": gatewayId
    }
    results = sensorRepository.gets(query)
    formart_id_with_entitites(results)
    return Response.success(data=results, message="Get sensors successfully")

    



