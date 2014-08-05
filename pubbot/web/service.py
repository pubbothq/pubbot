from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.handlers.wsgi import WSGIHandler

from gevent import wsgi
from gevent.pool import Pool

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

        if getattr(settings, "WEB_POOL", None):
            try:
                self.pool_size = int(settings.WEB_POOL)
            except ValueError:
                raise ImproperlyConfigured("'WEB_POOL' must be an integer")
        else:
            self.pool_size = None

    def run(self):
        self.logger.debug("Getting WSGI application")
        app = WSGIHandler()

        pool = Pool(self.pool_size) if self.pool_size else None
        self.logger.debug("Prerparing  WSGI server")
        server = wsgi.WSGIServer((self.addr, self.port), app, spawn=pool)

        self.logger.debug("Serving WSGI requests")
        server.serve_forever()
