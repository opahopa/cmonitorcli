import logging
import itertools
import version

from datetime import datetime
from models.message import MessageCommands, MessageTypes
from services.system.system_service import SystemService
from services.db_service import DbService
from .message_helpers import parse_message, result_to_json_response, calc_income
from models.response import ResponseStatus
from services.monitor_functions import run_bash_script, bash_cmd_result, set_codiusd_fee, set_codiusd_variables,\
    hyperd_rm_pods
from settings.config import REST_SERVER, EXTRA_SERVICES, DISTRIB
from services.cli_tools import generate_cmoncli, cli_update_request

logger = logging.getLogger(__name__)
logging.getLogger('apscheduler.executors.default').setLevel(logging.DEBUG)

bash_scripts = {
    'upload_test': 'scripts/upload_test.sh',
    'install_fail2ban': 'scripts/install_fail2ban.sh',
    'cleanup_hyperd': 'scripts/cleanup_hyperd.sh'
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
            msg_upd = cli_update_request(self.hostname)
            if msg_upd is not None:
                return result_to_json_response(msg_upd['command'], ResponseStatus.OK, self.hostname)
            return self.report_status(msg.command)
        if msg.command is MessageCommands.STATS_ALL:
            return result_to_json_response(
                msg.command, ResponseStatus.OK, self.hostname, body=self.stats_n_days(int(msg.body)))

    def _execute_command_single(self, msg):
        if msg.command is MessageCommands.SET_CODIUS_FEE:
            return self.command_wrapper(msg, lambda: set_codiusd_fee(msg.body))
        if msg.command is MessageCommands.SERVICE_RESTART:
            return self.command_wrapper(msg, lambda: self.run_systemctl_command('restart', msg.body, msg.command))
        if msg.command is MessageCommands.SERVICE_STOP:
            return self.command_wrapper(msg, lambda: self.run_systemctl_command('stop', msg.body, msg.command))
        if msg.command is MessageCommands.SERVICE_START:
            return self.command_wrapper(msg, lambda: self.run_systemctl_command('start', msg.body, msg.command))
        if msg.command is MessageCommands.STATS_SYSTEM:
            return self.command_wrapper(msg, lambda: self.system_stats(msg.body))
        if msg.command is MessageCommands.SERVICE_SPECAIL_DATA:
            return self.command_wrapper(msg, lambda: self.service_special_data(msg))
        if msg.command is MessageCommands.POD_UPLOAD_SELFTEST:
            return self.command_wrapper(msg, lambda: run_bash_script(bash_scripts['upload_test'], cmd_args=[msg.body['duration']], timeout=70))
        if msg.command is MessageCommands.INSTALL_SERVICE:
            return self.command_wrapper(msg, lambda: self.install_service(msg.body))
        if msg.command is MessageCommands.UNINSTALL_SERVICE:
            return self.command_wrapper(msg, lambda: self.uninstall_service(msg.body))
        if msg.command is MessageCommands.CLI_UPGRADE:
            return self.command_wrapper(msg, lambda: self.cmoncli_autoupgrade(msg.body))
        if msg.command is MessageCommands.SET_CODIUSD_VARIABLES:
            return self.command_wrapper(msg, lambda: set_codiusd_variables(msg.body))
        if msg.command is MessageCommands.EXTRA_NETSTAT:
            return self.command_wrapper(msg, lambda: self.service_special_data(msg))
        if msg.command is MessageCommands.CLEANUP_HYPERD:
            return self.command_wrapper(msg, lambda: run_bash_script(bash_scripts['cleanup_hyperd'], timeout=45))
        if msg.command is MessageCommands.HYPERD_RM_POD:
            return self.command_wrapper(msg, lambda: hyperd_rm_pods(msg.body))
        return None

    def command_wrapper(self, msg, fcn):
        result = fcn()
        if not 'body' in result:
            result['body'] = 'success'
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
                    db_service.write_status(codius, system)
                    if len(db_service.get_codiusd_in_n_days(1)) > 0:
                        codius['income_24'], codius['count_24'] = calc_income(db_service.get_codiusd_in_n_days(1))

                return result_to_json_response(msg_command, ResponseStatus.OK, self.hostname,
                                               report_system=system, report_codius=codius,
                                               report_extra_services=extra_services)
        except Exception as e:
            logger.error("Error on command: {} :{}".format(msg_command.name, e))
            return result_to_json_response(msg_command, ResponseStatus.ERROR, self.hostname, body=e)

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
            pods_n_days = db_service.get_codiusd_in_n_days(n)
            for dt, grp in itertools.groupby(pods_n_days, key=lambda x: x[0].date()):
                tmp = []
                for v in list(grp):
                    tmp.append(v)

                income, count = calc_income(tmp)
                dialy.append({'date': dt, 'income': income, 'count': count})

        return dialy

    def system_stats(self, body):
        result = []

        try:
            with DbService() as db_service:
                services_status_log = db_service.get_system_in_n_days(int(body['days']))
                if body['days'] == 1:
                    for hr_minute, grp in itertools.groupby(services_status_log, lambda x: (x[0].hour, x[0].minute)):
                        group = list(grp)
                        hyperd = sum([v[1] for v in group]) >= (len(group) / 2)
                        moneyd = sum([v[2] for v in group]) >= (len(group) / 2)
                        codiusd = sum([v[3] for v in group]) >= (len(group) / 2)
                        nginx = sum([v[4] for v in group]) >= (len(group) / 2)
                        result.append({'time': hr_minute, 'hyperd': int(hyperd), 'moneyd': int(moneyd), 'codiusd': int(codiusd), 'nginx': int(nginx) })
                elif body['days'] > 1:
                    for hr, grp in itertools.groupby(services_status_log, lambda x: x[0].hour):
                        group = list(grp)
                        hyperd = sum([v[1] for v in group]) >= (len(group) / 2)
                        moneyd = sum([v[2] for v in group]) >= (len(group) / 2)
                        codiusd = sum([v[3] for v in group]) >= (len(group) / 2)
                        nginx = sum([v[4] for v in group]) >= (len(group) / 2)
                        result.append({'hour': hr, 'hyperd': int(hyperd), 'moneyd': int(moneyd), 'codiusd': int(codiusd), 'nginx': int(nginx) })
            return {'success': True, 'body': result}
        except Exception as e:
            return {'success': False, 'body': e}

    def run_systemctl_command(self, command, service_name, command_name):
        try:
            logger.info(command)
            with SystemService() as system_service:
                result = system_service.run_command(['systemctl', command, service_name])
                if command == 'stop' or command == 'restart' or command == 'start':
                    logger.info('stop/restart/start')
                    return {'success': True}
                else:
                    return bash_cmd_result(result)
        except Exception as e:
            logger.error("Error on command: {} :{}".format(command_name.name, e))
            return {'success': False, 'body': e}

    def install_service(self, name):
        if name == 'fail2ban':
            return run_bash_script(bash_scripts['install_fail2ban'], timeout=120)

    def uninstall_service(self, name):
        if name == 'fail2ban':
            with SystemService() as system_service:
                if 'centos'in DISTRIB:
                    result = system_service.run_command('yum remove -y fail2ban\*', shell=True)
                if 'ubuntu'in DISTRIB or 'debian' in DISTRIB:
                    result = system_service.run_command('apt-get remove -y fail2ban\*', shell=True)
                if 'fedora'in DISTRIB:
                    result = system_service.run_command('dnf remove -y fail2ban\*', shell=True)
                else:
                    return {'success': False, 'body': f'OS not supported'}
                return bash_cmd_result(result)
        else:
            return {'success': False, 'body': f'{name} service is not supported'}

    def run_cmoncli_installer(self, path):
        if len(path) > 0:
            command = f'wget {REST_SERVER}/{path} -O cmoncli-install.sh && bash cmoncli-install.sh'
            logger.info(f'getting installer {command}')
            return run_bash_script('', command=command, timeout=45)
        else:
            return {'success': False, 'body': "invalid installer command"}

    def service_special_data(self, msg):
        if msg.body['name'] in EXTRA_SERVICES:
            if msg.body['name'] == 'fail2ban':
                try:
                    logger.info('Running fail2ban log request')
                    with SystemService() as system_service:
                        result = system_service.run_command('tail -n 1000 /var/log/secure | grep \'Failed password\'',
                                                            shell=True)
                        return bash_cmd_result(result)
                except Exception as e:
                    logger.error(e)
                    return {'success': False, 'body': e.__str__()}
            if msg.body['name'] == 'netstat':
                try:
                    cmd = 'netstat {}'.format(msg.body['args'].strip())
                    logger.info('Running netstat request: {}'.format(cmd))
                    with SystemService() as system_service:
                        result = system_service.run_command(cmd, shell=True)
                        return bash_cmd_result(result, exclude_errors=True)
                except Exception as e:
                    logger.error(e)
                    return {'success': False, 'body': e.__str__()}
            return {'success': False, 'body': f'{msg.body} no method for this service'}
        else:
            return {'success': False, 'body': f'{msg.body} service is not supported'}


    # messy, but need to block additional attempts in order to not let them possibly hang API
    def cmoncli_autoupgrade(self, data):
        if data['token']:
            if not version.error['autoinstall_gen'] or (
                    version.error['autoinstall_gen'] and timediff_min(version.error['autoinstall_gen']) > 30):
                cli_links = generate_cmoncli(data['token'])
                if cli_links['installer']:
                    if not version.error['autoinstall_cli'] or (
                            version.error['autoinstall_cli'] and timediff_min(version.error['autoinstall_cli']) > 60):
                        try:
                            return self.run_cmoncli_installer(cli_links['installer'])
                        except Exception as e:
                            logger.error(f'Failed to install cmoncli {e}')
                            version.error['autoinstall_cli'] = datetime.now()
                            return {'success': False, 'body': f'Failed to install cmoncli {e.__str__()}'}
                else:
                    version.error['autoinstall_gen'] = datetime.now()
                    logger.info('Failed to generate cmoncli')
                    return {'success': False, 'body': 'Failed to generate cmoncli'}
        else:
            return {'success': False, 'body': 'Client auth fail'}


def timediff_min(prev):
    return (datetime.now() - prev).total_seconds() / 60
