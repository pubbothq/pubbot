import os
import random
import json

from django.utils.functional import SimpleLazyObject
import redis

from .stemmer import stemmer


def group_tokens(tokens):
    a = ""
    b = ""
    c = tokens.next()
    yield (a, b, c)

    while c:
        a = b
        b = c
        try:
            c = tokens.next()
        except StopIteration:
            c = ""
        yield (a, b, c)


class Brain(object):

    TOKEN_KEY = "T_%s"
    GROUP_KEY = "G_%s_%s_%s"
    FORWARD_KEY = "F_%s_%s"
    BACKWARD_KEY = "B_%s_%s"
    STEM_KEY = "S_%s"

    def __init__(self):
        self.client = redis.StrictRedis(host='localhost', port=6379, db=10)
        with open(os.path.join(os.path.dirname(__file__), "generate_sentence.lua")) as fp:
            self.generate_sentence = fp.read()

    def store_tokens(self, tokens):
        for a, b, c in group_tokens(tokens):
            self.client.sadd(self.TOKEN_KEY % (b, ), self.GROUP_KEY % (a, b, c))
            self.client.sadd(self.FORWARD_KEY % (a, b), c)
            self.client.sadd(self.BACKWARD_KEY % (c, b), a)
            self.client.incr(self.GROUP_KEY % (a, b, c))
            self.client.sadd(self.STEM_KEY % stemmer.stem(c), c)

    def get_chains_from_tokens(self, tokens):
        while True:
            token = random.choice(tokens)
            try:
                results = json.loads(self.client.eval(self.generate_sentence, 0, token, 10), "utf-8")
            except UnicodeError:
                continue

            for result in results:
                yield result["chain"], result["score"]


brain = SimpleLazyObject(Brain)
