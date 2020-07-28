from payment.scheduler.tasks.jobs.subscription_payment import update_subscriptions_payment
from shared.utils import timestamp_util

@timestamp_util.timing
def daily_jobs():
    # daily jobs here
    update_subscriptions_payment()

jobs = {
    'daily_scheduler':{
        'task':daily_jobs,
        'type':'cron',
        #normal config
        'kwargs':{
            'month':'*',
            'day':'*',
            'hour':'2',
            'minute':'0',
        }
        #test config
        # 'kwargs':{
        #     'month':'*',
        #     'day':'*',
        #     'hour':'22',
        #     'minute':"51",
        # }
    }
}