import logging
import os

from models.message import MessageCommands, MessageTypes
from services.system.system_service import SystemService
from services.db_service import DbService
from .message_helpers import parse_message, result_to_json_response, calc_dialy_income
from models.response import ResponseStatus

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
            os.environ['CODIUS_COST_PER_MONTH'] = str(msg.body)
        if msg.command is MessageCommands.SERVICE_RESTART and msg.hostname == self.hostname:
            try:
                with SystemService() as system_service:
                    system_service.run_command(['systemctl', 'restart', msg.body])
                    return result_to_json_response(msg.command, ResponseStatus.OK, self.hostname)
            except Exception as e:
                logger.error("Error on command: {} :{}".format(msg.command.name, e))
                return result_to_json_response(msg.command, ResponseStatus.ERROR, self.hostname, body=e)

        return None

    def report_status(self):
        with SystemService() as system_service:
            system = system_service.report_system_services()
            codius = system_service.report_codius()
            with DbService() as db_service:
                codius['income_24'] = 0
                db_service.write_pods_status(codius)
                if len(db_service.get_pods_in24hours()) > 0:
                    codius['income_24'], codius['count_24'] = calc_dialy_income(db_service.get_pods_in24hours())

            return result_to_json_response(MessageCommands.STATUS_CLI_UPDATE, ResponseStatus.OK, self.hostname,
                                           report_system=system, report_codius=codius)
