""" Ayncio based timer and client server.
The server wait to refresh the wifi status and listen for command coming from
the client command line
Client and server are implemented in :ProtoClient: and :ProtoServer:
"""

import signal
import asyncio
import logging

SOCKET = "/tmp/whruslack.sock"
logger = logging.getLogger("whruslack")


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
        self.handle_callback = self.loop.call_later(self.refresh_period, self.callback)
        self.handle_rearm = self.loop.call_later(self.refresh_period, self.resume)

    def try_send_message(self, message):
        coro_client = self.loop.create_unix_connection(
            lambda: ProtoClient(self.loop, message), SOCKET
        )
        ret = self.loop.run_until_complete(coro_client)
        self.loop.run_forever()
        return ret[1].reply

    def schedule(self, command, *args):
        """ schedule a callback to be called every :refresh_period: second
        The scheduling stop on SIGTERM and SIGINT
        """

        def _callback():
            return command.reload(*args)

        self.callback = _callback

        self.resume()

        self.loop.add_signal_handler(signal.SIGTERM, self.__quitloop)
        self.loop.add_signal_handler(signal.SIGINT, self.__quitloop)

        # call once immediately
        self.callback()

        coro_server = self.loop.create_unix_server(lambda: ProtoServer(command), SOCKET)
        self.loop.run_until_complete(coro_server)
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


class ProtoClient(asyncio.Protocol):
    def __init__(self, loop, message):
        self.message = message
        self.loop = loop
        self.reply = None

    def connection_made(self, transport):
        transport.write(self.message)

    def connection_lost(self, exc):
        pass

    def data_received(self, data):
        if data:
            self.reply = data.decode()
            self.loop.stop()

    def eof_received(self):
        pass


class ProtoServer(asyncio.Protocol):
    def __init__(self, command):
        self.command = command
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        pass

    def data_received(self, data):
        logger.debug("data_received %s", data)
        reply = self.command.handle_message(data.decode())
        if reply:
            self.transport.write(reply.encode())

    def eof_received(self):
        pass
