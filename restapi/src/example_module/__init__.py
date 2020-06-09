from payment.routes import payment_blueprint
class PaymentApp:
    PREFIX="/example"
    def __init__(self, app):
        app.register_blueprint(payment_blueprint, url_prefix=self.PREFIX)

