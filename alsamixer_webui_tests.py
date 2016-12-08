import unittest
import socket
import alsamixer_webui


class AlsamixerTestCase(unittest.TestCase):

    def setUp(self):
        self.app = alsamixer_webui.app.test_client()

    def test_GET_index(self):
        rv = self.app.get('/')
        assert rv.status_code == 200

    def test_GET_not_found(self):
        rv = self.app.get('/helloWorld')
        assert rv.status_code == 404

    def test_GET_not_found_with_extension(self):
        rv = self.app.get('/helloWorld.css')
        assert rv.status_code == 404

    def test_PUT_not_found(self):
        rv = self.app.put('/helloWorld')
        assert rv.status_code == 405

    def test_static_file(self):
        rv = self.app.get('/css/style.css')
        assert rv.status_code == 200

    def test_GET_hostname(self):
        rv = self.app.get('/hostname/')
        assert rv.status_code == 200
        assert rv.data.decode('ascii') == socket.gethostname()

    def test_GET_card(self):
        rv = self.app.get('/card/')
        assert rv.status_code == 200
        self.assertEqual(rv.data, b'null')

    def test_GET_cards(self):
        rv = self.app.get('/cards/')
        assert rv.status_code == 200

    def test_GET_controls(self):
        rv = self.app.get('/controls/')
        assert rv.status_code == 200

    def test_GET_equalizer(self):
        rv = self.app.get('/equalizer/')
        assert rv.status_code == 200

    def test_PUT_card(self):
        rv = self.app.put('/card/0/')
        assert rv.status_code == 200

    def test_PUT_control(self):
        rv = self.app.put('/control/9999/0/')
        assert rv.status_code == 200

    def test_PUT_source(self):
        rv = self.app.put('/source/9999/0/')
        assert rv.status_code == 200

    def test_PUT_volume(self):
        rv = self.app.put('/volume/9999/0/')
        assert rv.status_code == 200

    def test_PUT_equalizer(self):
        rv = self.app.put('/equalizer/9999/0/')
        assert rv.status_code == 200

    def test_is_digit(self):
        self.assertTrue(alsamixer_webui.is_digit("1"))
        self.assertTrue(alsamixer_webui.is_digit("-1"))
        self.assertFalse(alsamixer_webui.is_digit("1.0"))
        self.assertFalse(alsamixer_webui.is_digit("hello world"))

if __name__ == '__main__':
    unittest.main()
