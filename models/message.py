from enum import Enum


class MessageTypes(Enum):
    STATUS = 'STATUS',
    CONTROL = 'CONTROL'
    REPORT = 'REPORT'


class MessageStatus(Enum):
    OK = 'OK',
    ERROR = 'ERROR'


class MessageCommands(Enum):
    STATUS_ALL = 'STATUS_ALL',
    STATUS_CLI_DISCONNECT = 'STATUS_CLI_DISCONNECT',
    STATUS_CLI_UPDATE = 'STATUS_CLI_UPDATE',
    SERVICE_RESTART = 'SERVICE_RESTART',
    SERVICE_STOP = 'SERVICE_STOP',
    SERVICE_SPECAIL_DATA = 'SERVICE_SPECAIL_DATA',
    STATS_ALL = 'STATS_ALL',
    SET_CODIUS_FEE = 'SET_CODIUS_FEE',
    POD_UPLOAD_SELFTEST = 'POD_UPLOAD_SELFTEST',
    CMONCLI_UPDATE = 'CMONCLI_UPDATE',
    INSTALL_SERVICE = 'INSTALL_SERVICE',
    CLI_UPGRADE_REQUIRED = 'CLI_UPGRADE_REQUIRED',
    CLI_UPGRADE = 'CLI_UPGRADE'


class Message(object):

    def __init__(self, type, command, status=None, body=None, hostname=None):
        self.type = MessageTypes[type]

        if command:
            self.command = MessageCommands[command]
        if status:
            self.status = MessageStatus[status]
        if body:
            self.body = body
        if hostname:
            self.hostname = hostname