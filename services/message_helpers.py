import logging
import sys
import json
import traceback

from models.report import ReportService
from models.response import ResponseTypes, ResponseStatus
from models.message import MessageCommands, MessageStatus

sys.path.append("..")

from models.message import Message

logger = logging.getLogger(__name__)


def parse_message(content):
    try:
        content = json.loads(content)
        msg = Message(type=content["type"], command=content["command"])
        try:
            msg.status = content["status"]
        except KeyError:
            pass
        try:
            msg.body = content["body"]
        except KeyError:
            pass
        return msg
    except Exception as e:
        logger.error(e)
        # traceback.print_exc()


def result_to_json_response(content, type, status, hostname):
    result = {}
    result['type'] = "REPORT"
    result['command'] = type.name
    result['status'] = status.name
    result['hostname'] = hostname
    result['body'] = content

    if status is MessageStatus.ERROR:
        return json.dumps(result)

    if type is MessageCommands.STATUS_ALL:
        for i in range(0, len(content)):
            if isinstance(content[i], ReportService):
                content[i] = content[i].toDict()

    #     for k, v in content.items():
    #         try:
    #             if isinstance(content[k], ReportService):
    #                 content[k] = v.toDict()
    #         except Exception as e:
    #             logger.error(e)


        result['body'] = content

    return json.dumps(result)