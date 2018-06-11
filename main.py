from services.socket_client import WsClient
from services.system_service import SystemService
from services.db_service import DbService
from services.utils import rnd_servname



class CmonitorCli(object):
    def __init__(self):
        self.system = SystemService()
        self.db = DbService()

        self.hostname = self.get_hostname()
        print(self.hostname)


        # self.ws = WsClient("wss://127.0.0.1:8000/ws/monitor/username/server0/")
        # self.ws.close()

    def get_hostname(self):
        os_hostname = self.system.get_hostname()
        if os_hostname is None or os_hostname[0] != 0 or len(os_hostname[1]) == 0:
            hostname = self.db.get_hostname()
            if self.db.get_hostname() is None:
                hostname = rnd_servname(5)
                self.db.write_hostname(hostname)

            return hostname
        else:
            return os_hostname[1]


def main_job():
    cclient = CmonitorCli()
    # ws = WsClient("wss://127.0.0.1:8000/ws/monitor/username/server0/")
    # ws.close()
    pass


if __name__ == '__main__':
    main_job()