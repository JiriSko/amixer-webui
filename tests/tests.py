#!/usr/bin/env python2

import unittest
import importlib


try:
    # Python 2.x
    import BaseHTTPServer as server
    from StringIO import StringIO as IO
except ImportError:
    # Python 3.x
    from http import server
    from io import BytesIO as IO


class MyTest(unittest.TestCase):

    class MockServer(object):
        def __init__(self, Handler, request):
            handler = Handler(request, ('0.0.0.0', 8888), self)

    def setUp(self):
        self.amixer = importlib.import_module("alsamixer-webui")


    def test_GET_index(self):
        class MockRequest(object):
            def makefile(self, *args, **kwargs):
                return IO(b"GET /")
        self.MockServer(self.amixer.Handler, MockRequest())  # cannot test result :(

    def test_GET_not_found(self):
        class MockRequest(object):
            def makefile(self, *args, **kwargs):
                return IO(b"GET /helloWorld")
        self.MockServer(self.amixer.Handler, MockRequest())

    def test_GET_not_found_with_extension(self):
        class MockRequest(object):
            def makefile(self, *args, **kwargs):
                return IO(b"GET /helloWorld.css")
        self.MockServer(self.amixer.Handler, MockRequest())

    def test_PUT_not_found(self):
        class MockRequest(object):
            def makefile(self, *args, **kwargs):
                return IO(b"PUT /helloWorld HTTP/1.1")
        self.MockServer(self.amixer.Handler, MockRequest())

    def test_static_file(self):
        class MockRequest(object):
            def makefile(self, *args, **kwargs):
                return IO(b"GET /css/style.css")
        self.MockServer(self.amixer.Handler, MockRequest())

    def test_GET_hostname(self):
        class MockRequest(object):
            def makefile(self, *args, **kwargs):
                return IO(b"GET /hostname/")
        self.MockServer(self.amixer.Handler, MockRequest())

    def test_GET_card(self):
        class MockRequest(object):
            def makefile(self, *args, **kwargs):
                return IO(b"GET /card/")
        self.MockServer(self.amixer.Handler, MockRequest())

    def test_GET_cards(self):
        class MockRequest(object):
            def makefile(self, *args, **kwargs):
                return IO(b"GET /cards/")
        self.MockServer(self.amixer.Handler, MockRequest())

    def test_GET_controls(self):
        class MockRequest(object):
            def makefile(self, *args, **kwargs):
                return IO(b"GET /controls/")
        self.MockServer(self.amixer.Handler, MockRequest())

    def test_GET_equalizer(self):
        class MockRequest(object):
            def makefile(self, *args, **kwargs):
                return IO(b"GET /equalizer/")
        self.MockServer(self.amixer.Handler, MockRequest())

    def test_amixer_command(self):
        self.assertEqual(self.amixer.Handler.__get_amixer_command__(), ["amixer"])

    def test_change_card(self):
        class MockRequest(object):
            def makefile(self, *args, **kwargs):
                return IO(b"PUT /card/0/ HTTP/1.1")
        self.MockServer(self.amixer.Handler, MockRequest())
        self.assertEqual(self.amixer.Handler.__get_amixer_command__(), ["amixer", "-c", "0"])

    def test_PUT_control(self):
        class MockRequest(object):
            def makefile(self, *args, **kwargs):
                return IO(b"PUT /control/9999/0/ HTTP/1.1")
        self.MockServer(self.amixer.Handler, MockRequest())

    def test_PUT_source(self):
        class MockRequest(object):
            def makefile(self, *args, **kwargs):
                return IO(b"PUT /source/9999/0/ HTTP/1.1")
        self.MockServer(self.amixer.Handler, MockRequest())

    def test_PUT_volume(self):
        class MockRequest(object):
            def makefile(self, *args, **kwargs):
                return IO(b"PUT /volume/9999/0/ HTTP/1.1")
        self.MockServer(self.amixer.Handler, MockRequest())


    def test_is_digit(self):
        self.assertTrue(self.amixer.is_digit("1"))
        self.assertTrue(self.amixer.is_digit("-1"))
        self.assertFalse(self.amixer.is_digit("1.0"))
        self.assertFalse(self.amixer.is_digit("hello world"))
