import logging

from subprocess import PIPE, run, CalledProcessError
from models.report import ReportDaemon
from services.system.system_helpers import parse_status_stdout

logger = logging.getLogger(__name__)


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
        active, run_time, last_log = parse_status_stdout(result)
        logger.info(last_log)
        # logger.info(result.returncode)
        # logger.info(result.stdout.strip())
        # logger.info(result.stderr)
        # logger.info(result.check_returncode())

    def report_all(self):
        services = [ 'whoopsie']
        for s in services:
            self.get_service_report(s)

        pass
