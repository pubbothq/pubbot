#!/usr/bin/env python
import os
import sys

try:
    from gevent import monkey
    monkey.patch_all()
except ImportError:
    pass

try:
    import gevent_psycopg2
    gevent_psycopg2.monkey_patch()
except ImportError:
    pass


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pubbot.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
