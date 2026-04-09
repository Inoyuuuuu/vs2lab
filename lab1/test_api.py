

import logging
import threading
import unittest

import clientserver
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)

class TestAuskunftService(unittest.TestCase):
    
    _server = clientserver.Server()
    _server_thread = threading.Thread(target=_server.serve)

    @classmethod
    def setUpClass(cls):
        cls._server_thread.start()

    def setUp(self):
        super().setUp()
        self.client = clientserver.Client()

    def test_srv_get_alice(self):
        msg = self.client.get("Alice")
        self.assertEqual(msg, "4098")

    def test_srv_get_bob(self):
        msg = self.client.get("Bob")
        self.assertEqual(msg, "4139")

    def test_srv_get_all(self):
        msg = self.client.getAll()
        msg = str(msg)
        self.assertTrue(msg.__contains__("Alice"))
        self.assertTrue(msg.__contains__("Bob"))

    def test_srv_get_garbage(self):
        msg = self.client.get("a")
        self.assertEqual(msg, "ERROR: no data found")

    def tearDown(self):
        self.client.close()

    @classmethod
    def tearDownClass(cls):
        cls._server._serving = False
        cls._server_thread.join()

if __name__ == '__main__':
    unittest.main()