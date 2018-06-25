import sys
import os
import logging
import configparser
import time

import appdirs

from whruslack import wififactory
from whruslack import sleepmonitorfactory
from whruslack.scheduler import Scheduler
from whruslack.slack import Slack


def scan_wifi_and_update_status(slack, roomconfig, default_emoji):
    logger = logging.getLogger("whruslack")
    for _ in range(0, 10):
        currentAP = wififactory.getwifi().wifiAP()
        if currentAP:
            currentAP = currentAP.lower()
            break
        time.sleep(1)
    else:
        logger.debug("currentAP is None")
        return

    for status in roomconfig:
        if status == 'app' or status == 'DEFAULT':
            continue
        room = roomconfig[status]
        if 'ap' not in room:
            logger.error("no 'ap' for %s", status)
            return
        ap = [x.strip().lower() for x in room['ap'].split(',')]
        if currentAP in ap:
            emoji = default_emoji
            if 'emoji' in room:
                emoji = room['emoji']

            if emoji:
                for _ in range(0, 10):
                    try:
                        slack.changestatus(status, emoji)
                    except Exception as e:
                        logger.error("error %s", e)
                        time.sleep(5)
                    else:
                        break
            else:
                logger.error('"%s" is misconfigured', status)
            break
    else:
        logger.info('unknown wifi, reset status')
        slack.resetstatus()


def get_wakeup_callback(scheduler, slack, config, default_emoji):
    def _wakeup_callback():
        scheduler.resume()
        scheduler.call_soon(scan_wifi_and_update_status, slack, config,
                            default_emoji)
    return _wakeup_callback


def get_sleep_callback(scheduler, slack):
    def _sleep_callback():
        scheduler.call_soon(slack.resetstatus)
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

    sleepmonitor = \
        sleepmonitorfactory.getsleepmonitor(
            get_sleep_callback(scheduler, slack),
            get_wakeup_callback(scheduler, slack,
                                config, default_emoji))

    sleepmonitor.start()
    scheduler.set_quit_cb(sleepmonitor.stop)
    scheduler.schedule(scan_wifi_and_update_status, slack,
                       config, default_emoji)

    slack.resetstatus()
