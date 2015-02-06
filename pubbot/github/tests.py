from unittest import mock
import unittest

from pubbot.github import receivers


class TestPushToCommit(unittest.TestCase):

    def test_push(self):
        with mock.patch("pubbot.github.receivers.commit") as commit:
            payload = mock.Mock()
            payload.payload = {
                "commits": [
                    {"distinct": False},
                    {"distinct": True, "sha": "abc", "message": "hello", "author": {"name": "Pubbot"}},
                ]
            }
            receivers.push_to_commit(None, payload)

            commit.send.assert_called_with(
                revision="abc",
                message="hello",
                committer="Pubbot",
            )


class TestPushToChat(unittest.TestCase):

    def test_push(self):
        with mock.patch("pubbot.github.receivers.say") as say:
            payload = mock.Mock()
            payload.repo = ('pubbothq', 'pubbot')
            payload.payload = {
                "commits": [
                    {"distinct": False},
                    {"distinct": True, "sha": "abc", "message": "hello", "author": {"name": "Pubbot"}},
                ]
            }
            receivers.push_to_chat(None, payload)

            say.assert_called_with(
                content="\x0303Pubbot \x0302pubbothq/pubbot \x0310abc\x0314\x0f: hello ...",
                tags=['github:pubbothq/pubbot', 'github:pubbothq']
            )
