from __future__ import absolute_import

from constance import config

from twitter.oauth import OAuth
from twitter.stream import TwitterStream, Timeout, HeartbeatTimeout, Hangup

import gevent

from pubbot import service
from . import signals


class Service(service.TaskService):

    def run(self):
        self.logger.debug("Setting up twitter stream")

        if not config.TWITTER_TOKEN:
            self.logger.error("I don't know how to access my twitter stream")
            return

        if not config.TWITTER_TOKEN_SECRET:
            self.logger.error("I don't know how to access my twitter stream")
            return

        auth = OAuth(
            consumer_key='XryIxN3J2ACaJs50EizfLQ',
            consumer_secret='j7IuDCNjftVY8DBauRdqXs4jDl5Fgk1IJRag8iE',
            token=config.TWITTER_TOKEN,
            token_secret=config.TWITTER_TOKEN_SECRET,
        )

        while True:
            self.logger.info("Connecting to userstream.twitter.com")

            stream = TwitterStream(auth=auth, domain='userstream.twitter.com')
            for msg in stream.user():
                if msg is None:
                    self.logger.debug("Got blank-line keep alive")
                elif msg is Timeout:
                    self.logger.debug("Got timeout. Expecting reconnect.")
                elif msg is HeartbeatTimeout:
                    self.logger.debug("Got heartbeat timeout. Expecting reconnect.")
                elif msg is Hangup:
                    self.logger.debug("Got hangup notification. Expecting reconnect.")
                elif 'text' in msg and 'user' in msg:
                    signals.tweet.send_robust(None, **msg)
                else:
                    print msg

            self.logger.info("Lost connection to userstream.twitter.com. Reconnecting in 10s...")
            gevent.sleep(10)
