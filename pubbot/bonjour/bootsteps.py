# Copyright 2008-2013 the original author or authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from celery import bootsteps
from gevent.socket import wait_read, timeout
from gevent.queue import Queue
from gevent.pool import Group
import pybonjour

from pubbot.main.utils import broadcast


class Bootstep(bootsteps.StartStopStep):

    queue = 'bonjour'

    def start(self, worker):
        print "Starting bonjour..."
        self._to_resolve = Queue()

        self.group = Group()
        self.group.spawn(self._browse_loop)
        self.group.spawn(self._resolve_loop)

    def stop(self, worker):
        print "Stopping bonjour..."
        self.group.kill()

    def _browse_loop(self):
        # FIXME: Would be nice to detect more than just airplay...
        regtype = "_airplay._tcp"

        ref = pybonjour.DNSServiceBrowse(
            regtype=regtype, callBack=self._browse_callback)
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

            ref = pybonjour.DNSServiceResolve(
                0, iface, service, regtype, replydomain, self._resolve_callback)
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

        d, created = Device.get_or_create(
            fullname=fullname, defaults={'host': host, 'port': port, 'txt': txt})
        d.host = host
        d.port = port
        d.txt = txt
        d.save()

        broadcast(kind="network-device.%s" % kind,
                  fullname=fullname,
                  flags=flags,
                  iface_index=iface_index,
                  host=host,
                  port=port,
                  txt=txt,
                  )

        print ' '.join(fullname, host, port, txt)
