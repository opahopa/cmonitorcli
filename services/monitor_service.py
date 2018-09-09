import logging
import itertools
import traceback


from models.message import MessageCommands, MessageTypes
from services.system.system_service import SystemService
from services.db_service import DbService
from .message_helpers import parse_message, result_to_json_response, calc_income
from models.response import ResponseStatus
from services.utils import set_fee_in_codiusconf
from settings.config import WEBSOCKET_SERVER

logger = logging.getLogger(__name__)
logging.getLogger('apscheduler.executors.default').setLevel(logging.DEBUG)


class MonitorService(object):

    def __init__(self, hostname):
        self.hostname = hostname

    def watch_message(self, content):
        msg = parse_message(content)
        try:
            if msg.type is MessageTypes.CONTROL:
                return self._execute_command(msg)
        except AttributeError:
            return None

    def _execute_command(self, msg):
        if msg.command is MessageCommands.STATUS_ALL:
            try:
                with SystemService() as system_service:
                    system = system_service.report_system_services()
                    codius = system_service.report_codius()
                    return result_to_json_response(msg.command, ResponseStatus.OK, self.hostname
                                                   , report_system=system, report_codius=codius)
            except Exception as e:
                logger.error("Error on command: {} :{}".format(msg.command.name, e))
                return None

        if msg.command is MessageCommands.SET_CODIUS_FEE and msg.hostname == self.hostname:
            with SystemService() as system_service:
                set_fee_in_codiusconf(msg.body)
                system_service.run_command('systemctl daemon-reload', shell=True)
                system_service.run_command('systemctl restart codiusd', shell=True)
        if msg.command is MessageCommands.SERVICE_RESTART and msg.hostname == self.hostname:
            try:
                with SystemService() as system_service:
                    system_service.run_command(['systemctl', 'restart', msg.body])
                    return result_to_json_response(msg.command, ResponseStatus.OK, self.hostname)
            except Exception as e:
                logger.error("Error on command: {} :{}".format(msg.command.name, e))
                return result_to_json_response(msg.command, ResponseStatus.ERROR, self.hostname, body=e)
        if msg.command is MessageCommands.STATS_ALL:
            return result_to_json_response(
                msg.command, ResponseStatus.OK, self.hostname, body=self.stats_n_days(int(msg.body)))
        if msg.command is MessageCommands.POD_UPLOAD_SELFTEST:
            result = self.codiusd_upload_test()
            if result['success']:
                return result_to_json_response(msg.command, ResponseStatus.OK, self.hostname, body=result['body'])
            else:
                return result_to_json_response(msg.command, ResponseStatus.ERROR, self.hostname, body=result['body'])
        if msg.command is MessageCommands.CMONCLI_UPDATE:
            result = self.update_cmoncli(msg.body)
            if result['success']:
                return result_to_json_response(msg.command, ResponseStatus.OK, self.hostname, body=result['body'])
            else:
                return result_to_json_response(msg.command, ResponseStatus.ERROR, self.hostname, body=result['body'])
        return None

    def report_status(self):
        with SystemService() as system_service:
            system = system_service.report_system_services()
            codius = system_service.report_codius()
            with DbService() as db_service:
                codius['income_24'] = 0
                db_service.write_pods_status(codius)
                if len(db_service.get_pods_in_n_days(1)) > 0:
                    codius['income_24'], codius['count_24'] = calc_income(db_service.get_pods_in_n_days(1))

            return result_to_json_response(MessageCommands.STATUS_CLI_UPDATE, ResponseStatus.OK, self.hostname,
                                           report_system=system, report_codius=codius)

    """"""""""""""""""""""""""""""""""""""""
    :returns
    list with dict values

    :datetime: date
    :int: income
    :int: count
    """""""""""""""""""""""""""""""""""""""""
    def stats_n_days(self, n):
        dialy = []

        with DbService() as db_service:
            pods_n_days = db_service.get_pods_in_n_days(n)
            for dt, grp in itertools.groupby(pods_n_days, key=lambda x: x[0].date()):
                tmp = []
                for v in list(grp):
                    tmp.append(v)

                income, count = calc_income(tmp)
                dialy.append({'date': dt, 'income': income, 'count': count})

        return dialy

    def update_cmoncli(self, path):
        if len(path) > 0:
            try:
                with SystemService() as system_service:
                   command = f'wget https://{WEBSOCKET_SERVER.split("://")[1]}/{path} ' \
                             f'-O cmoncli-install.sh && bash cmoncli-install.sh'
                   logger.info(command)
                   result = system_service.run_command(command.strip(), shell=True)
                   return {'success': True, 'body': result.stdout.strip()}
            except Exception as e:
                logger.error(e)
                return {'success': False, 'body': e}
        else:
            return {'success': False, 'body': "invalid installer command"}

    def codiusd_upload_test(self):
        try:
            with SystemService() as system_service:
                result = system_service.run_command("bash scripts/upload_test.sh", shell=True)
            return {'success': True, 'body': result.stdout.strip()}
        except Exception as e:
            logger.error(e)
            return {'success': False, 'body': e}
