import subprocess
import re

class Wifi:
    def wifiAP(self):
        # stupidly return the first Access Point
        out = subprocess.run(['iwconfig'], stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL)
        match = re.search('Access Point: (([0-9A-Fa-f]{2}:?){6})',
                          out.stdout.decode('utf-8'))
        return match.group(1)

