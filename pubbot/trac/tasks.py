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

from bs4 import BeautifulSoup
import requests

from pubbot.conversation.tasks import parse_chat_text


@parse_chat_text(r'^newticket: (?P<ticket>.*)$')
def raise_ticket(msg, ticket):
    s = requests.Session()
    s.verify = False

    auth = HTTPBasicAuth(self.username, self.password)

    #log.msg("Logging in")
    login_page = s.get("%s/login" % self.instance, auth=auth)

    #log.msg("Getting __FORM_TOKEN")
    form_page = s.get("%s/newticket" % self.instance, auth=auth)
    soup = BeautifulSoup(form_page.text)
    token = soup.find('input', attrs={"type": "hidden", "name": "__FORM_TOKEN"})[
        'value'].encode("utf-8")

    #log.msg("Trying to raise ticket")
    new_ticket = s.post("%s/newticket" % self.instance, allow_redirects=True, auth=auth, data={
        "__FORM_TOKEN": token,
        "field_summary": summary,
        "field_status": "new",
        "field_reporter": reporter,
        "field_owner": "",
    })

    return {
        'content': new_ticket.url,
    }
