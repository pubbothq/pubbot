# coding: utf-8

import urlparse

from bs4 import BeautifulSoup
import requests
import gevent

from pubbot.tasty.models import Link
from pubbot.conversation import chat_receiver


@chat_receiver(r'''(?xi)\b(?P<url>(?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''')
def got_chat_link(msg, url):
    gevent.spawn(process_link, url)


@chat_receiver(r'^(lastlink)|(last link)')
def last_link_details(msg):
    link = Link.objects.order_by('-first_seen')[0]
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
    l.content_size = r.headers.get("content-type", -1)
    l.hostname = urlparse.urlparse(r.url).hostname

    if l.content_type.startswith("text/html"):
        soup = BeautifulSoup(requests.get(r.url).text)
        l.title = soup.title.string

    l.save()
