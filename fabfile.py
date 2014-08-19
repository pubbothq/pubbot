import os
from fabric.api import env
from fuselage.contrib.fabric import blueprint
from fuselage.resources import *


def template(path, ctx=None):
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader(os.path.join(os.getcwd(), "files")))
    return env.get_template(path).render(**(ctx or {})) + "\n"


def static(path):
    with open(os.path.join(os.getcwd(), "files", path), "rb") as fp:
        return fp.read()


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
