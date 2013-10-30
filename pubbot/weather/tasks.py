import requests
from pubbot.main.celery import app
from pubbot.conversation.tasks import mouth
from pubbot.weather.models import Point

@app.task
def update_forecast():
    for point in Point.objects.all():
        forecast = requests.get('https://api.forecast.io/forecast/%(apikey)s/%(lat)s,%(lon)s' % dict(apikey=point.api, lat=point.lat, lon=point.lon))
        data = forecast.json()
        print data
        mouth({
            'content': data['minutely']['summary'],
            'tags': [point.tag] if point.tag else [],
            })

