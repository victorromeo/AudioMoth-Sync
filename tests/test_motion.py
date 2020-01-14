import unittest
from .context import motion

def on():
    print('A')

def off():
    print('B')

class TestMotion(unittest.TestCase):
    def test_init(self):
        m = motion.motion()
        m.when_motion = on
        m.when_no_motion = off
        self.assertIsNotNone(m)