



from dashboards.routes.dashboards_route import dashboards_blueprint
import flask

class DashboardsApp:

    def __init__(self, app):
        app.register_blueprint(dashboards_blueprint, url_prefix='/dashboards')
