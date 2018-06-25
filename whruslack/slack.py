import urllib.request
from urllib.error import HTTPError
import json
import logging

logger = logging.getLogger("whruslack")


class Slack:
    def __init__(self, token):
        self.token = token

    def __dochangestatus(self, status=None, emoji=None):
        if status is None:
            status = ""
        if emoji is None:
            emoji = ""

        logger.info('status "%s" emoji "%s"', status, emoji)

        payload = '{"profile": {"status_text": "%s","status_emoji": "%s"}}' % \
                  (status, emoji)

        req = urllib.request.Request(
            'https://api.slack.com/api/users.profile.set',
            payload.encode('utf-8'),
            headers={'Content-Type': 'application/json; charset=utf-8',
                     'Authorization': 'Bearer %s' % self.token})

        try:
            with urllib.request.urlopen(req) as f:
                response = json.loads(f.read().decode('utf-8'))
                if not response['ok']:
                    logger.error('error from slack api: %s', response['error'])

        except HTTPError as e:
            logger.error("http errror %s", e)

    def changestatus(self, status, emoji):
        self.__dochangestatus(status, emoji)

    def resetstatus(self):
        self.__dochangestatus(None, None)
