# coding: utf-8

from urllib import parse

from bs4 import BeautifulSoup
import requests
import eventlet

from pubbot.tasty.models import Link
from pubbot.conversation import chat_receiver


@chat_receiver(r'''(?xi)\b(?P<url>(?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''')
def got_chat_link(sender, url, **kwargs):
    eventlet.spawn(process_link, url)


@chat_receiver(r'^(lastlink)|(last link)')
def last_link_details(sender, **kwargs):
    link = Link.objects.order_by('-first_seen').first()
    if not link:
        return {
            'content': 'I don\'t know any links :(',
        }
    return {
        'content': link.title or "URL isn't HTML or doesn't have a title tag",
    }


def process_link(url):
    r = requests.head(url, allow_redirects=True)

    try:
        l = Link.objects.get(url=r.url)
    except Link.DoesNotExist:
        l = Link(url=r.url)
        l.save()

    l.content_type = r.headers.get("content-type", "")
    l.content_length = r.headers.get("content-length", -1)
    l.hostname = parse.urlparse(r.url).hostname

    if l.content_type.startswith("text/html"):
        soup = BeautifulSoup(requests.get(r.url).text)
        l.title = soup.title.string

    l.save()
