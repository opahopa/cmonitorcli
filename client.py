import logging
import time

from settings.config import ACC_USERNAME, WEBSOCKET_SERVER
from services.socket_client import WsClient
from services.system.system_service import SystemService
from services.db_service import DbService
from services.utils import rnd_servname
from services.monitor_service import MonitorService

logger = logging.getLogger(__name__)


class CmonitorCli(object):
    def __init__(self):
        self.system = SystemService()
        self.db = DbService()
        self.monitor_service = MonitorService()

        self.hostname = self._get_hostname()

        logger.info("connect to: ws://127.0.0.1:8000/ws/monitor/{}/{}/".format(ACC_USERNAME, self.hostname), )
        self.ws = WsClient("{}/ws/monitor/{}/{}/".format(WEBSOCKET_SERVER, ACC_USERNAME, self.hostname),
                           func_param=self.cron_job, func_onmsg=self.monitor_service.watch_message)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info("Exit")
        self.ws.close()

    def _get_hostname(self):
        os_hostname = self.system.get_hostname()
        if os_hostname is None or os_hostname[0] != 0 or len(os_hostname[1]) == 0:
            hostname = self.db.get_hostname()
            if self.db.get_hostname() is None:
                hostname = rnd_servname(5)
                self.db.write_hostname(hostname)

            return hostname
        else:
            return os_hostname[1]

    def send_status(self):
        self.ws.report("report:init", {'status': 0, "message": "hi"})

    def cron_job(self):
        for i in range(3):
            time.sleep(3)
