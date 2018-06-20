import logging
import sys
import json
import traceback

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
        logger.error(e.__str__())
        # traceback.print_exc()
