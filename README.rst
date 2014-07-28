======
pubbot
======

.. image:: https://travis-ci.org/pubbothq/pubbot.png?branch=master
   :target: https://travis-ci.org/#!/pubbothq/pubbot

I am a rewrite of an old and slightly broken Twisted IRC bot. I'm still very rough.


Development environment
=======================

Dependencies::

    sudo apt-get libavahi-compat-libdnssd-dev libmemcached-dev

To build me::

    git clone git://github.com/pubbothq/pubbot
    cd pubbot
    pip install -r requirements.txt
    pubbot rebuild

To do an incremental migration and collect static files::

    pubbot update

To launch me::

    pubbot bot


Responding to an irc message
============================

All incoming irc messages get broadcast to any task that subcribes to ``chat.<type>.<channel>.irc``. In ``tasks.py``::

There is a helper if you want to respond to a trigger that can be matched by a regex. In tasks.py::

    from pubbot.conversation import chat_receiver

    @chat_receiver(r'foo=(?P<foo>[\d\w]+), bar=(?P<bar>[\d\w]+)')
    def my_chat_handler(msg, foo, bar):
        return {
            'content': 'Foo was "%s", bar was "%s"' % (foo, bar),
            }


Messages
========

You can subscribe to a message by setting the ``subscribe`` option on a ``task`` decorator::

    @app.task(subscribe=['chat.irc.#.chat'])
    def my_chat_handler(msg):
        return {
            'content': 'You set something in irc',
            }

Messages can be matched in a similar way to RabbitMQ routing keys:

 * ``*`` matches a single word
 * ``#`` matches one or more words


``chat.<protocol>.<#channel>.chat``
-----------------------------------

This message is sent when a new line of chat has arrived.

source
channel
content
source_id
    The pk of a UserProfile object for the user that sent this chat. ``None`` if no UserProfile available.


``chat.<protocol>.<#channel>.join``
-----------------------------------

``chat.<protocol>.<#channel>.leave``
------------------------------------



``music.track``
---------------

This message is sent when the current track changes.

title
    The title of the current track.
album
    The album that the current track is part of.
artist
    The artist of the current track.

``music.stop``
--------------

This message is sent when the music stops. It doesn't have any arguments.


FAQ
===

Where is manage.py?
-------------------

The source is in ``pubbot/manage.py``. But it's installed as ``bin/pubbot``, so when your virtualenv is active you can just run ``pubbot syncdb`` etc.


Rules
=====

 * Don't make me self-aware
 * Don't bring buildout anywhere near me
 * Don't give me access to the nukes
 * Try to stick to PEP8
 * Write tests!!!


Todo
====

Dashboard - with SSE or websockets or something. See http://stackoverflow.com/questions/12853067/django-cleaning-up-redis-connection-after-client-disconnects-from-stream

