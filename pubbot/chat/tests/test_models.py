from django.test import TestCase

from pubbot.chat.training import Trainer
from pubbot.chat.models import Grouping


class TestIterRandomGroupings(TestCase):

    def setUp(self):
        with Trainer() as trainer:
            trainer.learn_string("I am happy to see you")

    def test_iter_by_token(self):
        groupings = list(Grouping.iter_random_groupings(["happy"]))
        self.assertEqual(len(groupings), 1)
        self.assertEqual(groupings[0].token1.token, "I")
        self.assertEqual(groupings[0].token2.token, "am")
        self.assertEqual(groupings[0].token3.token, "happy")

    def test_iter_by_stem(self):
        groupings = list(Grouping.iter_random_groupings(["happiness"]))
        self.assertEqual(len(groupings), 1)
        self.assertEqual(groupings[0].token1.token, "I")
        self.assertEqual(groupings[0].token2.token, "am")
        self.assertEqual(groupings[0].token3.token, "happy")
