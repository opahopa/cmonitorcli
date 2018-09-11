import logging
import json
import shlex

from subprocess import PIPE, run, CalledProcessError, Popen
from threading import Timer

from models.report import ReportService
from services.system.system_helpers import parse_service_report_stdout, parse_hyperctl_list, parse_memory_usage, parse_fee
from settings.config import WATCH_SERVICES, EXTRA_SERVICES
from services.utils import get_fee
from services.utils import Dict2Obj

logger = logging.getLogger(__name__)

services = WATCH_SERVICES
extra_services = EXTRA_SERVICES


class SystemService(object):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    """"""""""""""""""""""""""""""""""""""""
    don't forget to set shell=True for string command
    timeout bug: https://bugs.python.org/issue30154
    => thread.
    """""""""""""""""""""""""""""""""""""""""
    def run_command(self, command, shell=False, timeout=10):
        process = Popen(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=shell)
        timer = Timer(timeout, process.kill)
        try:
            timer.start()
            result = process.communicate(timeout=timeout)
            # process.wait()

            return Dict2Obj({'stdout': result[0].strip(), 'stderr': result[1]})
        except CalledProcessError as e:
            output = e.output.decode()
            logger.error(output)
            return e
        except Exception as e:
            logger.error(e)
            return e
        finally:
            timer.cancel()

    def get_hostname(self):
        result = self.run_command(['uname', '-n'])
        return result.stdout.strip(), result.stderr

    def get_service_report(self, service_name):
        result = self.run_command(['systemctl', 'status', service_name])
        try:
            active, runtime, last_log, warning, error, installed = parse_service_report_stdout(result)
            return ReportService(active=active, name=service_name, runtime=runtime
                                 , last_log=last_log, warning=warning, error=error, installed=installed)
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
            result['fee'] = get_fee()
        except KeyError as e:
            result['fee'] = None
            logger.error('KeyError: %s' % str(e))
            pass

        logger.info(f"Codius system info: {result}")

        return result

    def report_extra_services(self):
        reports = []
        for s in extra_services:
            reports.append(self.get_service_report(extra_services[s]))

        return reports


if __name__ == "__main__":
    with SystemService() as s:
        print(s.get_service_report('fail2ban').toDict())
