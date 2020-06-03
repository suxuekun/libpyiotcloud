

from dashboards_app.routes.dashboards_route import dashboards_blueprint, bootstrap
import flask

class DashboardsApp:


    def __init__(self, app):
        app.register_blueprint(dashboards_blueprint, url_prefix='/dashboards')


    def build(self):
        bootstrap()

