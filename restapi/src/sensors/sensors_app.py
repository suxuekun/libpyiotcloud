

from sensors.routes.sensors_route import sensors_blueprint

class SensorsApp:

    def __init__(self, app):
        app.register_blueprint(sensors_blueprint, url_prefix='/gateways/<gatewayId>/sensors')
