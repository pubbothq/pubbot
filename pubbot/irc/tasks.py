from pubbot.main.celery import app

@app.task
def mouth(results):
    results = [r for r in results if r]
    if not results:
        return
    say.apply(results[0])


@app.task
def say(msg):
    print msg

