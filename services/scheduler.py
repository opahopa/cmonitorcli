import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers import SchedulerAlreadyRunningError
from apscheduler.jobstores.base import JobLookupError

logger = logging.getLogger(__name__)
logging.getLogger('apscheduler.executors').setLevel(logging.DEBUG)
logging.getLogger('apscheduler.executors.default').propagate = False
scheduler = BackgroundScheduler()


class SchedulerService(object):

    def __init__(self, job_func):
        self.job_func = job_func
        pass

    def run_scheduler(self):
        try:
            scheduler.start()
        except SchedulerAlreadyRunningError:
            logger.error("SchedulerAlreadyRunningError")
            pass

    def delete_update_job(self):
        try:
            scheduler.remove_job('status_update_job')
        except JobLookupError:
            pass

    """""
    to be called in socket_client. ws & func passed on 'onopen' event
    """""
    def add_update_job(self, ws, job_func):
        scheduler.add_job(lambda: job_func(ws), 'interval', seconds=3, id='status_update_job', replace_existing=True)
        pass
