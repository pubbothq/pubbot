======
pubbot
======

I am a rewrite of an old and slightly broken Twisted IRC bot.

Running me
==========

    manage.py run_gunicorn
    manage.py worker
    manage.py irc
    manage.py kismet
    manage.py squeezecenter


Structure
=========

I am built as a gevent based Django app. A series of management commands run and send events into a queue. Worker agents process this event queue and generate more events. The agents are loosely coupled.

pubbot.irc
----------

My irc sensor allows me to listen in on your communication, and even reply to you.

pubbot.kismet
-------------

This sensor connects allows me to sense your presence by fingerprinting your wifi devices.


Hacking on me
=============

With ``virtualenvwrapper`` it looks something like this::

    git clone git://github.com/pubbot/pubbot
    cd pubbot
    mkvirtualenv pubbot
    python setup.py develop

You can start pubbot in the foreground with ``manage.py pubbot``.


Rules
=====

 * Don't make me self-aware
 * Don't bring buildout anywhere near me
 * Don't give me access to the nukes
 * Try to stick to PEP8
 * Write tests!!!


Todo
====

Use latest gevent - https://github.com/surfly/gevent/releases/download/1.0rc3/gevent-1.0rc3.tar.gz
Redis and gevent - http://gehrcke.de/2013/01/highly-concurrent-connections-to-redis-with-gevent-and-redis-py/
Dashboard - with SSE or websockets or something. See http://stackoverflow.com/questions/12853067/django-cleaning-up-redis-connection-after-client-disconnects-from-stream

