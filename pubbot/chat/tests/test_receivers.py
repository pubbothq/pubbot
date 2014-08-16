from django.test import TestCase
from pubbot.chat.receivers import mutter, learn


class TestMutter(TestCase):

    def setUp(self):
        learn(None, content="Happiness is important")

    def test_can_reply(self):
        self.assertEqual(
            mutter(None, content="Chocolate is important", direct=True)['content'],
            "Happiness is important",
        )
