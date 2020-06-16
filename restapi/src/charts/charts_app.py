

from charts.routes.charts_route import charts_blueprint
import flask

class ChartsApp:

    def __init__(self, app):
        app.register_blueprint(charts_blueprint, url_prefix='/charts')