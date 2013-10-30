# coding: utf-8

import urlparse

from bs4 import BeautifulSoup
import requests

from pubbot.conversation.tasks import parse_chat_text
from pubbot.main.celery import app
from pubbot.tasty.models import Link

@parse_chat_text(r'''(?xi)\b(?P<url>(?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''')
def got_chat_link(msg, url):
    # Once we have identified a URL we immediately re-queue it - we don't want to block the chatting processes
    process_link.delay(url)


@parse_chat_text(r'^(lastlink)|(last link)')
def last_link_details(msg):
    link = Link.objects.order_by('-first_seen')[0]
    return {
        'content': link.title or "URL isn't HTML or doesn't have a title tag",
        }


@app.task
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

