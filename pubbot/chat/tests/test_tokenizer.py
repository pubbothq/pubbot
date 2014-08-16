import unittest

from pubbot.chat.tokenizer import tokenizer


class TestTokenizer(unittest.TestCase):

    def test_simple_sentence(self):
        self.assertEqual(
            list(tokenizer.split("a b c")),
            ["a", "b", "c"]
        )

    def test_simple_numbers(self):
        self.assertEqual(
            list(tokenizer.split("1.11 1 0.1")),
            ["1.11", "1", "0.1"]
        )

    def test_non_alphanum(self):
        self.assertEqual(
            list(tokenizer.split("foo, bar: baz")),
            ["foo,", "bar:", "baz"],
        )
