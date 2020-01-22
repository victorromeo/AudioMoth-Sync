import unittest
from .context import network

class TestNetwork(unittest.TestCase):
    def test_ping_google(self):
        n = network()
        ok = n.ping()
        self.assertTrue(ok)

    def test_ping_github(self):
        n = network('https://www.google.com', 10)
        ok = n.ping()
        self.assertTrue(ok)