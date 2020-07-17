from payment.routes import payment_blueprint
from payment.scheduler.app import IotPaymentSchedulerAPP


class PaymentApp:
    PREFIX="/payment"
    def __init__(self, app):
        app.register_blueprint(payment_blueprint, url_prefix=self.PREFIX)
        self._schedulerApp = IotPaymentSchedulerAPP()

    @property
    def scheduler(self):
        return self._schedulerApp.scheduler
