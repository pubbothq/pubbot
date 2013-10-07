from django.core.management.base import BaseCommand, CommandError
from gevent.socket import wait_read, timeout
from gevent.queue import Queue
from gevent.pool import Group
import pybonjour

from pubbot.main.utils import broadcast


class Command(BaseCommand):
    args = ''
    help = 'Listen to bonjour announcements on the network'

    def handle(self, *args, **options):
        self._to_resolve = Queue()

        group = Group()
        group.spawn(self._browse_loop)
        group.spawn(self._resolve_loop)
        group.join()

    def _browse_loop(self):
        # FIXME: Would be nice to detect more than just airplay...
        regtype = "_airplay._tcp"

        ref = pybonjour.DNSServiceBrowse(regtype=regtype, callBack=self._browse_callback)
        try:
            while True:
                wait_read(ref.fileno())
                pybonjour.DNSServiceProcessResult(ref)
        finally:
            ref.close()

    def _browse_callback(self, sdRef, flags, iface, errorCode, service, regtype, replydomain):
        self._to_resolve.put((iface, service, regtype, replydomain))

    def _resolve_loop(self):
        while True:
            iface, service, regtype, replydomain = self._to_resolve.get()

            ref = pybonjour.DNSServiceResolve(0, iface, service, regtype, replydomain, self._resolve_callback)
            try:
                wait_read(ref.fileno())
                pybonjour.DNSServiceProcessResult(ref)
            finally:
                ref.close()

    def _resolve_callback(self, ref, flags, iface_index, errorCode, fullname, host, port, txt):
        if errorCode != pybonjour.kDNSServiceErr_NoError:
            return

        if not (flags & pybonjour.kDNSServiceFlagsAdd):
            kind = "goodbye"
        else:
            kind = "hello"

        d, created = Device.get_or_create(fullname=fullname, defaults={'host': host, 'port': port, 'txt': txt})
        d.host = host
        d.port = port
        d.txt = txt
        d.save()

        broadcast(kind="network-device.%s" % kind,
            fullname = fullname,
            flags = flags,
            iface_index = iface_index,
            host = host,
            port = port,
            txt = txt,
            )

        print ' '.join(fullname, host, port, txt)

