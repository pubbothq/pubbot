from django.test import TestCase
from pubbot.chat import scoring


class TestBaseScorer(TestCase):

    def test_score(self):
        scorer = scoring.BaseScorer()
        self.assertRaises(NotImplementedError, scorer.score, [])
