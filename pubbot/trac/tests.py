import mock
import unittest

from pubbot.trac import receivers


DUMMY_FORM = """
<html><head><title>Trac</title></head><body>
<input type="hidden" name="__FORM_TOKEN" value="FOOBAR" />
</body></html>
"""


class TestRaiseTicket(unittest.TestCase):

    def test_raise_ticket(self):
        with mock.patch("requests.Session") as Session:
            Session.return_value.get.return_value.text = DUMMY_FORM
            Session.return_value.post.return_value.url = 'http://localhost/sometrac/ticket/1'

            r = receivers.raise_ticket(None, user='fred', content="newticket: Raise a ticket")
            self.assertEqual(r['content'], 'http://localhost/sometrac/ticket/1')
