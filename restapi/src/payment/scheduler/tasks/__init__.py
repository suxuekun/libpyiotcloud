from payment.scheduler.tasks import daily, monthly

jobs = {}
jobs.update(daily.jobs)
jobs.update(monthly.jobs)