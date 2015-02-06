# Copyright 2008-2015 the original author or authors
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
import ssl

import eventlet

import irc.bot
import irc.strings
import irc.connection

from pubbot import service
from pubbot.conversation import signals
from pubbot.irc.models import Network


logger = logging.getLogger(__name__)


"""
class JoinHandler(object):

    commands = ['001']

    def __init__(self, channel):
        self.channel = channel

    def __call__(self, client, msg):
        eventlet.sleep(5)
        client.msg('ChanServ', 'unban %s' % (self.channel, ))
        eventlet.sleep(10)
        client.send_message(message.Join(self.channel))
"""


class Bot(irc.bot.SingleServerIRCBot):

    def __init__(self, nickname, server, port, service):
        irc.bot.SingleServerIRCBot.__init__(
            self,
            [(server, port)],
            nickname,
            nickname,
            connect_factory=irc.connection.Factory(wrapper=ssl.wrap_socket),
        )
        self.service = service

    def do_ghost(self):
        self.connection.privmsg(
            'nickserv',
            'ghost %s %s' % (self.service.network.nick, self.service.network.nickserv_password),
        )

    def do_join(self):
        for channel in self.service.hannels:
            self.connection.join(channel.name)

    def on_mode(self, c, e):
        print "=======>"
        print e.source.nick
        print e.target
        print e.arguments
        print "<======="

    def on_invite(self, c, e):
        signals.invite.send(
            sender=self,
            invited_to=e.arguments[0],
            invited_by=e.source.nick,
        )

    def on_nicknameinuse(self, c, e):
        if self.service.network.nickserv_password:
            self.do_ghost()
        else:
            c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        if self.service.network.nickserv_password:
            self.do_ghost()
        else:
            self.do_join()

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        content = e.arguments[0]
        channel = e.target
        user = e.source

        if channel not in self.service.channels:
            return

        direct = False
        if ": " in content:
            u, msg = content.split(":", 1)
            if u.lower() == self.connection.get_nickname().lower():
                direct = True
                content = msg.lstrip()

        responses = signals.message.send(
            sender=self,
            source=user,
            user=user,
            channel=self.channel,
            content=content,
            direct=direct,
        )

        def sortfun(args):
            receiver, response = args
            weight = response.get('weight', 0)
            if response.get('has_side_effect', False):
                return 1000 + weight
            if response.get('useful', False):
                return 100 + weight
            return weight

        responses.sort(key=sortfun, reverse=True)

        if responses and 'content' in responses[0][1]:
            self.privmsg(channel, responses[0][1]['content'])


class ChannelService(service.BaseService):

    def __init__(self, channel):
        super(ChannelService, self).__init__(channel.name)
        self.channel = channel
        self.users = []
        self.subscribes_tags = set(t for t in channel.subscribes_tags.split(",") if t)
        self.blocks_tags = set(t for t in channel.blocks_tags.split(",") if t)

    def start_service(self):
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
        self.parent.client.privmsg(self.channel.name, message)

    def action(self, content):
        self.parent.client.action(self.channel.name, content)

    def notice(self, message):
        self.parent.client.notice(self.channel.name, message)


class NetworkService(service.BaseService):

    def __init__(self, network):
        super(NetworkService, self).__init__(network.server)
        self.network = network
        for room in self.network.rooms.all():
            self.add_child(ChannelService(room))

    def start_service(self):
        self.logger.info("Connecting to '%s' on port '%d'" % (self.network.server, int(self.network.port)))

        self.client = Bot(self.network.nick, self.network.server, int(self.network.port), self)
        eventlet.spawn(self.client.start)


class Service(service.BaseService):

    def __init__(self, *args, **kwargs):
        super(Service, self).__init__(*args, **kwargs)
        for network in Network.objects.all():
            self.add_child(NetworkService(network))
