import mock

from django.test import TestCase
from pubbot.chat.receivers import mutter, learn


class TestMutter(TestCase):

    def setUp(self):
        learn(None, content="Happiness is important")

    def test_dont_learn_if_directed(self):
        learn(None, content="Time is but a window", direct=True)
        self.assertEqual(
            mutter(None, content="Time is but a window", direct=True)['content'],
            'You make no sense',
        )

    def test_dont_reply_if_not_directed(self):
        with mock.patch("random.random") as random:
            random.return_value = 0
            self.assertEqual(
                mutter(None, content="Chocolate is important", direct=False),
                None,
            )

    def test_can_reply(self):
        self.assertEqual(
            mutter(None, content="Chocolate is important", direct=True)['content'],
            "Happiness is important",
        )
