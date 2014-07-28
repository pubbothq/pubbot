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

from pubbot.conversation import chat_receiver
from pubbot.education.models import Education


@chat_receiver(r".*")
def lookup_education_response(sender, **kwargs):
    replies = []

    # FIXME: Stupid bug in match.py
    if not kwargs['kind'].endswith('.chat'):
        return

    # FIXME: Cache this... in memcache.. somewhere..?
    for module in Education.objects.all():
        if module.regex:
            regex = module.trigger
        else:
            regex = r'\b%s\b' % re.escape(module.trigger)

        # Does this line of text match the database?
        result = re.search(regex, kwargs['content'].lower())
        if not result:
            continue

        # Build a reply using common fields and values matched in regex
        metadata = {'nick': kwargs['source']}
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
