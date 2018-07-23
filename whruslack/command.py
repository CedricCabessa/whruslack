import time
import logging
from whruslack import wififactory

logger = logging.getLogger("whruslack")


class Command:
    def __init__(self, slack, roomconfig, default_emoji):
        self.slack = slack
        self.roomconfig = roomconfig
        self.default_emoji = default_emoji

    def reload(self):
        self.scan_wifi_and_update_status()

    def scan_wifi_and_update_status(self):
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

        for status in self.roomconfig:
            if status == 'app' or status == 'DEFAULT':
                continue
            room = self.roomconfig[status]
            if 'ap' not in room:
                logger.error("no 'ap' for %s", status)
                return
            ap = [x.strip().lower() for x in room['ap'].split(',')]
            if currentAP in ap:
                emoji = self.default_emoji
                if 'emoji' in room:
                    emoji = room['emoji']

                if emoji:
                    for _ in range(0, 10):
                        try:
                            self.slack.changestatus(status, emoji)
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
            self.slack.resetstatus()

    def resetstatus(self):
        self.slack.resetstatus()

    def meeting(self):
        self.slack.changestatus('in a meeting', ':calendar:')
