import logging
import sys
import datetime, time

sys.path.append("..")

from models.message import MessageCommands, MessageTypes
from services.system.system_service import SystemService
from services.db_service import DbService
from .message_helpers import parse_message, result_to_json_response, calcDialyIncome
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
                return self.execute_command_wrapper(msg)
        except AttributeError:
            return None

    def execute_command_wrapper(self, msg):
        try:
            system, codius = self._execute_command(msg)
            return result_to_json_response(system, codius, msg.command, ResponseStatus.OK, self.hostname)
        except Exception as e:
            logger.error("Error on command: {} :{}".format(msg.command.name, e))
            system, codius = self._execute_command(msg)
            return result_to_json_response(system, codius, msg.command, ResponseStatus.ERROR, self.hostname)


    def _execute_command(self, msg):
        if msg.command is MessageCommands.STATUS_ALL:
            with SystemService() as system_service:
                system = system_service.report_system_services()
                codius = system_service.report_codius()
                return system, codius

        return None

    def report_status(self):
        with SystemService() as system_service:
            system = system_service.report_system_services()
            codius = system_service.report_codius()
            with DbService() as db_service:
                logger.info(calcDialyIncome(db_service.get_pods_in24hours()))
                # db_service.write_pods_status(codius['pods'])
            return result_to_json_response(system, codius, MessageCommands.STATUS_CLI_UPDATE, ResponseStatus.OK, self.hostname)