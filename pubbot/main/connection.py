
import json
import time

from django.conf import settings
import redis


class Connection(object):

    def __init__(self, redis, channel="default"):
        self.redis = redis.StrictRedis()

    def publish(self, channel, data):
        timestamp = int(time.time() * 1000)
        event = json.dumps(data)
        self.redis.publish(channel, event)
        # self.redis.zadd("replay:%s" % channel, event, timestamp)

    def subscribe(self, channel, handler, since=None):
        redis = self.redis.pubsub()
        redis.subscribe(channel)

        # If since is set we can avoid missing messages that happened whilst we were offline
        if since:
            for dat in self.redis.zrangebyscore('replay:%s' % channel, since, '+inf'):
                handler(data)

        for data_raw in redis.listen():
            if data_raw['type'] != "message":
                continue
            data = json.loads(data_raw["data"])
            handler(data)

    def prune(self):
        # Expire old replay logs
        channels = self.redis.keys('replay:*')
        timestamp = int(time.time() * 1000)
        oldest = timestamp - settings.QUEUE_REPLAY_EXPIRE
        if channels:
            p = self.redis.pipeline(transaction=False)
            for channels in channels:
                p.zremrangebyscore(key, 0, oldest)
            p.execute()


_connections = {}
def get_connection():
    if not _connections:
        _connections['default'] = Connection()
    return _connections

