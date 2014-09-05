import mock

from django.test import TestCase
from django.core.cache import caches

from pubbot.vcs import receivers


class TestWoot(TestCase):

    def test_not_woot(self):
        with mock.patch("pubbot.vcs.receivers.say") as say:
            receivers.svnwoot(None, 1336)
            self.assertEqual(say.called, 0)

    def test_woot(self):
        with mock.patch("pubbot.vcs.receivers.say") as say:
            receivers.svnwoot(None, 1337)
            say.assert_called_with(content="r1337 - \o/")


class TestNotLikely(TestCase):

    def test_not_likely(self):
        with mock.patch("pubbot.vcs.receivers.say") as say:
            receivers.notlikely(None, "The final version of my doc", "fred")
            say.assert_called_with(content="Final? Not likely, fred")


class TestMultiKill(TestCase):

    def setUp(self):
        self.patchers = []

        def _(s):
            patcher = mock.patch(s)
            self.patchers.append(patcher.stop)
            return patcher.start()

        self.date = _("pubbot.vcs.receivers.date")
        self.date.today.return_value.weekday.return_value = 2
        self.say = _("pubbot.vcs.receivers.say")
        self.cache = caches['default']
        self.cache.clear()

    def cleanUp(self):
        [stop() for stop in self.patchers]
        self.cache.clear()

    def test_weekend(self):
        self.date.today.return_value.weekday.return_value = 5
        receivers.multikill(None, "fred")
        self.assertEqual(self.say.called, 0)

    def test_end_of_spree(self):
        self.cache.set("multikill_killer", "tommy")
        receivers.multikill(None, "fred")
        self.assertEqual(self.cache.get("multikill_kills"), 1)
        self.assertEqual(self.cache.get("multikill_killer"), "fred")
        self.say.assert_called_with(content="fred ended the killing spree! poor tommy", tags=['multikill'])

    def test_double_kill(self):
        self.cache.set("multikill_kills", 1)
        receivers.multikill(None, "fred")
        self.say.assert_called_with(content="Double Kill", tags=['multikill'])

    def test_multi_kill(self):
        self.cache.set("multikill_kills", 2)
        receivers.multikill(None, "fred")
        self.say.assert_called_with(content="Multi Kill", tags=['multikill'])

    def test_ultra_kill(self):
        self.cache.set("multikill_kills", 3)
        receivers.multikill(None, "fred")
        self.say.assert_called_with(content="Ultra Kill", tags=['multikill'])

    def test_mega_kill(self):
        self.cache.set("multikill_kills", 4)
        receivers.multikill(None, "fred")
        self.say.assert_called_with(content="Megakill", tags=['multikill'])

    def test_monster_kill(self):
        self.cache.set("multikill_kills", 5)
        receivers.multikill(None, "fred")
        self.say.assert_called_with(content="MONSTTTTTTTEEER KILLLLL", tags=['multikill'])
