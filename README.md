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

## Usage

For now, whruslack is a simple command line tool, you need to call it manually
everytime you want to change your status.

You can add it in a crontab if you want

Future version should provide a daemon mode.
