from unittest import mock

from django.test import TestCase

from pubbot.tasty import receivers
from pubbot.tasty.models import Link


class TestTastyReceivers(TestCase):

    def test_last_link_no_data(self):
        r = receivers.last_link_details(None, content="lastlink")
        self.assertEqual(r['content'], "I don't know any links :(")

    def test_last_link_no_logo(self):
        Link.objects.create(url="http://www.github.com/logo.png", title="")
        r = receivers.last_link_details(None, content="lastlink")
        self.assertEqual(r['content'], "URL isn't HTML or doesn't have a title tag")

    def test_last_link(self):
        Link.objects.create(url="http://www.github.com", title="GitHub")
        r = receivers.last_link_details(None, content="lastlink")
        self.assertEqual(r['content'], "GitHub")

    def test_got_chat_link(self):
        with mock.patch("eventlet.spawn") as spawn:
            receivers.got_chat_link(None, content="I really like http://google.com fonts")
        spawn.assert_called_with(receivers.process_link, "http://google.com")

    def test_got_chat_link_http(self):
        with mock.patch("eventlet.spawn") as spawn:
            receivers.got_chat_link(None, content="http://google.com")
        spawn.assert_called_with(receivers.process_link, "http://google.com")

    def test_got_chat_link_ssl(self):
        with mock.patch("eventlet.spawn") as spawn:
            receivers.got_chat_link(None, content="https://google.com")
        spawn.assert_called_with(receivers.process_link, "https://google.com")

    def test_got_chat_link_no_protocol(self):
        with mock.patch("eventlet.spawn") as spawn:
            receivers.got_chat_link(None, content="www.google.com")
        spawn.assert_called_with(receivers.process_link, "www.google.com")

    def test_process_link(self):
        with mock.patch("requests.head") as head:
            r = head.return_value
            r.headers = {
                "content-type": "text/html",
                "content-length": 99,
            }
            r.url = "http://localhost"

            with mock.patch("requests.get") as get:
                r2 = get.return_value
                r2.text = "<html><head><title>:)</title></head></html>"

                receivers.process_link("http://localhost")

        link = Link.objects.first()
        self.assertEqual(link.url, "http://localhost")
        self.assertEqual(link.content_type, "text/html")
        self.assertEqual(link.content_length, "99")
        self.assertEqual(link.hostname, "localhost")
        self.assertEqual(link.title, ":)")
