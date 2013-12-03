'''
Created on 3 Dec 2013

@author: mitchell
'''
import requests

from pubbot.conversation import tasks as conversation_tasks


URL = 'http://developer.evi.com/ajax/api/combined'
USER_AGENT = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, '
              'like Gecko) Chrome/31.0.1650.57 Safari/537.36')


@conversation_tasks.parse_chat_text('^quizbot:\\s+(?P<terms>.*)')
def quizbot_request(msg, terms):
    try:
        response = requests.get(URL,
                                params={'query': terms},
                                headers={'User-Agent': USER_AGENT})
        data = response.json()
        conversation_tasks.mouth({
            'scene_id': msg['scene_id'],
            'content': '{nick}: the answer to "{terms}" is: '.format(
                            nick=msg['user'],
                            terms=terms,
                            data['answer'],
                            ),
        })
    except Exception:
        conversation_tasks.mouth({
            'scene_id': msg['scene_id'],
            'content': "{nick}: I don't know the answer to \"{terms}\"".format(
                            nick=msg['user'],
                            terms=terms,
                            ),
            })
