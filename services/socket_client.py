import websocket, json
import logging
import time

try:
    import thread
except ImportError:
    import _thread as thread

try:
    import threading
except ImportError:
    import _threading as threading

logger = logging.getLogger(__name__)


class WsClient(object):

    def __enter__(self):
        return self

    def __init__(self, url, func_param, func_onmsg):
        self.url = url
        self.func_param = func_param
        self.func_onmsg = func_onmsg
        # self.connect()

    def connect(self):
        websocket.enableTrace(True)
        try:
            self.ws = websocket.WebSocketApp(self.url,
                                             on_message=self.on_message,
                                             on_error=self.on_error,
                                             on_close=self.on_close)

            self.ws.on_open = self.on_open
            self.ws.run_forever()
        except websocket.WebSocketConnectionClosedException:
            pass

    def on_message(self, ws, message):
        try:
            logger.info("received message: {}".format(message))
            self.func_onmsg(ws, message)
        except Exception as e:
            logger.info(e)
            pass

    def on_error(self, ws, error):
        logger.error(error)

    def on_close(self, ws):
        logger.info("### closed ###")

        # 5 days with 5 sec interval
        for i in range(0, 86400):
            try:
                time.sleep(5)
                self.connect()
            except:
                pass

    def on_open(self, ws):
        """
        to send main report here
        :param ws:
        :return:
        """

        def run(func_param):
            logger.info("connected")
            # ws.send(json.dumps({
            #     'message': "Hello there"
            # }))
            # func_param()
            # ws.close()

        thread.start_new_thread(run, (self.func_param,))
