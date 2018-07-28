# whruslack
Change slack status according to current wifi access point

I work in a very large office made of various rooms and spread on 3 floors. We
also use flexible workspace so people can work in the room they feel the most
comfortable.
When you need to talk with a coworker, it is sometime hard find where (s)he is.

Fortunately every room has its own wifi access point, so your laptop know where
you are :-)

This script simply change your current slack status according to the current
wifi access point, all you need to do is create a mapping between an access
point MAC address and a human name.


## Configuration

Create a configuration file in `~/.config/whruslack/whruslack.ini` on linux or
`~/Library/Preferences/whruslack/whruslack.ini` on mac.

See this [example](whruslack.ini)

## Installation

Whruslack use setuptools, so you should simply use:

```
 $ ./setup.py install --user
```

### linux

On linux, you can add whruslack as a systemd service

```
cp systemd/whruslack.service ~/.config/systemd/user/
systemctl --user enable whruslack.service
systemctl --user start whruslack.service
```

Logs are available with:

```
journalctl --user -u whruslack.service
```

Note that `whruslack` use `dbus` and `systemd-logind` to detect shutdown and
sleep event.

### Hibernation

We detect hibernation in order to clear your slack status when you close your
laptop.

However, NetworkManager shutdown the wifi interface on hibernation, so we cannot
send the request to the slack API.

A workaround consist of delay the wifi shutdown, this can be done with the
following command

```
sudo tee /etc/NetworkManager/dispatcher.d/pre-down.d/11-whruslack.sh << EOF
#!/bin/sh
sleep 2
EOF

sudo chmod +x /etc/NetworkManager/dispatcher.d/pre-down.d/11-whruslack.sh
```

## Usage

When the service is running, you can dynamically change the configuration with
the client.

A few predefined status are coded (TODO: make it configurable):

`whruslack meeting`
change the status to "meeting"

`whruslack holiday "back on Monday the 1st"`
change the status to "holiday", this status be followed by a free form text.
