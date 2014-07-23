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

import logging

from geventirc.irc import Client
from geventirc import handlers, replycode, message

from pubbot import service
from pubbot.irc.models import Network
from pubbot.irc.handlers import GhostHandler, UserListHandler, InviteProcessor, ConversationHandler, JoinHandler


logger = logging.getLogger(__name__)


class Notice(message.Command):

    def __init__(self, to, msg, prefix=None):
        super(Notice, self).__init__([to, msg], prefix=prefix)


class ChannelService(service.BaseService):

    def __init__(self, channel):
        super(ChannelService, self).__init__(channel.name)
        self.channel = channel

    def start(self):
        self.parent.add_handler(JoinHandler(self.channel.name))

    def say(self, message):
        self.parent.client.msg(self.channel.name, message.encode('utf-8'))

    def action(self, message):
        self.parent.client.send_message(message.Me(self.channel.name, message.encode('utf-8')))

    def notice(self, message):
        self.parent.client.send_message(Notice(self.channel.name, message.encode('utf-8')))


class NetworkService(service.BaseService):

    def __init__(self, network):
        super(NetworkService, self).__init__(network.server)
        self.network = network

    def start_service(self):
        logger.info("Connecting to '%s' on port '%d'" % (self.network.server, int(self.network.port)))
        self.client = Client(self.network.server, self.network.nick, port=str(self.network.port), ssl=self.network.ssl)

        # self.client.add_handler(handlers.print_handler)
        self.client.add_handler(handlers.ping_handler, 'PING')

        if self.network.nickserv_password:
            self.client.add_handler(GhostHandler(self.network.nick, self.network.nickserv_password))
        else:
            self.client.add_handler(handlers.nick_in_use_handler, replycode.ERR_NICKNAMEINUSE)

        self.client.add_handler(UserListHandler())
        self.client.add_handler(InviteProcessor())

        # Channels to join
        for room in self.network.rooms.all():
            self.add_child(ChannelService(room))

        # Inject conversation data into queue
        self.client.add_handler(ConversationHandler())


class Service(service.BaseService):

    def start_service(self):
        print "Starting irc services"
        for network in Network.objects.all():
            self.add_child(NetworkService(network))
