from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.handlers.wsgi import WSGIHandler

import eventlet
from eventlet import wsgi

from pubbot import service


class Service(service.TaskService):

    def __init__(self, name):
        super(Service, self).__init__(name)

        bind = getattr(settings, "WEB_BIND", "127.0.0.1:8000")
        if ':' in bind:
            addr, port = bind.split(':')
        else:
            addr = ''
            port = bind

        try:
            port = int(port)
        except ValueError:
            raise ImproperlyConfigured("'WEB_BIND' must specify a port and it must be a valid integer")

        self.addr = addr
        self.port = port

    def run(self):
        self.logger.debug("Serving WSGI")
        wsgi.server(eventlet.listen((self.addr, self.port)), WSGIHandler())

        pool = Pool(self.pool_size) if self.pool_size else None
        self.logger.debug("Prerparing  WSGI server")
        server = wsgi.WSGIServer((self.addr, self.port), app, spawn=pool)

        server.serve_forever()
