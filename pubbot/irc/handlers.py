import re

from geventirc.irc import Client, IRC_PORT
from geventirc import handlers, replycode, message

from pubbot.main.utils import broadcast, get_broadcast_group_for_message
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
        self.users = {}
        self.incoming = {}

    def __call__(self, client, msg):
        if msg.command == '353':
            channel = msg.params[2]
            users = self.incoming.setdefault(channel, [])
            users.extend(msg.params[3:])

        elif msg.command == '366':
            channel = msg.params[1]
            if channel in self.incoming:
                self.users[channel] = self.incoming[channel]
                del self.incoming[channel]
            else:
                self.users[channel] = []

        elif msg.command == 'JOIN':
            user = msg.prefix.split("!")[0]
            channel = msg.params[0]
            chan = self.users.setdefault(channel, [])
            if not user in chan:
                chan.append(user)

            broadcast(
                kind="chat.irc.%s.join" % channel,
                user = user,
                channel = channel,
                )

        elif msg.command == 'PART':
            user = msg.prefix.split("!")[0]
            channel = msg.params[0]
            chan = self.users.setdefault(channel, [])
            if user in chan:
                chan.remove(user)

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

        handlers = get_broadcast_group_for_message(
            kind = "chat.irc.%s.chat" % channel,
            user = user,
            channel = channel,
            content = content,
            )
        (handlers | mouth.s(server=client.hostname, channel=channel)).apply_async()

