from threading import Thread

class SleepMonitor(Thread):
    def __init__(self, sleep_callback, wakeup_callback):
        super().__init__()
        self.sleep_cb = sleep_callback
        self.wakeup_cb = wakeup_callback

    def run(self):
        raise NotImplementedError("please send me a patch")

    def stop(self):
        raise NotImplementedError("please send me a patch")
