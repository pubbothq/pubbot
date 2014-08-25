from django.test import TestCase
from django.core.exceptions import ValidationError

from pubbot.education.models import Education


class TestEducationModel(TestCase):

    def test_as_str(self):
        e = Education.objects.create(
            trigger='foo',
            response='bar',
            probability=0.5,
        )
        self.assertEqual(str(e), "'foo' -> 'bar'")

    def test_invalid_regex(self):
        e = Education.objects.create(
            regex=True,
            trigger=r'\x',
            probability=0.5,
        )
        self.assertRaises(ValidationError, e.clean)
