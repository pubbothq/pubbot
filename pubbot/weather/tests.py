import mock

from django.test import TestCase

from pubbot.weather.models import Point
from pubbot.weather.receivers import update_forecast


class TestWeather(TestCase):

    def setUp(self):
        Point.objects.create(api="some_api_key", lat=0, lon=0)

    def test_weather(self):
        with mock.patch("requests.get") as get:
            get.return_value.json.return_value = {'minutely': {'summary': 'rubbish'}}
            with mock.patch("random.choice") as choice:
                choice.side_effect = lambda x: x[0]
                with mock.patch("pubbot.weather.receivers.say") as say:
                    update_forecast()
                    say.assert_called_with(
                        content='Stay dry this lunch kids, the weatherman says: rubbish',
                        tags=[],
                    )
