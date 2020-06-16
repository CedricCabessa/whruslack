import re
import subprocess


class Wifi:
    def wifi_ap(self):
        out = subprocess.run(
            [
                "/System/Library/PrivateFrameworks/Apple80211.framework/"
                "Versions/Current/Resources/airport",
                "-I",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        match = re.search("BSSID: (([0-9A-Fa-f]{2}:?){6})", out.stdout.decode("utf-8"))
        if match:
            return match.group(1)

        return None
