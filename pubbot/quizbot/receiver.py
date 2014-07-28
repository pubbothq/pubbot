'''
Created on 3 Dec 2013

@author: mitchell
'''
import logging
import requests
from pubbot.conversation import chat_receiver


URL = 'http://developer.evi.com/ajax/api/combined'
USER_AGENT = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, '
              'like Gecko) Chrome/31.0.1650.57 Safari/537.36')

logger = logging.getLogger(__name__)


@chat_receiver('^quizbot:\\s+(?P<terms>.*)')
def quizbot_request(sender, terms, **kwargs):
    logger.info("quizbot_request: %r" % terms)
    try:
        response = requests.get(
            URL,
            params={'query': terms},
            headers={'User-Agent': USER_AGENT},
        ).json()
    except Exception as e:
        logger.exception(e)
        return

    return response['answer']
