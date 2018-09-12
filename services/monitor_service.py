import logging
import itertools
import os, sys

from models.message import MessageCommands, MessageTypes
from services.system.system_service import SystemService
from services.db_service import DbService
from .message_helpers import parse_message, result_to_json_response, calc_income, bash_cmd_result
from models.response import ResponseStatus
from services.utils import set_fee_in_codiusconf
from settings.config import WEBSOCKET_SERVER
from settings.config import EXTRA_SERVICES

logger = logging.getLogger(__name__)
logging.getLogger('apscheduler.executors.default').setLevel(logging.DEBUG)

if getattr(sys, 'freeze', False):
    bundle_dir = sys._MEIPASS
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

bash_scripts = {
    'upload_test': 'scripts/upload_test.sh',
    'install_fail2ban': 'scripts/install_fail2ban.sh'
}


class MonitorService(object):

    def __init__(self, hostname):
        self.hostname = hostname

    def watch_message(self, content):
        msg = parse_message(content)

        if msg.type is MessageTypes.CONTROL:
            if hasattr(msg, 'hostname') and msg.hostname == self.hostname:
                return self._execute_command_single(msg)
            else:
                return self._execute_command_all(msg)

    def _execute_command_all(self, msg):
        if msg.command is MessageCommands.STATUS_ALL:
            return self.report_status(msg.command)
        if msg.command is MessageCommands.STATS_ALL:
            return result_to_json_response(
                msg.command, ResponseStatus.OK, self.hostname, body=self.stats_n_days(int(msg.body)))

    def _execute_command_single(self, msg):
        if msg.command is MessageCommands.SET_CODIUS_FEE:
            with SystemService() as system_service:
                set_fee_in_codiusconf(msg.body)
                system_service.run_command('systemctl daemon-reload', shell=True)
                system_service.run_command('systemctl restart codiusd', shell=True)
        if msg.command is MessageCommands.SERVICE_RESTART:
            return self.command_wrapper(msg, lambda: self.run_systemctl_command('restart', msg.body, msg.command))
        if msg.command is MessageCommands.SERVICE_STOP:
            return self.command_wrapper(msg, lambda: self.run_systemctl_command('stop', msg.body, msg.command))
        if msg.command is MessageCommands.SERVICE_SPECAIL_DATA:
            return self.command_wrapper(msg, lambda: self.service_special_data(msg))
        if msg.command is MessageCommands.POD_UPLOAD_SELFTEST:
            return self.command_wrapper(msg, lambda: self.run_bash_script(bash_scripts['upload_test']))
        if msg.command is MessageCommands.CMONCLI_UPDATE:
            return self.command_wrapper(msg, lambda: self.update_cmoncli(msg.body))
        if msg.command is MessageCommands.INSTALL_SERVICE:
            return self.command_wrapper(msg, lambda: self.install_service(msg.body))
        return None

    def command_wrapper(self, msg, fcn):
        result = fcn()
        if result['success']:
            return result_to_json_response(msg.command, ResponseStatus.OK, self.hostname, body=result['body'])
        else:
            return result_to_json_response(msg.command, ResponseStatus.ERROR, self.hostname, body=result['body'])

    def report_status(self, msg_command=MessageCommands.STATUS_CLI_UPDATE):
        try:
            with SystemService() as system_service:
                system = system_service.report_system_services()
                codius = system_service.report_codius()
                extra_services = system_service.report_extra_services()
                with DbService() as db_service:
                    codius['income_24'] = 0
                    db_service.write_pods_status(codius)
                    if len(db_service.get_pods_in_n_days(1)) > 0:
                        codius['income_24'], codius['count_24'] = calc_income(db_service.get_pods_in_n_days(1))

                return result_to_json_response(msg_command, ResponseStatus.OK, self.hostname,
                                               report_system=system, report_codius=codius, report_extra_services=extra_services )
        except Exception as e:
            logger.error("Error on command: {} :{}".format(msg_command.name, e))
            return None

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

    def run_systemctl_command(self, command, service_name, command_name):
        try:
            with SystemService() as system_service:
                system_service.run_command(['systemctl', command, service_name])
                return {'success': True}
        except Exception as e:
            logger.error("Error on command: {} :{}".format(command_name.name, e))
            return {'success': False, 'body': e}

    def update_cmoncli(self, path):
        if len(path) > 0:
            command = f'wget https://{WEBSOCKET_SERVER.split("://")[1]}/{path} ' \
                      f'-O cmoncli-install.sh && bash cmoncli-install.sh'
            return self.run_bash_script('', command)
        else:
            return {'success': False, 'body': "invalid installer command"}

    def install_service(self, name):
        if name == 'fail2ban':
            return self.run_bash_script(bash_scripts['install_fail2ban'])


    """"""""""""""""""""""""""""""""""""""""
    :returns
    dictionary:

    :success: boolean
    :body: string
    """""""""""""""""""""""""""""""""""""""""
    def run_bash_script(self, script_path, command=None):
        try:
            with SystemService() as system_service:

                if command is None:
                    command = f"bash {os.path.join(bundle_dir, script_path)}"

                logger.info("Running run_bash_script(), command: {}".format(command))
                result = system_service.run_command(command, shell=True, timeout=45)
                return bash_cmd_result(result)
        except Exception as e:
            logger.error(e)
            return {'success': False, 'body': e}

    def service_special_data(self, msg):
        if msg.body in EXTRA_SERVICES:
            if msg.body is 'fail2ban':
                try:
                    with SystemService() as system_service:
                        result = system_service.run_command('cat /var/log/secure | grep \'Failed password\'', shell=True)
                        return bash_cmd_result(result)
                except Exception as e:
                    logger.error(e)
                    return {'success': False, 'body': e}