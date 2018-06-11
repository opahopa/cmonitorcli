import websocket

try:
    import thread
except ImportError:
    import _thread as thread
import time


def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    def run(*args):
        for i in range(3):
            time.sleep(1)
            ws.send("Hello %d" % i)
        time.sleep(1)
        ws.close()
        print("thread terminating...")

    thread.start_new_thread(run, ())


class WsClient(object):
    def __init__(self, url):
        self.url = url
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(self.url,
                                         on_message=on_message,
                                         on_error=on_error,
                                         on_close=on_close)
        self.ws.on_open = on_open
        self.ws.run_forever()


    def connect(self):
        pass

    def report(self):
        pass

    def close(self):
        self.ws.close()
