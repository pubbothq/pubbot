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

import random
import re
from urllib import quote

from bs4 import BeautifulSoup
import requests

from django.contrib.humanize.templatetags.humanize import intword

from pubbot.main.celery import app
from pubbot.conversation.models import Scene


def parse_chat_text(regex, subscribe=None):
    """
    A decorator that turns a function into a celery task that receives chat messages that can be parse by a regex::

        @parse_chat_text(r'^hello <?P<name>)
        def someone_said_hello(msg, name):
            print "someone said hello to %s" % name
    """
    if isinstance(regex, basestring):
        _regex = re.compile(regex)
    else:
        _regex = regex

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

    active_scenes = Scene.objects.get_query_set()

    if 'scene_id' in msg:
        scenes = active_scenes.filter(pk=msg['scene_id'])
    elif 'tags' in msg:
        scenes = active_scenes.filter(follows_tags__name__in=msg['tags'])
        if not scenes.exists():
            scenes = active_scenes.filter(follows_tags__name='default')
    else:
        scenes = active_scenes.filter(follows_tags__name='default')

    if msg.get("action", False):
        func_name = "action"
    elif msg.get("notice", False):
        func_name = "notice"
    else:
        func_name = "say"

    for scene in scenes.exclude(bans_tags__name__in=msg.get('tags', [])).distinct():
        getattr(scene, func_name)(msg['content'])


@app.task(subscribe=['chat.#.join'])
def hello(msg):
    if msg.get('is_me', False):
        return

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
    res = requests.get('https://alpha-api.app.net/stream/0/posts/%s' %
                       id).json()
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
        v='1.0',
        rsz=8,
        q=query,
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
        definition = ''.join(BeautifulSoup(definition).findAll(text=True))

        definitions.append(u"\x031,1" + unicode(definition))

    if not definitions:
        return {
            'content': "No matches found for '%s'" % term,
        }

    return {
        'content': definitions[:4],
        'offensive': True,
    }

    # message.reply("\x031,1 " + d)


WIKTIONARY_URL_FORMAT = 'https://en.wiktionary.org/w/api.php?action=query&prop=extracts&titles={titles}&format=json'


@parse_chat_text(
    re.compile(r'^(?P<prefix>so|very|much|many)\s+(?P<word>[\w-]+)[\.\?!]?$', re.I)
    )
def doge(msg, prefix, word):
    type_prefixes = {
        'Verb': ['so', 'very', 'much', 'many'],
        'Noun': ['so', 'very'],
        'Adjective': ['much', 'many'],
        'Adverb': ['much', 'many'],
        }
    response = 'wow'
    word_type = None
    # Adding word.title() may catch some extra English words, but also yields foreign words which we don't want.
    page_titles = '|'.join([quote(word)])
    url = WIKTIONARY_URL_FORMAT.format(titles=page_titles)
    resp = requests.get(url)
    data = resp.json()
    pages = data['query']['pages']
    for page_id in pages:
        if page_id == u'-1':
            continue
        doc = BeautifulSoup(pages[page_id]['extract'])
        for synonym_heading in doc.find_all(re.compile('^h[3-9]$')):
            if synonym_heading.string != u'Synonyms':
                continue

            for sibling in synonym_heading.previous_siblings:
                if not re.match(r'^h[3-5]', sibling.name or ''):
                    continue
                if sibling.string not in type_prefixes:
                    continue
                word_type = sibling.string
                break

            if not word_type:
                continue
            prefixes = type_prefixes[word_type]
            if prefix in prefixes:
                prefixes.remove(prefix)
            response_prefix = random.choice(prefixes)

            synonyms = set()
            for list_ in synonym_heading.next_siblings:
                if list_.name == u'ul':
                    for item in list_.children:
                        if item.name != 'li':
                            continue
                        match = re.match(r'^(?:\(([^,]+(?:,\s+[^,]+)?)\):\s+)?([^,]+(?:,\s+[^,]+)?)', item.string or '')
                        if not match:
                            continue
                        synonyms |= set(match.group(1).split(', '))
                        synonyms |= set(match.group(2).split(', '))
                    break
            if not synonyms:
                continue
            synonyms = set(map(unicode.strip, synonyms))
            synonyms = set(filter(lambda x: ' ' not in x, synonyms))
            synonym = random.choice(synonyms)

            response = '{prefix} {word}'.format(prefix=response_prefix,
                                                word=synonym)
            break
        break

    return {'content': response}


@parse_chat_text(r'^fight:[\s]*(?P<word1>.*)(?:[;,]| vs\.? | v\.? )[\s]*(?P<word2>.*)')
def fight(msg, word1, word2):
    def _score(word):
        r = requests.get('http://www.google.co.uk/search',
                         params={'q': word, 'safe': 'off'})
        soup = BeautifulSoup(r.text)
        score_string = soup.find(id='resultStats').string
        return int(''.join(re.findall('\d+', score_string)))

    score1 = _score(word1)
    score2 = _score(word2)

    winner = word1 if score1 > score2 else word2

    score1 = intword(score1)
    score2 = intword(score2)

    return {
        'content': '%(word1)s (%(score1)s) vs %(word2)s (%(score2)s) -- %(winner)s wins!' %
        locals(),
    }
