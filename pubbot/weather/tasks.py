import requests
import random
from pubbot.main.celery import app
from pubbot.conversation.tasks import mouth
from pubbot.weather.models import Point


@app.task
def update_forecast():
    for point in Point.objects.all():
        forecast = requests.get(
            'https://api.forecast.io/forecast/%(apikey)s/%(lat)s,%(lon)s' %
            dict(apikey=point.api, lat=point.lat, lon=point.lon))
        data = forecast.json()

        content = "Stay %(dry)s this %(lunchtime)s %(kids)s, %(weatherman)s says: %(itswet)s" % dict(
            dry=random.choice(["dry", "warm", "toasty", "snug"]),
            lunchtime=random.choice(
                ["lunch", "lunchtime", "dinner", "eating time"]),
            kids=random.choice(["kids", "folk", "silly people"]),
            weatherman=random.choice(
                ["the weatherman", "the forecast", "the weatherbot", "pubbot"]),
            itswet=data['minutely']['summary'],
        )

        mouth({
            'content': content,
            'tags': [point.tag] if point.tag else [],
        })
