import time
import logging
from urllib.error import URLError
from whruslack import wififactory

logger = logging.getLogger("whruslack")


class Command:
    """ Implement command sent by the client and the default behavior
    :default():
    """

    def __init__(self, slack, roomconfig, default_emoji):
        self.slack = slack
        self.roomconfig = roomconfig
        self.default_emoji = default_emoji
        self.status_override_cmd = None

    def handle_message(self, msg):
        if msg == "reload":
            self.reload()
        elif msg == "meeting":
            self.meeting()
        elif msg == "default":
            self.default()
        elif msg.startswith("holiday;"):
            self.holiday(msg[msg.index(";") + 1 :])
        elif msg == "ping":
            if self.status_override_cmd:
                return self.status_override_cmd
            return "default"
        else:
            logger.error("unknown command")
            return None
        return "OK"

    def reload(self):
        if not self.status_override_cmd:
            self.__scan_wifi_and_update_status()
        else:
            logger.debug("status is overridden")

    def __scan_wifi_and_update_status(self):
        for _ in range(0, 10):
            current_ap = wififactory.getwifi().wifi_ap()
            if current_ap:
                current_ap = current_ap.lower()
                break
            time.sleep(1)
        else:
            logger.debug("current AP is None")
            return

        for status in self.roomconfig:
            if status == "app" or status == "DEFAULT":
                continue
            room = self.roomconfig[status]
            if "ap" not in room:
                logger.error("no 'ap' for %s", status)
                return
            configured_aps = [x.strip().lower() for x in room["ap"].split(",")]
            if current_ap in configured_aps:
                emoji = self.default_emoji
                if "emoji" in room:
                    emoji = room["emoji"]

                if emoji:
                    for _ in range(0, 10):
                        try:
                            self.slack.changestatus(status, emoji)
                        except URLError as exc:
                            logger.error("error %s", exc)
                            time.sleep(5)
                        else:
                            break
                else:
                    logger.error('"%s" is misconfigured', status)
                break
        else:
            logger.info("unknown wifi, reset status")
            self.slack.resetstatus()

    def resetstatus(self):
        self.slack.resetstatus()

    def meeting(self):
        self.status_override_cmd = "meeting"
        self.slack.changestatus("in a meeting", ":calendar:")

    def holiday(self, msg):
        self.status_override_cmd = "holiday"
        self.slack.changestatus("Vacationing %s" % msg, ":palm_tree:")

    def default(self):
        self.status_override_cmd = None
        self.reload()
