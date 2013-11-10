import random
from django.contrib.humanize.templatetags.humanize import naturaltime
from pubbot.conversation.tasks import parse_chat_text
from pubbot.conversation.models import Scene, Participant
from pubbot.kismet.models import Times


@parse_chat_text('locate (?P<user>[^\\s]+)')
def locate(msg, user):
    s = Scene.objects.get(pk=msg['scene_id'])

    try:
        u = s.participants.get(name=user).profile
    except Participant.DoesNotExist:
        return {'content': 'Who?'}

    last_seen = Times.objects.filter(
        device__in=u.devices.all()).order_by('-last_seen')[0].last_seen
    last_seen = naturaltime(last_seen)

    content = 'Last saw %(fred)s %(at_basecamp)s %(an_hour_ago)s' % dict(
        fred=user,
        at_basecamp=random.choice(
            ['at basecamp', 'in the bat cave', 'in the office',
             'sleeping at their desk', 'getting coffee', 'eating', 'hiding from you']),
        an_hour_ago=last_seen,
    )

    return {
        'content': content,
        'tags': ['useful'],
    }
