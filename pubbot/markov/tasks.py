import random

from pubbot.conversation.tasks import parse_chat_text
from pubbot.markov.utils import tokenize_sentence, get_sentence_for, render_sentence, Collector


# FIXME: Determine these sorts of things programatically/statistically
#    perhaps by using the same markov model, but on adjoining sentence starts
start_points_2 = {
    ("you", "are"): [
        ("i", "am"),
        ("you", "are"),
        ("i", "will"),
    ],
    ("i", "am"): [
        ("yes", ","),
        ("yes", "you"),
        ("no", ","),
        ("no", "you"),
    ]
}


@parse_chat_text(r'^(?P<sentence>.*)$')
def markov(msg, sentence):
    if not msg.get('direct', False):
        return

    try:
        tokens = tokenize_sentence(sentence)
        word1, word2 = tokens.next(), tokens.next()
    except StopIteration:
        return

    word1, word2 = random.choice(
        start_points_2.get((word1, word2), [(word1, word2)]))

    try:
        return {
            'content': render_sentence(get_sentence_for(word1, word2))
        }
    except IndexError:
        pass


@parse_chat_text(r'^(?P<sentence>.*)$')
def learn(msg, sentence):
    if msg.get('direct', False):
        return

    c = Collector()
    c.process_line(sentence)
    c.update_database()
