from enum import Enum


class ResponseTypes(Enum):
    STATUS_ALL = 'STATUS_ALL',
    STATUS_ONE = 'STATUS_ONE'


class ResponseStatus(Enum):
    OK = 'OK',
    ERROR = 'ERROR'
