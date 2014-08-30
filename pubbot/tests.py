import mock
import unittest
import gevent

from django.core.cache import caches

from pubbot import ratelimit
from pubbot.state import Machine, State, Transition
from pubbot.service import BaseService, TaskService
from pubbot.utils import force_str, force_bytes


class TestRateLimitUtils(unittest.TestCase):

    def test_get_rate_1000_s(self):
        rate = ratelimit._get_rate("1000/s")
        self.assertEqual(rate, (1000, 1))

    def test_get_rate_1000_1s(self):
        rate = ratelimit._get_rate("1000/1s")
        self.assertEqual(rate, (1000, 1))

    def test_get_rate_1_5m(self):
        rate = ratelimit._get_rate("1/5m")
        self.assertEqual(rate, (1, 5 * 60))

    def test_get_rate_4_5h(self):
        rate = ratelimit._get_rate("4/5h")
        self.assertEqual(rate, (4, 5 * 60 * 60))

    def test_get_rate_20_2d(self):
        rate = ratelimit._get_rate("20/2d")
        self.assertEqual(rate, (20, 60 * 60 * 24 * 2))

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


class TestMachine(unittest.TestCase):

    def test_duplicate_state(self):
        try:
            class M(Machine):
                state = State(initial=True)

            class Y(M):
                state = State()
        except RuntimeError:
            return
        self.fail("Did not detect duplicate state")

    def test_duplicate_intial_state(self):
        try:
            class M(Machine):
                state1 = State(initial=True)
                state2 = State(initial=True)
        except RuntimeError:
            return
        self.fail("Did not detect duplicate initial=True")

    def test_no_initial_state(self):
        try:
            class M(Machine):
                state1 = State()
        except RuntimeError:
            return
        self.fail("Did not detect lack of initial=True")

    def test_wait_for_invalid(self):
        class M(Machine):
            state = State(initial=True)
        m = M()
        self.assertRaises(RuntimeError, m.wait, "invalid_state")

    def test_wait_for_state(self):
        class M(Machine):
            state = State(initial=True)
        m = M()
        m.wait("state")

    def test_no_transition(self):
        class M(Machine):
            state1 = State(initial=True)
            state2 = State()
        m = M()
        try:
            with m.transition_to("state2"):
                pass
        except RuntimeError:
            return
        self.fail("Found a valid transition but shouldnt have")

    def test_already_in_transition(self):
        class M(Machine):
            state1 = State(initial=True)
            state2 = State()
            transition = Transition("state1", "state2")

        m = M()
        try:
            with m.transition_to("state2"):
                with m.transition_to("state2"):
                    pass
        except RuntimeError:
            return
        self.fail("Nested transition was allowed")

    def test_transition(self):
        class M(Machine):
            state1 = State(initial=True)
            state2 = State()
            transition = Transition("state1", "state2")

        m = M()
        with m.transition_to("state2"):
            pass
        self.assertEqual(m.state, "state2")


class TestBaseService(unittest.TestCase):

    def test_parenting_and_deparenting(self):
        p = BaseService("parent")
        c = BaseService("child")
        p.add_child(c)
        self.assertEqual(len(p.keys()), 1)
        c.disown_parent()
        self.assertEqual(len(p.keys()), 0)

    def test_remove_child_not_parent_of(self):
        p = BaseService("parent")
        c = BaseService("child")
        self.assertRaises(KeyError, p.remove_child, c)

    def test_double_add_child_fails(self):
        p = BaseService("parent")
        c = BaseService("child")
        p.add_child(c)
        self.assertRaises(KeyError, p.add_child, c)

    def test_stop_service_with_child(self):
        class C(BaseService):
            _outcome = 0

            def stop_service(self):
                self._outcome = 1

        p = BaseService("parent")
        c = C("child")
        p.add_child(c)
        p.start()
        self.assertEqual(c._outcome, 0)
        p.stop()
        self.assertEqual(c._outcome, 1)


class TestSimpleTaskService(unittest.TestCase):

    def test_repr(self):
        t = TaskService("test_repr")
        self.assertEqual(t.__repr__(), "Service(test_repr)")

    def test_run(self):
        class T(TaskService):
            _outcome = 0

            def run(self):
                self._outcome = 1

        t = T("test_run")
        gevent.with_timeout(1, t.start_and_wait)
        self.assertEqual(t._outcome, 1)

    def test_run_not_impl(self):
        self.assertRaises(NotImplementedError, TaskService("test").run)


class TestUtils(unittest.TestCase):

    def test_force_str_error(self):
        self.assertRaises(ValueError, force_str, [])

    def test_force_str_u(self):
        self.assertTrue(isinstance(force_str(u"hello"), str))

    def test_force_str_b(self):
        self.assertTrue(isinstance(force_str(b"hello"), str))

    def test_force_bytes_error(self):
        self.assertRaises(ValueError, force_bytes, [])

    def test_force_bytes_u(self):
        self.assertTrue(isinstance(force_bytes(u"HELLO"), str))

    def test_force_bytes_b(self):
        self.assertTrue(isinstance(force_bytes(b"HELLO"), str))
