import sys
import os
import logging
import configparser

import appdirs

from whruslack import wififactory
from whruslack import sleepmonitorfactory
from whruslack.scheduler import Scheduler
from whruslack.slack import Slack


def scan_wifi_and_update_status(slack, roomconfig, default_emoji):
    logger = logging.getLogger("whruslack")
    currentAP = wififactory.getwifi().wifiAP()
    if not currentAP:
        logger.debug("currentAP is None")
        return

    if currentAP not in roomconfig:
        logger.info('unknown wifi, reset status')
        slack.resetstatus()
    else:
        room = roomconfig[currentAP]
        status = ""
        if 'status' in room:
            status = room['status']

        emoji = default_emoji
        if 'emoji' in room:
            emoji = room['emoji']

        if emoji:
            slack.changestatus(status, emoji)
        else:
            logger.error('AP %s is misconfigured', currentAP)


def get_wakeup_callback(scheduler, slack, config, default_emoji):
    def _wakeup_callback():
        scheduler.resume()
        scheduler.call_soon(scan_wifi_and_update_status, slack, config, default_emoji)
    return _wakeup_callback


def get_sleep_callback(scheduler, slack):
    def _sleep_callback():
        # executed in caller thread, will block the shutdown process
        slack.resetstatus()
        scheduler.pause()
    return _sleep_callback


def main():
    logging.basicConfig(level=logging.DEBUG,
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

    sleepmonitor = \
        sleepmonitorfactory.getsleepmonitor(get_sleep_callback(scheduler, slack),
                                            get_wakeup_callback(scheduler, slack,
                                                                config, default_emoji))

    sleepmonitor.start()
    scheduler.set_quit_cb(sleepmonitor.stop)
    scheduler.schedule(scan_wifi_and_update_status, slack, config, default_emoji)

    slack.resetstatus()
