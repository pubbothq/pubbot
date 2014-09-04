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
def deploy(bundle):
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
        group='pubbot',
        )

    yield Directory(
        name='/var/local/pubbot/var',
        owner='pubbot',
        group='pubbot',
        )

    yield Package(name="git-core")
    yield Package(name="python-dev")
    yield Package(name="python-virtualenv")


    yield Execute(
        name='virtualenv',
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
        name='pip-install',
        command='/var/local/pubbot/bin/pip install -r /var/local/pubbot/src/requirements.txt',
        cwd='/var/local/pubbot/src',
        user='pubbot',
        watches=['/var/local/pubbot/src'],
    )

    yield Execute(
        name='migrate',
        command='/var/local/pubbot/bin/pubbot update',
        cwd='/var/local/pubbot/src',
        user='pubbot',
        watches=['/var/local/pubbot/src'],
    )

    yield File(
        name="/etc/systemd/system/pubbot.service",
        contents=systemd_unit,
    )

    # FIXME: Not entirely sure if this is required?
    # FIXME: Need a similar enable command to start on boot?
    yield Execute(
        name="systemctl-daemon-reload",
        command="systemctl daemon-reload",
        watches=['/etc/systemd/system/pubbot.service'],
    )

    yield Execute(
        name="systemctl-enable-pubbot",
        command="systemctl enable /etc/systemd/system/pubbot.service",
        creates="/etc/systemd/system/multi-user.target.wants/pubbot.service",
        )

    yield Execute(
        name="systemctl-restart",
        command="systemctl restart pubbot.service",
        watches=[
            "/var/local/pubbot/src",
            "/etc/systemd/system/pubbot.service",
        ]
    )
