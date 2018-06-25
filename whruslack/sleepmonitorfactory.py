import sys


def getsleepmonitor(sleep_callback, wakeup_callback):
    """ Return an os specific class with the following method.

    run(): start a thread to watch for sleep or shutdown signal
    stop(): stop the thread

    User should provide 2 callback:
    sleep_callback -- called when sleep or shutdown is detected
    wakeup_callback -- called when coming back from sleep
    """
    if sys.platform.startswith('linux'):
        import whruslack.linux.sleepmonitor
        return whruslack.linux.sleepmonitor.SleepMonitor(sleep_callback,
                                                         wakeup_callback)
    elif sys.platform.startswith('darwin'):
        import whruslack.macos.sleepmonitor
        return whruslack.macos.sleepmonitor.SleepMonitor(sleep_callback,
                                                         wakeup_callback)
    else:
        raise NotImplementedError("your os %s is not supported" % sys.platform)
