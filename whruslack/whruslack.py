import sys
import os
import logging
import configparser

import appdirs

from whruslack import wififactory
from whruslack.slack import Slack, WhruslackException

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

    if 'default_emoji' in config['app']:
        default_emoji = config['app']['default_emoji']

    currentAP = wififactory.getwifi().wifiAP()
    try:
        if currentAP not in config:
            logger.info('unknown wifi, reset status')
            slack.resetstatus()
        else:
            room = config[currentAP]
            status = ""
            if 'status' in room:
                status = room['status']

            emoji = default_emoji
            if 'emoji' in room:
                emoji = room['emoji']

            if emoji:
                slack.changestatus(status, emoji)
                logger.info('status "%s" emoji "%s"', status, emoji)
            else:
                logger.error('AP %s is misconfigured', currentAP)
                sys.exit(1)

    except WhruslackException as e:
        logger.error('slack error %s', e)
        sys.exit(1)
