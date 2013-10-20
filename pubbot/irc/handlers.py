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

from geventirc.irc import Client, IRC_PORT
from geventirc import handlers, replycode, message

from pubbot.main.utils import broadcast, get_broadcast_group_for_message
from pubbot.irc.models import *
from pubbot.irc.tasks import mouth


class BotInterfaceHandler(object):

    """
    Parse notifications from bots into internal messages
    """

    commands = ['PRIVMSG']

    def __init__(self, botname, channels, regex, topic):
        self.botname = botname
        self.channels = channels
        self.regex = regex
        self._regex = re.compile(regex)
        self.kind = kind

    def __call__(self, client, msg):
        if self.botname != msg.prefix.split("!")[0]:
            return

        channel, content = msg.params[0], " ".join(msg.params[1:])
        if not channel in self.channels:
            return

        results = self._regex.search(content)
        if not results:
            return

        broadcast(
            kind=self.kind,
            **results.groupdict()
            )


class UserListHandler(object):

    commands = ['353', '366', 'JOIN', 'PART']

    def __init__(self):
        self.incoming = {}

    def get_room(self, client, channel):
        return Room.objects.get(server__server=client.hostname, name=channel)

    def __call__(self, client, msg):
        if msg.command == '353':
            channel = msg.params[2]
            users = self.incoming.setdefault(channel, [])
            users.extend(msg.params[3:])

        elif msg.command == '366':
            channel = msg.params[1]

            room = self.get_room(client, channel)

            if not channel in self.incoming:
                room.participants.clear()
                return

            # Eject user not present
            users = [u.lstrip("@").lstrip("+") for u in self.incoming[channel]]
            room.participants.remove(*room.participants.exclude(name__in=users))

            # Record user presence
            users_from_db = [user.name for user in room.participants.all()]
            for user in self.incoming[channel]:
                if user.startswith("@"):
                    user = user[1:]
                    has_op = True
                if user.startswith("+"):
                    user = user[1:]
                    has_voice = True

                if not user in users_from_db:
                    print "Adding %s to %s" % (user, room)
                    try:
                        u = room.server.users.get(name=user)
                    except User.DoesNotExist:
                        u = User(name=user, network=room.server)
                        u.save()
                    room.participants.add(u)
                    room.save()

            del self.incoming[channel]

        elif msg.command == 'JOIN':
            user = msg.prefix.split("!")[0]
            channel = msg.params[0]

            room = self.get_room(client, channel)
            if not room.participants.filter(name=user).exists():
                print "Adding %s" % user
                try:
                    u = room.server.users.get(name=user)
                except User.DoesNotExist:
                    u = User(name=user, network=room.server)
                    u.save()
                room.participants.add(u)
                room.save()

            broadcast(
                kind="chat.irc.%s.join" % channel,
                user = user,
                channel = channel,
                )

        elif msg.command == 'PART':
            user = msg.prefix.split("!")[0]
            channel = msg.params[0]

            print "Removing %s" % user
            room = self.get_room(client, channel)
            room.participants.remove(*room.participants.filter(name=user))

            broadcast(
                kind ="chat.irc.%s.leave" % channel,
                user = user,
                channel = channel,
                )


class InviteProcessor(object):

    commands = ['INVITE']

    def __call__(self, client, msg):
        broadcast(
            kind = "chat.irc.%s.invite" % msg.params[1],
            invited_to = msg.params[1],
            invited_by = msg.prefix.split("!")[0],
            )


class ConversationHandler(object):

    commands = ['PRIVMSG']

    def __init__(self):
        self.channels = {}

    def __call__(self, client, msg):
        channel, content = msg.params[0], " ".join(msg.params[1:])
        user = msg.prefix.split("!")[0]

        scene = Room.objects.get(server__server=client.hostname, name=channel)

        # cache this with tuple of (hostname, room, name) ?
        try:
            participant = scene.participants.get(name=user)
        except User.DoesNotExist:
            print "User '%s' not in roster" % user
            participant = None

        handlers = get_broadcast_group_for_message(
            kind = "chat.irc.%s.chat" % channel,
            scene_id = getattr(scene, "pk", None),
            participant_id = getattr(participant, "pk", None),
            source = user,
            channel = channel,
            content = content,
            )

        (handlers | mouth.s(server=client.hostname, channel=channel)).apply_async()

