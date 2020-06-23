



from dashboards.routes.dashboards_route import dashboards_blueprint
from dashboards.routes.chart_types_route import chart_types_blueprint
from dashboards.routes.gateway_attributes_route import gateway_attributes_blueprint
from dashboards.routes.charts_gateways_route import charts_gateways_blueprint
import flask

class DashboardsApp:

    def __init__(self, app):
        app.register_blueprint(dashboards_blueprint, url_prefix='/dashboards')
        app.register_blueprint(chart_types_blueprint, url_prefix='/dashboards/charts/types')
        app.register_blueprint(gateway_attributes_blueprint, url_prefix='/dashboards/gateway/attributes')
        
