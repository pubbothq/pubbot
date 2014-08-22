from django.test import TestCase
from django.core.cache import caches

from pubbot.education import receivers
from pubbot.education.models import Education


class TestEducation(TestCase):

    def setUp(self):
        caches['default'].clear()

    def test_no_match(self):
        r = receivers.lookup_education_response(None, content='Hello!', user='fred')
        self.assertEqual(r, None)

    def test_match(self):
        Education.objects.create(
            trigger="hello",
            regex=False,
            probability=1.0,
            response="sup?",
        )

        r = receivers.lookup_education_response(
            None,
            content='Hello!',
            user='fred',
        )

        self.assertEqual(r['content'], 'sup?')
