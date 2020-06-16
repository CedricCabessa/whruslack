import logging
from threading import Thread

logger = logging.getLogger("whruslack")


class SleepMonitor(Thread):
    def __init__(self, sleep_callback, wakeup_callback):
        super().__init__()
        self.sleep_cb = sleep_callback
        self.wakeup_cb = wakeup_callback

    def run(self):
        logger.warning(
            "macos version of SleepMonitor not implemented, " "please send me a patch"
        )

    def stop(self):
        logger.warning(
            "macos version of SleepMonitor not implemented, " "please send me a patch"
        )
