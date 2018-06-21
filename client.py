import logging
import time, json

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
        self.hostname = self._get_hostname()
        self.monitor_service = MonitorService(self.hostname)


        logger.info("connect to: ws://127.0.0.1:8000/ws/monitor/{}/{}/".format(ACC_USERNAME, self.hostname), )
        self.wsocket = WsClient("{}/ws/monitor/{}/{}/".format(WEBSOCKET_SERVER, ACC_USERNAME, self.hostname),
                           func_param=self.cron_job, func_onmsg=self.watcher)
        self.wsocket.connect()

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info("Exit")
        self.wsocket.close()

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

    """""
    ws: passed through ws initializer method in socket_client.py
    """""
    def watcher(self, ws, content):
        result_json = self.monitor_service.watch_message(content)
        if result_json is not None:
            ws.send(result_json)
            logger.info("Send resp: {}".format(result_json))

    def cron_job(self):
        for i in range(3):
            time.sleep(3)
