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

from pubbot.main.celery import app


@app.task(queue='irc')
def mouth(results, server, channel):
    results = [r for r in results if r]
    if not results:
        return

    msg = results[0]

    from pubbot.irc.bootsteps import clients
    clients[server].msg(channel, msg['content'].encode('utf-8'))


@app.task(queue='irc')
def say(msg):
    clients[msg['server']].msg(msg['channel'], msg['content'].encode('utf-8'))

