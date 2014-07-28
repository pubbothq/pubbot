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

from pubbot.irc.models import Network, Room, User
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


class BotInterfaceHandler(object):

    """
    Parse notifications from bots into internal messages
    """

    commands = ['PRIVMSG']

    def __init__(self, botname, channels, regex, topic, kind):
        self.botname = botname
        self.channels = channels
        self.regex = regex
        self._regex = re.compile(regex)
        self.kind = kind

    def __call__(self, client, msg):
        if self.botname != msg.prefix.split("!")[0]:
            return

        channel, content = msg.params[0], " ".join(msg.params[1:])
        if channel not in self.channels:
            return

        results = self._regex.search(content)
        if not results:
            return

        # broadcast(
        #     kind=self.kind,
        #     **results.groupdict()
        # )


class UserListHandler(object):

    commands = ['353', '366', 'JOIN', 'PART', 'KICK', 'QUIT']

    def __init__(self):
        self.incoming = {}

    def get_scene(self, client, channel):
        return Room.objects.get(server__server=client.hostname, name=channel)

    def __call__(self, client, msg):
        if msg.command == '353':
            channel = msg.params[2]
            users = self.incoming.setdefault(channel, [])
            users.extend(msg.params[3:])

        elif msg.command == '366':
            channel = msg.params[1]

            scene = self.get_scene(client, channel)

            if channel not in self.incoming:
                scene.participants.clear()
                return

            # Eject user not present
            users = [u.lstrip("@").lstrip("+") for u in self.incoming[channel]]
            scene.participants.remove(
                *scene.participants.exclude(name__in=users))

            # Record user presence
            users_from_db = [user.name for user in scene.participants.all()]
            for user in self.incoming[channel]:
                if user.startswith("@"):
                    user = user[1:]
                    # has_op = True
                if user.startswith("+"):
                    user = user[1:]
                    # has_voice = True

                if user not in users_from_db:
                    print "Adding %s to %s" % (user, scene)
                    try:
                        u = scene.server.users.filter(name=user)[0]
                    except (User.DoesNotExist, IndexError):
                        u = User(name=user, network=scene.server)
                        u.save()
                    scene.participants.add(u)
                    scene.save()

            del self.incoming[channel]

        elif msg.command == 'JOIN':
            user = msg.prefix.split("!")[0]
            channel = msg.params[0]

            scene = self.get_scene(client, channel)
            if not scene.participants.filter(name=user).exists():
                print "Adding %s" % user
                try:
                    u = scene.server.users.get(name=user)
                except User.DoesNotExist:
                    u = User(name=user, network=scene.server)
                    u.save()
                scene.participants.add(u)
                scene.save()

            signals.join.send_robust(
                sender=client,
                scene_id=scene.pk,
                user=user,
                channel=channel,
                is_me=(user == client.nick),
            )

        elif msg.command == 'PART':
            user = msg.prefix.split("!")[0]
            channel = msg.params[0]
            self.remove(client, channel, user, "leave")

        elif msg.command == 'KICK':
            kicker = msg.prefix.split("!")[0]
            channel = msg.params[0]
            kicked = msg.params[1]
            self.remove(client, channel, kicked, 'kicked', kicker=kicker)

        elif msg.command == 'QUIT':
            user = msg.prefix.split("!")[0]

            u = Network.objects.get(
                server=client.hostname).users.get(name=user)
            for scene in u.scenes.all():
                self.remove(client, scene.name, user, "quit")

    def remove(self, client, channel, user, type, **kwargs):
        print "Removing %s" % user

        scene = self.get_scene(client, channel)
        scene.participants.remove(*scene.participants.filter(name=user))

        signals.leave.send_robust(
            sender=client,
            type=type,
            scene_id=scene.pk,
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

        print msg

        scene = Room.objects.get(server__server=client.hostname, name=channel)

        # cache this with tuple of (hostname, room, name) ?
        try:
            participant = scene.participants.get(name=user)
        except User.DoesNotExist:
            print "User '%s' not in roster" % user
            participant = None

        direct = False
        if ": " in content:
            user, msg = content.split(": ", 1)
            if user == client.nick:
                direct = True
                content = msg

        responses = signals.message.send_robust(
            sender=client,
            scene_id=getattr(scene, "pk", None),
            participant_id=getattr(participant, "pk", None),
            source=user,
            channel=channel,
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
