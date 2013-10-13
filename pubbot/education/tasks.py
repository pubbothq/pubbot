import random
import re

from pubbot.main.celery import app
from pubbot.education.models import Education


@app.task(subscribe='chat.#.chat')
def lookup_education_response(msg):
    replies = []

    # FIXME: Stupid bug in match.py
    if not msg['kind'].endswith('.chat'):
        return

    # FIXME: Cache this... in memcache.. somewhere..?
    for module in Education.objects.all():
        if module.regex:
            regex = module.trigger
        else:
            regex = r'\b%s\b' % re.escape(module.trigger)

        # Does this line of text match the database?
        result = re.search(regex, msg['content'].lower())
        if not result:
            continue

        # Build a reply using common fields and values matched in regex
        metadata = {'nick': msg['source']}
        metadata.update(result.groupdict())
        reply = module.response % metadata

        # Collect all possible matches
        replies.append((module, reply))

    if len(replies) == 0:
        return

    module, reply = random.choice(replies)

    if random.random() >= module.probability:
        return

    # Forget education over time, to combat spammers
    # FIXME: Better approach welcome
    module.probability /= 2.0
    module.save()

    return {
        'content': reply,
        }

