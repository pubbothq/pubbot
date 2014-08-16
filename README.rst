======
pubbot
======

.. image:: https://travis-ci.org/pubbothq/pubbot.png?branch=master
   :target: https://travis-ci.org/#!/pubbothq/pubbot

.. image:: https://coveralls.io/repos/pubbothq/pubbot/badge.png?branch=master
    :target: https://coveralls.io/r/pubbothq/pubbot

I am a rewrite of an old and slightly broken Twisted IRC bot. I'm still very rough.


Development environment
=======================

To build me::

    git clone git://github.com/pubbothq/pubbot
    cd pubbot
    pip install -r requirements.txt
    pubbot rebuild

To do an incremental migration and collect static files::

    pubbot update

To launch me::

    pubbot bot


Hacking
=======

All interesting and hookable behaviour is extensible via Django signals.


Responding to an irc message
----------------------------

The signal ``pubbot.conversation.signals.message`` is fired when a chat message
is received. You can listen to it with the standard Django mechanisms,
including the ``@receiver`` decorator::

    from django.dispatch import receiver

    @receiver(message)
    def my_receiver(signal, **kwargs):
        return {"content": "Hello!"}

The responses will be sorted and the best match will be used as the IRC reply.

As most chat messages can be filtered by regexes a helper is provided::

    from pubbot.conversation import chat_receiver

    @chat_receiver(r'https://github.com/(?P<user>[\d\w]+)/(?P<repo>[\d\w]+)/pull/(?P<id>[\d]+)')
    def pull_request(sender, user, repo, id, **kwargs):
        # Process pull request in some way
        return {'content': 'Some information about a pull request'}


Signals
=======


``pubbot.conversation.signals.message``
---------------------------------------

This signal is sent when a new line of chat has arrived.

source
channel
content
source_id
    The pk of a UserProfile object for the user that sent this chat. ``None`` if no UserProfile available.


``pubbot.conversation.signals.join``
------------------------------------

``pubbot.conversation.signals.leave``
-------------------------------------



``pubbot.squeezecenter.signals.song_started``
---------------------------------------------

This signal is sent when the current track changes.

title
    The title of the current track.
album
    The album that the current track is part of.
artist
    The artist of the current track.

``pubbot.squeezecenter.signals.music_stopped``
----------------------------------------------

This signal is sent when the music stops. It doesn't have any arguments.


``pubbot.vcs.signals.commit``
-----------------------------

This signal is sent when a commit is detected.


FAQ
===

Where is manage.py?
-------------------

The source is in ``pubbot/manage.py``. But it's installed as ``bin/pubbot``, so when your virtualenv is active you can just run ``pubbot syncdb`` etc.
