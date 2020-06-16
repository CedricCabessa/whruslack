import configparser
import logging
import os
import sys

import appdirs

from whruslack import sleepmonitorfactory
from whruslack.command import Command
from whruslack.scheduler import Scheduler
from whruslack.slack import Slack


def get_wakeup_callback(scheduler, command):
    def _wakeup_callback():
        scheduler.resume()
        scheduler.call_soon(command.default)

    return _wakeup_callback


def get_sleep_callback(scheduler, command):
    def _sleep_callback():
        scheduler.call_soon(command.resetstatus)
        scheduler.pause()

    return _sleep_callback


def try_client(scheduler, args):
    if len(args) == 1 and args[0] == "reload":
        return scheduler.try_send_message(b"reload")
    elif len(args) == 1 and args[0] == "ping":
        return scheduler.try_send_message(b"ping")
    elif len(args) == 1 and args[0] == "meeting":
        return scheduler.try_send_message(b"meeting")
    elif len(args) == 2 and args[0] == "holiday":
        return scheduler.try_send_message(b"holiday;%s" % args[1].encode())
    elif len(args) == 1 and args[0] == "default":
        return scheduler.try_send_message(b"default")

    print("unknown command or invalid syntax")
    return "ERROR"


def server(scheduler, slack, config, default_emoji):
    """ Configure and start the server
    """
    command = Command(slack, config, default_emoji)
    sleepmonitor = sleepmonitorfactory.getsleepmonitor(
        get_sleep_callback(scheduler, command), get_wakeup_callback(scheduler, command)
    )
    sleepmonitor.start()
    scheduler.set_quit_cb(sleepmonitor.stop)
    scheduler.schedule(command)

    slack.resetstatus()


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s:%(process)d:%(threadName)s:%(message)s",
    )
    logger = logging.getLogger("whruslack")

    configfile = os.path.join(appdirs.user_config_dir("whruslack"), "whruslack.ini")
    config = configparser.ConfigParser()
    config.read(configfile)

    if "app" not in config or "token" not in config["app"]:
        logger.error('invalid configuration file, check "%s"', configfile)
        sys.exit(1)

    token = config["app"]["token"]
    slack = Slack(token)

    default_emoji = None

    refresh_period = 60 * int(config["app"].get("refresh_period", 15))
    logger.debug("refresh_period=%s", refresh_period)

    if "default_emoji" in config["app"]:
        default_emoji = config["app"]["default_emoji"]

    scheduler = Scheduler(refresh_period)
    if len(sys.argv) > 1:
        try:
            # client mode?
            reply = try_client(scheduler, sys.argv[1:])
            assert reply == "OK" or reply == "ERROR"
        except (ConnectionRefusedError, FileNotFoundError):
            print("no server running, launch it with no argument")
    else:
        try:
            reply = try_client(scheduler, ["ping"])
            print(reply)
        except (ConnectionRefusedError, FileNotFoundError):
            server(scheduler, slack, config, default_emoji)
