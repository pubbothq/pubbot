'''
Created on 3 Dec 2014

'''
import logging
import requests
from pubbot.conversation import chat_receiver

import giphypop

logger = logging.getLogger(__name__)

@chat_receiver('^gifme:\\s+(?P<terms>.*)')
def giphy_request(sender, terms, **kwargs):
    logger.info("giphy_request: %r" % terms)

    try:
        g = giphypop.Giphy()
        results = g.search_list(phrase=terms, limit=1)
    except Exception:
        logger.exception("Exception fetching/decoding giphy response")
        return

    if results:
        return {"content": results[0].media_url}
    return {"content": "No gifs found"}