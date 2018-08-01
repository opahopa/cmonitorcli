import logging
import json
import os

from subprocess import PIPE, run, CalledProcessError
from models.report import ReportService
from services.system.system_helpers import parse_service_report_stdout, parse_hyperctl_list, parse_memory_usage, parse_fee
from settings.config import WATCH_SERVICES

logger = logging.getLogger(__name__)

services = WATCH_SERVICES


class SystemService(object):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def run_command(self, command, shell=False):
        try:
            return run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, timeout=20, shell=shell)
        except CalledProcessError as e:
            output = e.output.decode()
            logger.error(output)

    def get_hostname(self):
        result = self.run_command(['uname', '-n'])
        return result.returncode, result.stdout.strip(), result.stderr, result.check_returncode

    def get_service_report(self, service_name):
        result = self.run_command(['systemctl', 'status', service_name])
        try:
            active, runtime, last_log, warning = parse_service_report_stdout(result)
            return ReportService(active=active, name=service_name, runtime=runtime, last_log=last_log, warning=warning)
        except Exception as e:
            logger.error(e)
            logger.error(result.stderr)

    def report_system_services(self):
        reports = []
        for s in services:
            reports.append(self.get_service_report(services[s]))

        # for k, v in reports.items():
        #     logger.info("{}:{}".format(k, pprint.pprint(v.toDict())))

        return reports

    def report_codius(self):
        result = {
            'version': '',
            'pods': [],
            'memory': {},
            'fee': 0
        }

        try:
            version = json.loads(self.run_command(['curl', '127.0.0.1:3000/version']).stdout.strip())['version']
            result['version'] = version
        except Exception as e:
            result['version'] = None
            logger.error(e)
            pass
        try:
            pods = parse_hyperctl_list(self.run_command(['hyperctl', 'list']))
            result['pods'] = pods
        except Exception as e:
            result['pods'] = []
            logger.error(e)
            pass

        try:
            memory = parse_memory_usage(self.run_command(['free', '-m']))
            result['memory'] = memory
        except Exception as e:
            result['memory'] = None
            logger.error(e)
            pass

        try:
            result['fee'] = parse_fee(self.run_command('echo $CODIUS_COST_PER_MONTH', shell=True))
        except KeyError as e:
            result['fee'] = None
            logger.error('KeyError: %s' % str(e))
            pass

        logger.info(f"Codius system info: {result}")

        return result
