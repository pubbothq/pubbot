# Copyright 2008-2013 the original author or authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from functools import wraps
import random
import re

from bs4 import BeautifulSoup
import requests

from pubbot.main.celery import app
from pubbot.conversation.models import *


def parse_chat_text(regex, subscribe=None):
    """
    A decorator that turns a function into a celery task that receives chat messages that can be parse by a regex::

        @parse_chat_text(r'^hello <?P<name>)
        def someone_said_hello(msg, name):
            print "someone said hello to %s" % name
    """
    _regex = re.compile(regex)
    def decorator(func):
        def new_func(msg):
            result = _regex.search(msg['content'])
            if result:
                return func(msg, **result.groupdict())
        new_func.__name__ = func.__name__
        new_func.__doc__ = func.__doc__
        new_func.__dict__.update(func.__dict__)
        new_func = app.task(new_func, subscribe=subscribe or ['chat.#.chat'])
        return new_func
    return decorator

@app.task
def mouth(msg):
    if not 'content' in msg:
        # FIXME: Some sort of logging would be good
        return

    scenes = Scene.objects.get_query_set()
    if 'scene_id' in msg:
        scenes = scenes.filter(pk=msg['scene_id'])
    elif 'tags' in msg:
        scenes = scenes.exclude(not_interested_in__name__in=msg['tags'])
        if not scenes.exists():
            # If there are no scenes left after excluding then bail
            return

        scenes = scenes.filter(interested_in__name__in=msg['tags'])
        if not scenes.exists():
            scenes = Scene.objects.filter(interested_in__name='default')
    else:
        scenes = scenes.filter(interested_in__name='default')

    for scene in scenes.distinct():
        scene.say(msg['content'])


@app.task(subscribe=['chat.#.join'])
def hello(msg):
    mouth({
        'scene_id': msg['scene_id'],
        'content': random.choice([
            "hi %s",
            "lo %s",
            "lo. how you doing, %s?",
            "%s, we all love you",
            "Help me, Obi Wan %s, you're my only hope",
            "Wave %s, wave",
            "Give us a smile %s",
            "%s! We've missed you!",
            "%s is in the room. I have a bad feeling about this.",
            "ewwo %s",
            "yo, %s",
            "Greetings, %s",
            "wotcha, %s",
            "Frak, it's %s",
            ]) % msg['user'],
        })

"""
@parse_chat_text(r'https://twitter.com/(?P<account>[\d\w]+)/status/(?P<id>[\d]+)')
def twitter_link(msg, account, id):
    # See https://dev.twitter.com/docs/auth/application-only-auth
    # and https://dev.twitter.com/docs/api/1.1/post/oauth2/token
    bearer_token = requests.post('https://api.twitter.com/oauth2/token')

    s = requests.get('https://api.twitter.com/1/statuses/show.json?id=%s' % id).json()
    tweet = s['text'].encode('ascii', 'replace')
    screen_name = s['user']['screen_name']

    return {
        'content': '[ %s: %s ]' % (screen_name, tweet),
        'useful': True,
        }
"""


@parse_chat_text(r'https://github.com/(?P<user>[\d\w]+)/(?P<repo>[\d\w]+)/pull/(?P<id>[\d]+)')
def pull_request(msg, user, repo, id):
    url = 'https://api.github.com/repos/%(user)s/%(repo)s/pulls/%(id)s' % locals()

    pull = requests.get(url).json()
    title = pull['title'].encode('ascii', 'replace')
    name = pull['user']['login']

    return {
        'content': '[ %s: %s ]' % (name, title),
        'useful': True,
        }


@parse_chat_text(r'https://alpha.app.net/(?P<account>[\d\w]+)/post/(?P<id>[\d]+)')
def on_appdotnet_link(msg, account, id):
    res = requests.get('https://alpha-api.app.net/stream/0/posts/%s' % id).json()
    tweet = res['data']['text'].encode('ascii', 'replace')
    screen_name = res['data']['user']['username']
    return {
        'content': '[ %s: %s ]' % (screen_name, tweet),
        'useful': True,
        }


@parse_chat_text(r'^(image|img) me (?P<query>[\s\w]+)')
def image_search(msg, query):
    url = 'https://ajax.googleapis.com/ajax/services/search/images'
    results = requests.get(url, params=dict(
        v = '1.0',
        rsz = 8,
        q = query,
        )).json()
    images = results['responseData']['results']

    if images:
        def_image = 'https://is0.4sqi.net/userpix/FFUB3WWFGXUNFYDP.gif'
        image = random.choice(images).get('url', def_image)
        return {
            'content': image,
            }

    return {
        'content': "There are no images matching '%s'" % query,
        }



@parse_chat_text(r'^udefine: (?P<term>[\w]+)')
def udefine(msg, term):
    results = requests.get("http://www.urbandictionary.com/iphone/search/define", params=dict(
        term=term,
        )).json()

    if results.get('result_type', '') == 'no_results':
        return

    if not "list" in results or len(results["list"]) == 0:
        return

    definitions = []
    for result in results["list"]:
        if result["word"] != term:
            continue

        definition = result['definition']
        definition = definition.replace('\r', '')
        definition = re.sub(r'\s', ' ', definition)
        definition = ''.join(Soup(definition).findAll(text=True))
        definition = Soup(definition, convertEntities=Soup.HTML_ENTITIES)

        definitions.append(unicode(definition))

    if not definitions:
        return {
            'content': "No matches found for '%s'" % term,
            }

    return {
        'content': definitions[:4],
        'offensive': True,
        }

    # message.reply("\x031,1 " + d)


@parse_chat_text(r'^fight:[\s]*(?P<word1>.*)(?:[;,]| vs\.? | v\.? )[\s]*(?P<word2>.*)')
def fight(msg, word1, word2):
    def _score(word):
        r = requests.get('http://www.google.co.uk/search', params={'q': word, 'safe': 'off'})
        soup = BeautifulSoup(r.text)
        score_string = soup.find(id='resultStats').string
        return int(''.join(re.findall('\d+', score_string)))

    score1 = _score(word1)
    score2 = _score(word2)

    winner = word1 if score1 > score2 else word2

    return {
        'content': '%(word1)s (%(score1)s) vs %(word2)s (%(score2)s) -- %(winner)s wins!' % locals(),
        }

