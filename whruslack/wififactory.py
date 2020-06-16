import sys


def getwifi():
    if sys.platform.startswith("linux"):
        import whruslack.linux.wifi

        return whruslack.linux.wifi.Wifi()
    elif sys.platform.startswith("darwin"):
        import whruslack.macos.wifi

        return whruslack.macos.wifi.Wifi()
    else:
        raise NotImplementedError("your os %s is not supported" % sys.platform)
