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

from geventirc import message
from pubbot.main.celery import app


@app.task(queue='irc')
def mouth(results, server, channel):
    results = [r for r in results if r]
    if not results:
        return

    msg = results[0]

    content = [msg['content']] if not isinstance(msg['content'], list) else msg['content']

    from pubbot.irc.bootsteps import clients
    for c in content:
        clients[server].msg(channel, c.encode('utf-8'))


@app.task(queue='irc')
def say(server, channel, content):
    from pubbot.irc.bootsteps import clients
    clients[server].msg(channel, content.encode('utf-8'))


@app.task(queue='irc')
def action(server, channel, content):
    from pubbot.irc.bootsteps import clients
    clients[server].send_message(message.Me(channel, content.encode('utf-8')))


class Notice(message.Command):
    def __init__(self, to, msg, prefix=None):
        super(Notice, self).__init__([to, msg], prefix=prefix)


@app.task(queue='irc')
def notice(server, channel, content):
    from pubbot.irc.bootsteps import clients
    clients[server].send_message(Notice(channel, content.encode('utf-8')))

