import re


class Node(object):
    __slots__ = ("sibling",)

    def __init__(self, part=None):
        pass

    def walk(self, chain):
        raise NotImplementedError

    def match(self, routing_key):
        return self.walk(list(routing_key.split(".")))


class Word(Node):
    __slots__ = ('word', "sibling",)

    def __init__(self, word):
        self.word = word

    def walk(self, chain):
        if chain and self.word == chain[0]:
            return self.sibling.walk(chain[1:])
        return False


class Octo(Node):

    def walk(self, chain):
        while chain:
            if chain and not chain[0]:
                return False
            if self.sibling.walk(chain):
                return True
            chain = chain[1:]

        if chain and not chain[0]:
            return False
        if self.sibling.walk(chain):
            return True

        return False


class Star(Node):

    def walk(self, chain):
        if len(chain) > 0 and not chain[0]:
            return False
        return self.sibling.walk(chain[1:])


class End(Node):

    def walk(self, chain):
        if len(chain) == 0:
            return True
        return False



class Subscriptions(Node):

    nodes = {
        '*': Star,
        '#': Octo,
        }

    def __init__(self, subscriptions):
        self.subscriptions = [self.compile(s) for s in subscriptions]

    def match(self, routing_key):
        for s in self.subscriptions:
            if s.match(routing_key):
                return True
        return False

    def compile(self, routing_key):
        """
        Given a routing key in the form foo.#.baz.*, return a graph with a match() method
        """
        parts = routing_key.split(".")
        previous = End()
        for p in reversed(parts):
            node = self.nodes.get(p, Word)(p)
            node.sibling = previous
            previous = node
        return previous

