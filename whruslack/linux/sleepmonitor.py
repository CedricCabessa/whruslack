from threading import Thread
import os

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib


class SleepMonitor(Thread):
    """ Watch for sleep or shutdown signal
    """
    def __init__(self, sleep_callback, wakeup_callback):
        super().__init__()
        self.sleep_cb = sleep_callback
        self.wakeup_cb = wakeup_callback
        self.fd = -1
        self.loop = GLib.MainLoop()
        self.dbus_inhibit = None

    def __prepareForSleepOrShutdown(self, sleep):
        if sleep:
            self.sleep_cb()
            self.__releaseInhibit()
        else:
            self.wakeup_cb()
            self.__inhibit()


    def __setup(self):
        DBusGMainLoop(set_as_default=True)
        system_bus = dbus.SystemBus()

        proxy = system_bus.get_object('org.freedesktop.login1',
                                      '/org/freedesktop/login1')
        login1 = dbus.Interface(proxy, 'org.freedesktop.login1.Manager')

        for signal in ['PrepareForSleep', 'PrepareForShutdown']:
            login1.connect_to_signal(signal, self.__prepareForSleepOrShutdown)

        self.dbus_inhibit = login1.Inhibit

        self.__inhibit()

    def __inhibit(self):
        dbus_fd = self.dbus_inhibit("shutdown:sleep",
                                    "Wruslack", "Updating status", "delay")
        self.fd = dbus_fd.take()

    def __releaseInhibit(self):
        os.close(self.fd)

    def run(self):
        self.__setup()
        self.loop.run()

    def stop(self):
        self.loop.quit()
