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

apt_preferences_redis = """
Package: redis-server
Pin: release n=wheezy-backports
Pin-Priority: 900
""".strip()

redis_launchd = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>KeepAlive</key>
    <dict>
      <key>SuccessfulExit</key>
      <false/>
    </dict>
    <key>Label</key>
    <string>homebrew.mxcl.redis</string>
    <key>UserName</key>
    <string>pubbot</string>
    <key>ProgramArguments</key>
    <array>
      <string>/usr/local/opt/redis/bin/redis-server</string>
      <string>/usr/local/etc/redis.conf</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>/usr/local/var</string>
    <key>StandardErrorPath</key>
    <string>/usr/local/var/log/redis.log</string>
    <key>StandardOutPath</key>
    <string>/usr/local/var/log/redis.log</string>
  </dict>
</plist>
""".strip()


pubbot_launchd = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>KeepAlive</key>
    <dict>
      <key>SuccessfulExit</key>
      <false/>
    </dict>
    <key>Label</key>
    <string>io.unrouted.pubbot</string>
    <key>UserName</key>
    <string>pubbot</string>
    <key>ProgramArguments</key>
    <array>
      <string>/Users/pubbot/pubbot/bin/pubbot</string>
      <string>bot</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>/Users/pubbot/pubbot</string>
    <key>StandardErrorPath</key>
    <string>/tmp/pubbot.log</string>
    <key>StandardOutPath</key>
    <string>/tmp/pubbot.log</string>
  </dict>
</plist>
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

    yield File(
        name="/etc/apt/preferences.d/redis-server",
        contents=apt_preferences_redis,
    )

    yield File(
        name="/etc/apt/sources.list.d/wheezy-backports",
        contents="deb http://ftp.debian.org/debian wheezy-backports main contrib non-free",
    )

    yield Execute(
        command="apt-get update",
        watches=[
            "/etc/apt/preferences.d/redis-server",
            "/etc/apt/sources.list.d/wheezy-backports",
        ]
    )

    yield Package(name="redis-server")

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


@blueprint
def deploy_osx(bundle, **kwargs):
    yield Execute(
        command="brew install redis",
        creates="/usr/local/bin/redis-server",
    )
    yield File(
        name="/Library/LaunchDaemons/homebrew.mxcl.redis.plist",
        contents=redis_launchd,
    )
    yield Execute(
        command="launchctl load /Library/LaunchDaemons/homebrew.mxcl.redis.plist",
        watches=["/Library/LaunchDaemons/homebrew.mxcl.redis.plist"],
    )

    yield Execute(
        command="easy_install virtualenv",
        creates="/usr/local/bin/virtualenv",
    )

    yield Execute(
        command='virtualenv /Users/pubbot/pubbot',
        creates='/Users/pubbot/pubbot/bin/pip',
        user='pubbot',
        )

    yield Directory(
        name='/Users/pubbot/pubbot/var',
        owner='pubbot',
    )

    yield Checkout(
        name='/Users/pubbot/pubbot/src',
        repository='git://github.com/pubbothq/pubbot',
        scm="git",
        user='pubbot',
        branch='master',
        )

    yield Execute(
        command='/Users/pubbot/pubbot/bin/pip install -r /Users/pubbot/pubbot/src/requirements.txt',
        cwd='/Users/pubbot/pubbot/src',
        user='pubbot',
        watches=['/Users/pubbot/pubbot/src'],
    )

    yield Execute(
        command='/Users/pubbot/pubbot/bin/pubbot update',
        cwd='/Users/pubbot/pubbot/src',
        user='pubbot',
        watches=['/Users/pubbot/pubbot/src'],
    )

    yield File(
        name="/Library/LaunchDaemons/io.unrouted.pubbot.plist",
        contents=pubbot_launchd,
    )
    yield Execute(
        commands=[
            "sh -c 'launchctl unload /Library/LaunchDaemons/io.unrouted.pubbot.plist || true'",
            "launchctl load /Library/LaunchDaemons/io.unrouted.pubbot.plist",
        ],
        watches=[
            "/Users/pubbot/pubbot/src",
            "/Library/LaunchDaemons/io.unrouted.pubbot.plist",
        ],
    )
