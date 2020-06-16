#!/usr/bin/env python3

from setuptools import find_packages, setup

setup(
    name="whruslack",
    version="0.1",
    packages=find_packages(),
    entry_points={"console_scripts": ["whruslack = whruslack.whruslack:main"]},
    install_requires=["appdirs", "dbus-python"],
    author="Cédric Cabessa",
    author_email="ced@ryick.net",
    description="Change slack status according to current wifi access point",
    license="MIT",
    url="https://github.com/CedricCabessa/whruslack",
)
