from pubbot.main.celery import app


@app.task(queue='irc')
def mouth(results, server, channel):
    results = [r for r in results if r]
    if not results:
        return

    msg = results[0]

    from pubbot.irc.bootsteps import clients
    clients[server].msg(channel, msg['content'])


@app.task(queue='irc')
def say(msg):
    clients[msg['server']].msg(msg['channel'], msg['content'])

