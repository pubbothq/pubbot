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
from pubbot.main.protocols.line_protocol import LineProtocol
from pubbot.kismet import handlers


class KismetConnection(LineProtocol):

    def __init__(self, hostname, port, handlers=None):
        super(KismetConnection, self).__init__(hostname, port)
        self.cmd = 1
        self.deferreds = {}
        self.capabilities = {}
        self.handlers = []
        if handlers:
            for h in handlers:
                self.add_handler(h)

    def add_handler(self, callable):
        self.handlers.append(callable)

    def subscribe(self, proto, fields):
        proto = proto.upper()
        self.send("!0 ENABLE %s %s" % (proto, ",".join(fields)))

    def unsubscribe(self, proto):
        proto = proto.upper()
        self.send("!0 REMOVE %s" % p)

    def start(self):
        super(KismetConnection, self).start()

    def line_received(self, line):
        if not line.startswith("*"):
            print ("Kismet: Abnormal data '%s'" % data)
            return
        data = line[1:]
        k, v = data.split(": ", 1)

        parsed = getattr(self, "parse_" + k, self._parse_identity)(v)

        for handler in self.handlers:
            if hasattr(handler, "handles") and not k in handler.handles:
                continue
            handler(k, parsed)

        # BACKWARDS COMPATIBILITY
        # NERF ASAP
        process = getattr(self, "kismet_" + k, self._kismet_noop)(*parsed)

    def _parse_identity(self, data):
        delim = False
        output = [""]
        for c in data:
            if c == "\001":
                delim = not delim
            elif c == ' ' and not delim:
                output.append("")
            else:
                output[-1] = output[-1] + c

        if not output[-1]:
            del output[-1]

        return output

    def _kismet_noop(self, *data):
        pass

    def parse_KISMET(self, data):
        return data.split(" ")

    def kismet_KISMET(
        self,
        version,
        start_time,
        server_name,
        build_revision,
        unknown1,
        unknown2,
            unknown3):
        self.version = version
        self.start_time = start_time
        self.server_name = server_name
        self.build_revision = build_revision
        self.unknown1 = unknown1
        self.unknown2 = unknown2
        self.unknown3 = unknown3

    def parse_PROTOCOLS(self, data):
        return [data.split(",")]

    def kismet_PROTOCOLS(self, protocols):
        for protocol in protocols:
            self.send("!0 CAPABILITY %s" % protocol.upper())
        # self.subscribe("NETWORK", ["bssid", "type", "ssid", "channel", "lasttime"])
        self.subscribe("CLIENT",
                       ["bssid", "mac", "type", "lasttime", "datapackets"])

    # def kismet_ACK(self, cmdid):
    #    if cmdid in self.deferreds:
    #        self.deferreds[cmdid].callback(True)
    #        del self.deferreds[cmdid]

    # def kismet_ERROR(self, cmdid, text):
    #    if cmdid in self.deferreds:
    # self.deferreds[cmdid].errback(Failure(text))
    #        del self.deferreds[cmdid]

    def parse_CAPABILITY(self, data):
        proto, params = data.split(" ", 1)
        return [proto, list(params.split(","))]

    def kismet_CAPABILITY(self, capability, fields):
        self.capabilities[capability] = fields


class Bootstep(bootsteps.StartStopStep):

    queue = 'kismet'

    def start(self, worker):
        print "Connecting to kistmet"
        self.connection = KismetConnection('192.168.0.142', 2501)
        self.connection.add_handler(handlers.NetworkFinder())
        self.connection.add_handler(handlers.ClientFinder())
        self.connection.start()

    def stop(self, worker):
        self.connection.stop()
