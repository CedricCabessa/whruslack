import re
import subprocess


class Wifi:
    def wifi_ap(self):
        # stupidly return the first Access Point
        out = subprocess.run(
            ["iwconfig"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )
        match = re.search(
            "Access Point: (([0-9A-Fa-f]{2}:?){6})", out.stdout.decode("utf-8")
        )
        # if we are called when wifi is down (hibernating) do not crash
        if match:
            return match.group(1)

        return None
