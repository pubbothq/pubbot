# coding: utf-8

from collections import defaultdict
import itertools
import random
import re

from django.conf import settings

from pubbot.markov.models import Word, Chain

if "pubbot.tasty" in settings.INSTALLED_APPS:
    from pubbot.tasty.models import Link
else:
    Link = None


WORD_BITS = re.compile('([^(),.!?\s]+|[^\s])')


def tokenize_sentence(sentence):
    data = iter(sentence.split(' '))
    while True:
        value = data.next()
        for bit in WORD_BITS.split(value):
            if not bit:
                continue
            if value.startswith("http://") or value.startswith("https://") or value.startswith("www."):
                yield "<url>"
            else:
                yield bit.replace('\x00', '')


def chainify_sentence(sentence):
    data = itertools.chain(["<start>"], tokenize_sentence(sentence), ["<stop>"])

    left1 = data.next()
    left2 = data.next()
    while True:
        right = data.next()
        yield left1, left2, right
        left1 = left2
        left2 = right


class Collector(object):

    def __init__(self):
        self.words = defaultdict(int)
        self.pairs = defaultdict(int)

    def process_line(self, line):
        data = chainify_sentence(line)

        try:
            left1, left2, right = data.next()
        except StopIteration:
            return

        try:
            while True:
                self.words[left1] += 1
                self.pairs[(left1, left2, right)] += 1
                left1, left2, right = data.next()
        except StopIteration:
            self.words[left2] += 1
            self.words[right] += 1

    def process_lines(self, lines):
        for line in lines:
            self.process_line(line)

    def create_database(self):
        print "Bulk word insert"
        Word.objects.bulk_create(
            Word(word=word, count=count) for (word,count) in self.words.items()
            )

        print "Build word get"
        words = dict((w.word, w) for w in Word.objects.all())

        print "Build chain insert"
        Chain.objects.bulk_create(
            Chain(
                left1 = words[chain[0]],
                left2 = words[chain[1]],
                right = words[chain[2]],
                count = count,
                ) for chain, count in self.pairs.items()
            )

    def update_database(self):
        pkmap = {}

        for word, count in self.words.items():
            try:
                pkmap[word] = w = Word.objects.get(word=word)
            except Word.DoesNotExist:
                pkmap[word] = w = Word(word=word)
            w.count += count
            w.save()

        for chain, count in self.pairs.items():
            l1, l2, r = chain
            left1 = pkmap[l1]
            left2 = pkmap[l2]
            right = pkmap[r]

            try:
                chain = Chain.objects.get(left1=left1, left2=left2, right=right)
            except Chain.DoesNotExist:
                chain = Chain(left1=left1, left2=left2, right=right)

            chain.count += count
            chain.save()


def get_sentence_for(word1, word2):
    yield word1
    yield word2
    c = random.choice(Chain.objects.filter(left1__word=word1, left2__word=word2))
    while c.right.word != "<stop>":
        yield c.right.word
        c = c.get_next_chain()


def render_sentence(iterator):
    try:
        sentence = [iterator.next()]
        while True:
            word = iterator.next()
            if word in ',.!?':
                sentence[-1] += word
            elif word == '<url>':
                try:
                    if Link:
                        sentence.append(random.choice(Link.objects.all()).url)
                    else:
                        sentence.append('www.github.com')
                except IndexError:
                    sentence.append('http://www.duckduckgo.com')
            else:
                sentence.append(word)
    except StopIteration:
        return ' '.join(sentence)

