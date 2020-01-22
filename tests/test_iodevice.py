import unittest
from lib.iodevice import iodevice
from lib.iostate import iostate

class Test_IODevice(unittest.TestCase):
    def test_input(self):
        io = iodevice(16, iostate.Input)
        self.assertIsNotNone(io)

    def test_float(self):
        io = iodevice(16, iostate.Float)
        self.assertIsNotNone(io)

    def test_output_low(self):
        io = iodevice(16, iostate.Output, None, False, None, None, True, False)
        self.assertIsNotNone(io)
        self.assertEqual(io.mode, iostate.Output)
        self.assertEqual(io.value(), False)

    def test_output_high(self):
        io = iodevice(16, iostate.Output, None, False, None, None, True, True)
        self.assertIsNotNone(io)
        self.assertEqual(io.mode, iostate.Output)
        self.assertEqual(io.value(), True)

    def test_input_to_output(self):
        io = iodevice(16, iostate.Input)
        io.outputMode(True)
        self.assertEqual(io.mode, iostate.Output)
        self.assertEqual(io.value(), True)

    def test_output_to_input(self):
        io = iodevice(16, iostate.Output, None, False, None, None, True, True)
        io.inputMode()
        self.assertEqual(io.mode, iostate.Input)

    def test_input_to_float(self):
        io = iodevice(16, iostate.Input)
        io.close()
        self.assertEqual(io.mode, iostate.Float)

    def test_output_to_float(self):
        io = iodevice(16, iostate.Output, None, False, None, None, True, False)
        io.close()
        self.assertEqual(io.mode, iostate.Float)

    def test_float_to_input(self):
        io = iodevice(16, iostate.Float)
        io.inputMode()
        self.assertEqual(io.mode, iostate.Input)

    def test_float_to_output(self):
        io = iodevice(16, iostate.Float)
        io.outputMode(False)
        self.assertEqual(io.mode, iostate.Output)
        self.assertEqual(io.value(), False)