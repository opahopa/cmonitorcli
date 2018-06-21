import logging
import pprint

from subprocess import PIPE, run, CalledProcessError
from models.report import ReportService
from services.system.system_helpers import parse_status_stdout
from settings.config import WATCH_SERVICES

logger = logging.getLogger(__name__)

services = WATCH_SERVICES
services = {
    'whoopsie': "whoopsie",
    'winbind': "winbind",
    'umountfs': "umountfs",
    'hostapd': "hostapd"
}


class SystemService(object):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _run_command(self, command):
        try:
            return run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, timeout=20)
        except CalledProcessError as e:
            output = e.output.decode()
            logger.error(output)

    def get_hostname(self):
        result = self._run_command(['uname', '-n'])
        return result.returncode, result.stdout.strip(), result.stderr, result.check_returncode

    def get_service_report(self, service_name):
        result = self._run_command(['systemctl', 'status', service_name])
        try:
            active, runtime, last_log, warning = parse_status_stdout(result)
            return ReportService(active=active, name=service_name, runtime=runtime, last_log=last_log, warning=warning)
        except Exception as e:
            logger.error(e)
            logger.error(result.stderr)

    def report_all(self):
        reports = []
        for s in services:
            reports.append(self.get_service_report(s))

        # for k, v in reports.items():
        #     logger.info("{}:{}".format(k, pprint.pprint(v.toDict())))

        return reports
