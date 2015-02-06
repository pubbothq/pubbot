import unittest
from unittest import mock
import contextlib2 as contextlib

from pubbot.squeezecenter import service


class TestSqueezeCenterConnection(unittest.TestCase):

    def setUp(self):
        self.stack = contextlib.ExitStack()
        self.socket = self.stack.enter_context(mock.patch("pubbot.squeezecenter.service.socket.socket"))
        self.spawn = self.stack.enter_context(mock.patch("eventlet.spawn"))
        self.sleep = self.stack.enter_context(mock.patch("eventlet.sleep"))
        self.Queue = self.stack.enter_context(mock.patch("eventlet.queue.Queue"))

        self.conn = service.SqueezeCenterConnection("127.0.0.1", 1234)
        self.conn._recv_queue = mock.Mock()
        self.conn._send_queue = mock.Mock()

    def tearDown(self):
        self.stack.close()

    def test_start(self):
        self.conn.start()
        self.socket.return_value.connect.assert_called_with(('127.0.0.1', 1234))

    def test_stop(self):
        self.conn.start()
        s = self.conn._socket
        self.conn.stop()
        s.shutdown.assert_called_with(2)
        s.close.asser_called_with()
        self.assertEqual(self.conn._socket, None)

    def test_reconnect(self):
        self.conn.reconnect()

    def test_join(self):
        self.conn.join()

    def test_send(self):
        self.conn.send("hello")
        self.conn._send_queue.put.assert_called_with("hello\n")

    def test_process_loop(self):
        handler = mock.Mock()
        self.conn.add_handler(handler)
        self.conn._recv_queue.get.side_effect = ["DATA", StopIteration()]
        try:
            self.conn._process_loop()
        except StopIteration:
            pass
        # self.conn._group.spawn.assert_called_with(handler, self.conn, "DATA")

    def test_recv_loop(self):
        self.conn.start()
        self.conn._socket.recv.side_effect = [b"data data bar\n", b"data data ", b"foo\n", BaseException()]
        try:
            self.conn._recv_loop()
        except BaseException:
            pass

        self.conn._recv_queue.put.assert_has_calls([
            mock.call(["data", "bar"]),
            mock.call(["data", "foo"]),
        ])

    def test_send_loop(self):
        self.conn.start()
        self.conn._send_queue.get.side_effect = ["data data bar\n", "data data foo\n", BaseException()]
        try:
            self.conn._send_loop()
        except BaseException:
            pass

        self.conn._socket.sendall.assert_has_calls([
            mock.call(b"data data bar\n"),
            mock.call(b"data data foo\n"),
        ])


class TestService(unittest.TestCase):

    def test_start_service(self):
        with mock.patch("pubbot.squeezecenter.service.SqueezeCenterConnection") as Conn:
            s = service.Service("squeezecenter")
            s.start_service()
            Conn.start.assed_called_with()
