import unittest
import mock

from pubbot.irc.handlers import JoinHandler, ChannelHandler, GhostHandler, FeedHandler, UserListHandler


dummy_signal = mock.Mock()


class TestJoinHandler(unittest.TestCase):

    def test_join(self):
        client = mock.Mock()
        j = JoinHandler("#example")
        with mock.patch("gevent.sleep"):
            j(client, None)

        client.msg.assert_called_with("ChanServ", "unban #example")
        self.assertEqual(
            client.send_message.call_args[0][0].params,
            "#example",
        )


class TestGhostHandler(unittest.TestCase):

    def test_ghost(self):
        client = mock.Mock()
        g = GhostHandler("fred", "password")
        g(client, None)

        client.msg.assert_called_with("NickServ", "ghost fred password")
        self.assertEqual(client.nick, "fred")


class TestFeedHandler(unittest.TestCase):

    def test_feed(self):
        f = FeedHandler(
            "fred", ["#example"],
            r'\x0303(?P<committer>\w+) \x0302(?P<repository>[\w\d]+) \x0310r(?P<revision>\d+) (?P<message>.*)\x0314',
            "pubbot.irc.tests.test_handlers.dummy_signal",
        )

        client = mock.Mock()
        msg = mock.Mock()
        msg.prefix = "fred!"
        msg.params = ["#example", '\x0303committer \x0302repository \x0310r100 message\x0314']
        f(client, msg)

        dummy_signal.send_robust.assert_called_with(None, committer="committer", repository="repository", revision='100', message="message")


class TestUserListHandler(unittest.TestCase):

    def test_353_366(self):
        network = {"#example": mock.Mock()}
        u = UserListHandler(network)
        msg = mock.Mock()
        msg.command = '353'
        msg.params = ['', '', '#example', 'fred', 'tommy']
        u(mock.Mock(), msg)

        msg = mock.Mock()
        msg.command = '366'
        msg.params = ['', '#example']
        u(mock.Mock(), msg)

        self.assertEqual(network['#example'].users, ['fred', 'tommy'])

    def test_join(self):
        network = {"#example": mock.Mock()}
        network['#example'].users = []

        u = UserListHandler(network)
        msg = mock.Mock()
        msg.command = 'JOIN'
        msg.prefix = "tommy!"
        msg.params = ['#example']

        client = mock.Mock()
        with mock.patch("gevent.sleep"):
            with mock.patch("pubbot.conversation.signals.join") as join:
                u(client, msg)
                join.send_robust(
                    sender=client,
                    channel=network['#example'],
                    user='tommy',
                    is_me=False,
                )

    def test_part(self):
        network = {"#example": mock.Mock()}
        network['#example'].users = ['tommy']

        u = UserListHandler(network)
        msg = mock.Mock()
        msg.command = 'PART'
        msg.prefix = "tommy!"
        msg.params = ['#example']

        client = mock.Mock()
        with mock.patch("pubbot.conversation.signals.leave") as leave:
            u(client, msg)
            leave.send_robust(
                sender=client,
                type="leave",
                channel=network['#example'],
                user='tommy',
            )


class TestChannelHandler(unittest.TestCase):

    def test_channel(self):
        channel = mock.Mock()
        channel.name = "#example"

        c = ChannelHandler(channel)

        client = mock.Mock()
        client.nick = "fred"

        msg = mock.Mock()
        msg.prefix = "dave!"
        msg.params = ["#example", 'fred: here is a test message']

        with mock.patch("pubbot.conversation.signals.message") as message:
            message.send_robust.return_value = [
                (None, None),
                (None, {'content': "hello"}),
                (None, RuntimeError()),
            ]
            c(client, msg)
            message.send_robust.assert_called_with(
                sender=client,
                source="dave",
                user="dave",
                channel=channel,
                content='here is a test message',
                direct=True,
            )
            channel.msg.assert_called_with("hello")
