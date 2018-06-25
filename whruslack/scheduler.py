import signal
import asyncio


class Scheduler:
    """ Configure asyncio and call a callback (see schedule) every
    :refresh_period:.
    You can also add a callback to be called when the scheduling finish with
    :set_quit_cb:
    """
    def __init__(self, refresh_period):
        self.loop = asyncio.get_event_loop()
        self.refresh_period = refresh_period
        self.handle_callback = None
        self.handle_rearm = None
        self.quit_cb = None
        self.callback = None

    def __quitloop(self):
        if self.quit_cb:
            self.quit_cb()
        self.loop.stop()

    def pause(self):
        """ Stop scheduling """
        self.handle_callback.cancel()
        self.handle_rearm.cancel()

    def resume(self):
        """ Resume scheduling after pause """
        self.handle_callback = self.loop.call_later(self.refresh_period,
                                                    self.callback)
        self.handle_rearm = self.loop.call_later(self.refresh_period,
                                                 self.resume)

    def schedule(self, callback, *args):
        """ schedule a callback to be called every :refresh_period: second
        The scheduling stop on SIGTERM and SIGINT
        """
        def _callback():
            return callback(*args)
        self.callback = _callback

        self.resume()

        self.loop.add_signal_handler(signal.SIGTERM, self.__quitloop)
        self.loop.add_signal_handler(signal.SIGINT, self.__quitloop)

        # call once immediately
        self.callback()

        self.loop.run_forever()

    def set_quit_cb(self, fn, *args):
        """ add a callback to be called when scheduling finish"""
        def _quit_cb():
            fn(*args)

        self.quit_cb = _quit_cb

    def call_soon(self, fn, *args):
        """ Call on the main thread as soon as possible
        This method can be called from another thread.
        """
        self.loop.call_soon_threadsafe(fn, *args)
