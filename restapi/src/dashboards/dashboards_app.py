



from dashboards.routes.dashboards_route import dashboards_blueprint
from dashboards.routes.chart_types_route import chart_types_blueprint
from dashboards.routes.gateway_attributes_route import gateway_attributes_blueprint
from dashboards.routes.charts_gateway_route import charts_gateway_blueprint
from dashboards.routes.charts_sensor_route import charts_sensor_blueprint

class DashboardsApp:

    def __init__(self, app):
        app.register_blueprint(charts_gateway_blueprint, url_prefix='/dashboards/dashboard/<dashboardId>/gateways')
        app.register_blueprint(charts_sensor_blueprint, url_prefix='/dashboards/dashboard/<dashboardId>/sensors')
        app.register_blueprint(chart_types_blueprint, url_prefix='/dashboards/charts/types')
        app.register_blueprint(gateway_attributes_blueprint, url_prefix='/dashboards/gateway/attributes')
        app.register_blueprint(dashboards_blueprint, url_prefix='/dashboards')
