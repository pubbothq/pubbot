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
from geventirc.irc import Client
from geventirc import handlers, replycode

from pubbot.irc.models import Network
from pubbot.irc.handlers import GhostHandler, UserListHandler, InviteProcessor, ConversationHandler, JoinHandler


# FIXME: It would be nice if this global didn't exist..
clients = {}


class Bootstep(bootsteps.StartStopStep):

    queue = 'irc'
    running = False

    def start(self, worker):
        print "Starting irc services"
        self.group = []
        for network in Network.objects.all():
            print "Connecting to '%s' on port '%d'" % (network.server, int(network.port))

            client = Client(network.server, network.nick,
                            port=str(network.port), ssl=network.ssl)
            clients[network.server] = client

            client.add_handler(handlers.print_handler)

            # House keeping handlers
            client.add_handler(handlers.ping_handler, 'PING')
            if network.nickserv_password:
                client.add_handler(
                    GhostHandler(network.nick, network.nickserv_password))
            else:
                client.add_handler(
                    handlers.nick_in_use_handler, replycode.ERR_NICKNAMEINUSE)
            client.add_handler(UserListHandler())
            client.add_handler(InviteProcessor())

            # Channels to join
            for room in network.rooms.all():
                client.add_handler(JoinHandler(room.name))

            # Inject conversation data into queue
            client.add_handler(ConversationHandler())

            client.start()

            self.group.append(client)

    def stop(self, worker):
        print "Stopping irc services"
        [c.stop() for c in self.group]
