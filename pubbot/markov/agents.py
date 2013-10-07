import re

import requests

@listen("chat", parse_text=r'https://github.com/(?P<user>[\d\w]+)/(?P<repo>[\d\w]+)/pull/(?P<id>[\d]+)')
def twitter_link(msg):
    s = requests.get('https://api.twitter.com/1/statuses/show.json?id=%s' % msg['text:id']).json()
    tweet = s['text'].encode('ascii', 'replace')
    screen_name = s['user']['screen_name']

    msg = {
        'channel': 'mouth',
        'text': '[ %s: %s ]' % (screen_name, tweet),
        }
    request.send(*msg)


@listen("chat", parse_text=r'https://github.com/(?P<user>[\d\w]+)/(?P<repo>[\d\w]+)/pull/(?P<id>[\d]+)')
def pull_request(msg):
    url = 'https://api.github.com/repos/%(user)s/%(repo)s/pulls/%(id)s' % locals()

    pull = requests.get(url).json()
    title = pull['title'].encode('ascii', 'replace')
    name = pull['user']['login']

    msg = {
        'channel': 'mouth',
        'text': '[ %s: %s ]' % (name, title),
        }
    request.send(*msg)


@listen("chat", parse_text=r'https://alpha.app.net/(?P<account>[\d\w]+)/post/(?P<id>[\d]+)')
def on_appdotnet_link(msg):
    res = requests.get('https://alpha-api.app.net/stream/0/posts/%s' % id).json()
    tweet = res['data']['text'].encode('ascii', 'replace')
    screen_name = res['data']['user']['username']
    message.reply('[ ' + screen_name +': ' + tweet + ' ]')


@listen("chat", parse_text=r'^(image|img) me (?P<query>[\s\w]+)')
def image_search(msg):
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
        message.reply(image)
     else:
        message.reply("There are no images matching '%s'" % query)


@listen("chat", parse_text=r'^(udefine: (?P<term>[\w]+)')
def udefine(msg):
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
        client.msg(channel, "No matches found for '%s'" % term)
        return

    for d in definitions[:4]:
        message.reply("\x031,1 " + d)

