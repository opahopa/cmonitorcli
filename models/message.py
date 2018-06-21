from enum import Enum


class MessageTypes(Enum):
    STATUS = 'STATUS',
    CONTROL = 'CONTROL'
    REPORT = 'REPORT'


class MessageStatus(Enum):
    OK = 'OK',
    ERROR = 'ERROR'


class MessageCommands(Enum):
    STATUS_ALL = 'STATUS_ALL'


class Message(object):

    def __init__(self, type, command, status=None, body=None):
        self.type = MessageTypes[type]

        if command:
            self.command = MessageCommands[command]
        if status:
            self.status = MessageStatus[status]
        if body:
            self.body = body