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

import re
import logging

import gevent

from geventirc import replycode, message

from django.utils.module_loading import import_string

from pubbot.conversation import signals


logger = logging.getLogger(__file__)


class JoinHandler(object):

    commands = ['001']

    def __init__(self, channel):
        self.channel = channel

    def __call__(self, client, msg):
        gevent.sleep(5)
        client.msg('ChanServ', 'unban %s' % (self.channel, ))
        gevent.sleep(10)
        client.send_message(message.Join(self.channel))


class GhostHandler(object):

    commands = [
        '001',
        replycode.ERR_NICKNAMEINUSE,
        replycode.ERR_NICKCOLLISION,
    ]

    def __init__(self, nick, password):
        self.nick = nick
        self.password = password

    def __call__(self, client, msg):
        client.msg('NickServ', 'ghost %s %s' % (self.nick, self.password))
        client.nick = self.nick


class FeedHandler(object):

    """
    Parse notifications from bots into internal messages
    """

    commands = ['PRIVMSG']

    def __init__(self, botname, channels, regex, signal):
        self.botname = botname
        self.channels = channels
        self.regex = re.compile(regex)
        self.signal = import_string(signal)

    def __call__(self, client, msg):
        if self.botname != msg.prefix.split("!")[0]:
            return

        channel, content = msg.params[0], " ".join(msg.params[1:])
        if channel not in self.channels:
            return

        results = self.regex.search(content)
        if not results:
            return

        self.signal.send_robust(None, **results.groupdict())


class UserListHandler(object):

    commands = ['353', '366', 'JOIN', 'PART', 'KICK', 'QUIT']

    def __init__(self, network):
        self.network = network
        self.incoming = {}

    def __call__(self, client, msg):
        if msg.command == '353':
            channel = self.network[msg.params[2]]
            users = self.incoming.setdefault(channel.name, [])
            users.extend(msg.params[3:])

        elif msg.command == '366':
            channel = self.network[msg.params[1]]

            if channel.name not in self.incoming:
                channel.users = []
                return

            channel.users = [u.lstrip("@").lstrip("+") for u in self.incoming[channel.name]]
            del self.incoming[channel.name]

        elif msg.command == 'JOIN':
            user = msg.prefix.split("!")[0]
            if client.nick == user:
                return
            channel = self.network[msg.params[0]]

            channel.users.append(user)

            # De-bounce the user leaving immediately - like a bot ban.
            gevent.sleep(1)
            if user not in channel.users:
                return

            signals.join.send_robust(
                sender=client,
                channel=channel,
                user=user,
                is_me=(user == client.nick),
            )

        elif msg.command == 'PART':
            user = msg.prefix.split("!")[0]
            channel = self.network[msg.params[0]]
            self.remove(client, channel, user, "leave")

        elif msg.command == 'KICK':
            kicker = msg.prefix.split("!")[0]
            channel = self.network[msg.params[0]]
            kicked = msg.params[1]
            self.remove(client, channel, kicked, 'kicked', kicker=kicker)

        elif msg.command == 'QUIT':
            user = msg.prefix.split("!")[0]

            for room in self.network.values():
                if user in room.users:
                    self.remove(client, self.network[room], user, "quit")

    def remove(self, client, channel, user, type, **kwargs):
        print "Removing %s" % user

        channel.users.remove(user)

        signals.leave.send_robust(
            sender=client,
            type=type,
            user=user,
            channel=channel,
            **kwargs
        )


class InviteProcessor(object):

    commands = ['INVITE']

    def __call__(self, client, msg):
        signals.invite.send_robust(
            sender=client,
            invited_to=msg.params[1],
            invited_by=msg.prefix.split("!")[0],
        )


class ChannelHandler(object):

    commands = ['PRIVMSG']

    def __init__(self, channel):
        self.channel = channel

    def __call__(self, client, msg):
        channel, content = msg.params[0], " ".join(msg.params[1:])
        user = msg.prefix.split("!")[0]

        if channel != self.channel.name:
            return

        direct = False
        if ": " in content:
            u, msg = content.split(": ", 1)
            if u == client.nick:
                direct = True
                content = msg

        responses = signals.message.send_robust(
            sender=client,
            source=user,
            user=user,
            channel=self.channel,
            content=content,
            direct=direct,
        )

        valid_responses = []
        for receiver, response in responses:
            if not response:
                continue
            if isinstance(response, Exception):
                print response
                logger.exception(response)
                continue
            valid_responses.append(response)

        if valid_responses:
            self.channel.msg(valid_responses[0]['content'])
