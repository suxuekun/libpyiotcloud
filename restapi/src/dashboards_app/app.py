

from dashboards_app.routes.dashboards_route import dashboards_blueprint
import flask

class DashboardsApp:

    def build(self, app):
        app.register_blueprint(dashboards_blueprint, url_prefix='/dashboards')

