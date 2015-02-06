from unittest import mock
import unittest

from pubbot.quizbot.receivers import quizbot_request


class TestQuizbot(unittest.TestCase):

    def test_simple_request(self):
        with mock.patch("requests.get") as get:
            get.return_value.json.return_value = {"answer": "hello"}
            r = quizbot_request(None, content="quizbot: foo bar")
        self.assertEqual(r['content'], 'hello')

    def test_log_error(self):
        with mock.patch("requests.get") as get:
            get.side_effect = Exception("Sad :(")
            r = quizbot_request(None, content="quizbot: foo bar")
        self.assertEqual(r, None)
