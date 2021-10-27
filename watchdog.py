from threading import Timer

# https://stackoverflow.com/a/16148744

class Watchdog(Exception):
    def __init__(self, timeout, userHandler=None):  # timeout in seconds
        self.timeout = timeout
        self.handler = userHandler if userHandler is not None else self.defaultHandler
        self.timer = Timer(self.timeout, self.handler)
        self.timer.start()
        self.flag = True

    def reset(self):
        self.timer.cancel()
        self.timer = Timer(self.timeout, self.handler)
        self.flag = True
        self.timer.start()

    def stop(self):
        self.timer.cancel()

    def defaultHandler(self):
        self.flag = False
