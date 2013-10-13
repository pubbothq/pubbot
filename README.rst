======
pubbot
======

I am a rewrite of an old and slightly broken Twisted IRC bot. I am built as a gevent based Django app. A series of management commands run and send events into a queue. Worker agents process this event queue and generate more events. The agents are loosely coupled.


Development environment
=======================

To build me::

    git clone git://github.com/pubbothq/pubbot
    cd pubbot
    pip install -r requirements.txt

To launch me::

    manage.py worker --queue celery,irc


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
Dashboard - with SSE or websockets or something. See http://stackoverflow.com/questions/12853067/django-cleaning-up-redis-connection-after-client-disconnects-from-stream

