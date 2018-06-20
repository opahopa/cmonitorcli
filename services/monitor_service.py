import logging
import sys

sys.path.append("..")


from models.message import MessageCommands, MessageTypes
from services.system.system_service import SystemService
from .message_helpers import parse_message

logger = logging.getLogger(__name__)

class MonitorService(object):


    def watch_message(self, content):
        msg = parse_message(content)

        if msg.type is MessageTypes.CONTROL:
            self._execute_command(msg)

    def _execute_command(self, msg):
        if msg.command is MessageCommands.STATUS_ALL:
            with SystemService() as system_service:
                system_service.reposr_all()