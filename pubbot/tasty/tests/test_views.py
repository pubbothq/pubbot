
from django.test import TestCase


class TestGalleryView(TestCase):

    def test_get_gallery_root(self):
        response = self.client.get('/gallery/')
        self.assertEqual(response.status_code, 200)
