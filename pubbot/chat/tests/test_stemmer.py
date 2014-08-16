import unittest

from pubbot.chat.stemmer import stemmer


class TestTokenizer(unittest.TestCase):

    def test_simple_sentence(self):
        self.assertEqual(stemmer.stem("happiness"), "happi")
