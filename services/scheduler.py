import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers import SchedulerAlreadyRunningError
from apscheduler.triggers import interval
from apscheduler.jobstores.base import JobLookupError
from services.db_service import DbService

logger = logging.getLogger(__name__)
logging.getLogger('apscheduler.executors').setLevel(logging.DEBUG)
logging.getLogger('apscheduler.executors.default').propagate = False
scheduler = BackgroundScheduler()


class SchedulerService(object):

    def __init__(self):
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
            scheduler.remove_job('cmoncli_update_job')
        except JobLookupError:
            pass

    """""
    to be called in socket_client. ws & func passed on 'onopen' event
    """""
    def add_update_job(self, ws, job_func0, job_func1):
        trigger0 = interval.IntervalTrigger(seconds=3)
        scheduler.add_job(lambda: job_func0(ws), trigger=trigger0, id='status_update_job', replace_existing=True)

        trigger1 = interval.IntervalTrigger(minutes=15)
        scheduler.add_job(lambda: job_func1(ws), trigger=trigger1, id='cmoncli_update_job', replace_existing=True)
        pass

    def add_db_cleanup_task(self):
        trigger = interval.IntervalTrigger(hours=1)
        scheduler.add_job(lambda: self.cleanup_db_check, trigger=trigger, id='cmoncli_db_cleanup_job', replace_existing=True)

    def cleanup_db_check(self):
        with DbService() as db_service:
            db_service.cleanup_old_records(180)
