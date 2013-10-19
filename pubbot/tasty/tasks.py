import urlparse

from bs4 import BeautifulSoup
import requests

from pubbot.conversation.tasks import parse_chat_text
from pubbot.main.celery import app


@parse_chat_text(r"""(?i)\b(?P<url>(?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""")
def got_chat_link(msg, link):
    # Once we have identified a URL we immediately re-queue it - we don't want to block the chatting processes
    process_link.delay(link)


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
    l.hostname = urlparse(r.url).hostname

    if l.content_type.startswith("text/html"):
        soup = BeautifulSoup(requests.get(r.url).text)
        l.title = soup.title.string

    l.save()

