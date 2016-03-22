#!/usr/bin/env python
from setuptools import setup

setup(
    name='SlackBotFramework',
    version="1.0.0",
    description="Slack bot framework",
    long_description="Slack bot framework",
    author='Matt Smith',
    author_email='matt.daemon660@gmail.com',
    url='https://github.com/psykzz/py-bot-framework',
    packages=['SlackBotFramework'],
    install_requires=[
        "slackclient",
    ]
)
