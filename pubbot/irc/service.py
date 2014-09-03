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

import gevent

from geventirc import irc
from geventirc import handlers, replycode, message

from pubbot import service
from pubbot.conversation import signals
from pubbot.irc.models import Network
from pubbot.irc.handlers import GhostHandler, UserListHandler, InviteProcessor, ChannelHandler, JoinHandler


logger = logging.getLogger(__name__)


class Client(irc.Client):

    def _send_loop(self):
        while True:
            command = force_bytes(self._send_queue.get())
            self.logger.debug('send: %r', command[:-2])
            try:
                self._socket.sendall(command)
            except Exception as e:
                self.logger.exception("Client._send_loop failed")
                gevent.spawn(self.reconnect)
                return


class Ping(message.Command):

    def __init__(self, daemon, prefix=None):
        super(Ping, self).__init__(daemon, prefix=prefix)


class Notice(message.Command):

    def __init__(self, to, msg, prefix=None):
        super(Notice, self).__init__([to, msg], prefix=prefix)


class ChannelService(service.BaseService):

    def __init__(self, channel):
        super(ChannelService, self).__init__(channel.name)
        self.channel = channel
        self.users = []
        self.subscribes_tags = set(t for t in channel.subscribes_tags.split(",") if t)
        self.blocks_tags = set(t for t in channel.blocks_tags.split(",") if t)

    def start_service(self):
        self.parent.client.add_handler(ChannelHandler(self))
        self.parent.client.add_handler(JoinHandler(self.channel.name))
        signals.say.connect(self._maybe_say)

    def stop_service(self):
        signals.say.disconnect(self._maybe_say)

    def _maybe_say(self, sender, content, tags=None, action=False, notice=False, **kwargs):
        tags = set(tags if tags else [])

        if not self.blocks_tags.isdisjoint(tags):
            return False

        if self.subscribes_tags.isdisjoint(tags):
            return False

        if action:
            self.action(content)
        elif notice:
            self.notice(content)
        else:
            self.msg(content)

        return True

    def msg(self, message):
        self.parent.client.msg(self.channel.name, message)

    def action(self, content):
        self.parent.client.send_message(message.Me(self.channel.name, content))

    def notice(self, message):
        self.parent.client.send_message(Notice(self.channel.name, message))


class NetworkService(service.BaseService):

    def __init__(self, network):
        super(NetworkService, self).__init__(network.server)
        self.network = network

    def start_service(self):
        self.logger.info("Connecting to '%s' on port '%d'" % (self.network.server, int(self.network.port)))
        self.client = Client(self.network.server, self.network.nick, port=str(self.network.port), ssl=self.network.ssl)

        self.client.add_handler(handlers.print_handler)
        self.client.add_handler(handlers.ping_handler, 'PING')

        if self.network.nickserv_password:
            self.client.add_handler(GhostHandler(self.network.nick, self.network.nickserv_password))
        else:
            self.client.add_handler(handlers.nick_in_use_handler, replycode.ERR_NICKNAMEINUSE)

        self.client.add_handler(UserListHandler(self))
        self.client.add_handler(InviteProcessor())

        # Channels to join
        for room in self.network.rooms.all():
            self.add_child(ChannelService(room))

        self.client.start()

        self._ping_loop_greenlet = gevent.spawn(self._ping_loop)

    def stop_service(self):
        self._ping_loop_greenlet.kill()

    def _ping_loop(self):
        while True:
            gevent.sleep(120)
            self.client.send_message(Ping(self.client.nick))


class Service(service.BaseService):

    def __init__(self, *args, **kwargs):
        super(Service, self).__init__(*args, **kwargs)
        for network in Network.objects.all():
            self.add_child(NetworkService(network))
