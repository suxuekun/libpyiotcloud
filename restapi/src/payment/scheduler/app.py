from payment.scheduler.core import init_scheduler


class IotPaymentSchedulerAPP():
    def __init__(self):
        self._scheduler = init_scheduler()

    @property
    def scheduler(self):
        return self._scheduler