import random

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

    def store_tokens(self, tokens):
        for a, b, c in group_tokens(tokens):
            self.client.sadd(self.TOKEN_KEY % (b, ), self.GROUP_KEY % (a, b, c))
            self.client.sadd(self.FORWARD_KEY % (a, b), c)
            self.client.sadd(self.BACKWARD_KEY % (c, b), a)
            self.client.incr(self.GROUP_KEY % (a, b, c))
            self.client.sadd(self.STEM_KEY % stemmer.stem(c), c)

    def random_grouping_to_end(self, a, b, c):
        chain = []
        score = 0
        while True:
            score += int(self.client.get(self.GROUP_KEY % (a, b, c)) or 0)
            a = b
            b = c
            c = self.client.srandmember(self.FORWARD_KEY % (a, b))
            if not c:
                break
            chain.append(c)
        return chain, score

    def random_grouping_to_start(self, a, b, c):
        chain = []
        score = 0
        while True:
            score += int(self.client.get(self.GROUP_KEY % (a, b, c)) or 0)
            c = b
            b = a
            a = self.client.srandmember(self.BACKWARD_KEY % (c, b))
            if not a:
                break
            chain.insert(0, a)
        return chain, score

    def get_chain_from_group(self, a, b, c):
        left, lscore = self.random_grouping_to_start(a, b, c)
        right, rscore = self.random_grouping_to_end(a, b, c)
        chain = left + [a, b, c] + right
        return chain, lscore + rscore / len(chain)

    def get_chain_from_tokens(self, tokens):
        token = random.choice(tokens)
        _, a, b, c = self.client.srandmember(self.TOKEN_KEY % token).split("_")
        return self.get_chain_from_group(a, b, c)


brain = SimpleLazyObject(Brain)
