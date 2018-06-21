from .logging import *
# logging.basicConfig(format='%(levelname)s|%(asctime)s|%(module)s|%(funcName)s|%(lineno)d|%(message)s',
#                            datefmt="%d/%b/%Y %H:%M:%S" , filename='example.log', level=logging.DEBUG)
WEBSOCKET_SERVER = 'ws://127.0.0.1:8000'
ACC_USERNAME = 'test@test.com'
WATCH_SERVICES = {
    'hyperd':"hyperd",
    'moneyd':"moneyd-xrp",
    'codiusd':"codiusd",
    'nginx':"nginx"
}