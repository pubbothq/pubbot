import os
from fabric.api import env
from fuselage.contrib.fabric import blueprint
from fuselage.resources import *


systemd_unit = """
[Unit]
Description = pubbot irc service

[Service]
ExecStart  = /var/local/pubbot/bin/pubbot bot
User       = pubbot
Group      = pubbot
Restart    = always
RestartSec = 30

[Install]
WantedBy = multi-user.target
""".strip()


@blueprint
def deploy(bundle, **kwargs):
    yield Group(name="pubbot")

    yield User(
        name="pubbot",
        group="pubbot",
        home="/var/local/pubbot",
        shell="/bin/false",
        system=True,
    )

    yield Directory(
        name='/var/local/pubbot',
        owner='pubbot',
        )

    yield Directory(
        name='/var/local/pubbot/var',
        owner='pubbot',
        )

    yield Package(name="git-core")
    yield Package(name="python-dev")
    yield Package(name="python-virtualenv")


    yield Execute(
        command='virtualenv /var/local/pubbot',
        creates='/var/local/pubbot/bin/pip',
        user='pubbot',
        )

    yield Checkout(
        name='/var/local/pubbot/src',
        repository='git://github.com/pubbothq/pubbot',
        scm="git",
        user='pubbot',
        branch='master',
        )

    yield Execute(
        command='/var/local/pubbot/bin/pip install -r /var/local/pubbot/src/requirements.txt',
        cwd='/var/local/pubbot/src',
        user='pubbot',
        watches=['/var/local/pubbot/src'],
    )

    yield Execute(
        command='/var/local/pubbot/bin/pubbot update',
        cwd='/var/local/pubbot/src',
        user='pubbot',
        watches=['/var/local/pubbot/src'],
    )

    yield File(
        name="/etc/systemd/system/pubbot.service",
        contents=systemd_unit,
    )

    yield Execute(
        command="systemctl daemon-reload",
        watches=['/etc/systemd/system/pubbot.service'],
    )

    yield Execute(
        command="systemctl enable /etc/systemd/system/pubbot.service",
        creates="/etc/systemd/system/multi-user.target.wants/pubbot.service",
        )

    yield Execute(
        command="systemctl restart pubbot.service",
        watches=[
            "/var/local/pubbot/src",
            "/etc/systemd/system/pubbot.service",
        ]
    )
