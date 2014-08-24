import mock
import unittest

from django.core.cache import caches

from pubbot import ratelimit


class TestRateLimitUtils(unittest.TestCase):

    def test_get_rate_1000_s(self):
        rate = ratelimit._get_rate("1000/s")
        self.assertEqual(rate, (1000, 1))

    def test_get_rate_1000_1s(self):
        rate = ratelimit._get_rate("1000/1s")
        self.assertEqual(rate, (1000, 1))

    def test_get_rate_1_5m(self):
        rate = ratelimit._get_rate("1/5m")
        self.assertEqual(rate, (1, 5*60))

    def test_get_rate_4_5h(self):
        rate = ratelimit._get_rate("4/5h")
        self.assertEqual(rate, (4, 5*60*60))

    def test_get_rate_20_2d(self):
        rate = ratelimit._get_rate("20/2d")
        self.assertEqual(rate, (20, 60*60*24*2))

    def test_not_a_rate(self):
        self.assertRaises(ValueError, ratelimit._get_rate, "1 every 2 seconds")

    def test_invalid_units(self):
        self.assertRaises(ValueError, ratelimit._get_rate, "1/5y")
 
    def test_invalid_freq(self):
        self.assertRaises(ValueError, ratelimit._get_rate, "a/5s")
 
    def test_invalid_period(self):
        self.assertRaises(ValueError, ratelimit._get_rate, "1/zh")


class TestRateLimitEnforce(unittest.TestCase):

    def setUp(self):
        caches['default'].clear()

    def test_enforce(self):
        @ratelimit.enforce_rate_limit("1/10s")
        def example(*args, **kwargs):
            return 'hello'

        with mock.patch("time.time") as time:
            time.return_value = 0
            self.assertEqual('hello', example())
            self.assertEqual(None, example())
            time.return_value = 15
            self.assertEqual('hello', example())


class TestRateLimitTracked(unittest.TestCase):

    def setUp(self):
        caches['default'].clear()

    def test_enforce(self):
        @ratelimit.track_rate_limit("1/10s")
        def example_2(rate_limited=False):
            return rate_limited

        with mock.patch("time.time") as time:
            time.return_value = 0
            self.assertEqual(False, example_2())
            self.assertEqual(True, example_2())
            time.return_value = 15
            self.assertEqual(False, example_2())
