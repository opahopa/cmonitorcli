import logging
import sys
import datetime

sys.path.append("..")

from models.message import MessageCommands, MessageTypes
from services.system.system_service import SystemService
from .message_helpers import parse_message, result_to_json_response
from models.response import ResponseTypes, ResponseStatus

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
            result = self._execute_command(msg)
            return result_to_json_response(result, msg.command, ResponseStatus.OK, self.hostname)
        except Exception as e:
            logger.error("Error on command: {} :{}".format(msg.command.name, e))
            return result_to_json_response(self._execute_command(msg), msg.command, ResponseStatus.ERROR, self.hostname)


    def _execute_command(self, msg):
        if msg.command is MessageCommands.STATUS_ALL:
            with SystemService() as system_service:
                return system_service.report_all()

        return None

    def report_status(self):
        with SystemService() as system_service:
            result = system_service.report_all()
            return result_to_json_response(result, MessageCommands.STATUS_CLI_UPDATE, ResponseStatus.OK, self.hostname)