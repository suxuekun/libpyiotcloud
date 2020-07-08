from webhook.route import webhook_blueprint
class WebHookApp():
    PREFIX = "/webhook"
    def __init__(self, app):
        print('reg')
        app.register_blueprint(webhook_blueprint, url_prefix=self.PREFIX)

