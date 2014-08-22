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
from pubbot.ratelimit import enforce_rate_limit


@chat_receiver(r"^(?P<sentence>.*)$")
def lookup_education_response(sender, user, sentence, **kwargs):
    replies = []

    for module in Education.objects.all():
        if module.regex:
            regex = module.trigger
        else:
            regex = r'\b%s\b' % re.escape(module.trigger)

        result = re.search(regex, sentence.lower())
        if result:
            replies.append((module, result.groupdict()))

    if len(replies) == 0:
        return

    return choose_education_response(user=user, responses=replies)


@enforce_rate_limit("1/15s", limit_by=['user'])
@enforce_rate_limit("10/10m")
def choose_education_response(user, responses, **kwargs):
    response, args = random.choice(responses)

    if random.random() >= response.probability:
        return

    # Build a reply using common fields and values matched in regex
    metadata = {'nick': user}
    metadata.update(kwargs)
    metadata.update(args)

    reply = response.response % metadata

    return {
        'content': reply,
    }
