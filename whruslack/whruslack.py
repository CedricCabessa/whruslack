import sys
import os
import logging
import configparser
import appdirs

from whruslack import sleepmonitorfactory
from whruslack.scheduler import Scheduler
from whruslack.slack import Slack
from whruslack.command import Command


def get_wakeup_callback(scheduler, command):
    def _wakeup_callback():
        scheduler.resume()
        scheduler.call_soon(command.scan_wifi_and_update_status)
    return _wakeup_callback


def get_sleep_callback(scheduler, command):
    def _sleep_callback():
        scheduler.call_soon(command.resetstatus)
        scheduler.pause()
    return _sleep_callback


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s:%(process)d:%(threadName)s:%(message)s")
    logger = logging.getLogger("whruslack")

    configfile = os.path.join(appdirs.user_config_dir("whruslack"),
                              "whruslack.ini")
    config = configparser.ConfigParser()
    config.read(configfile)

    if 'app' not in config or 'token' not in config['app']:
        logger.error('invalid configuration file, check "%s"', configfile)
        sys.exit(1)

    token = config['app']['token']
    slack = Slack(token)

    default_emoji = None

    refresh_period = 60 * int(config['app'].get('refresh_period', 15))
    logger.debug("refresh_period=%s", refresh_period)

    if 'default_emoji' in config['app']:
        default_emoji = config['app']['default_emoji']

    scheduler = Scheduler(refresh_period)
    command = Command(slack, config, default_emoji)
    sleepmonitor = \
        sleepmonitorfactory.getsleepmonitor(
            get_sleep_callback(scheduler, command),
            get_wakeup_callback(scheduler, command))

    sleepmonitor.start()
    scheduler.set_quit_cb(sleepmonitor.stop)
    scheduler.schedule(command)

    slack.resetstatus()
