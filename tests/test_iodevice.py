import unittest
import iodevice
import iostate

class Test_IODevice(unittest.TestCase):
    def test_input(self):
        io = iodevice.iodevice(16, iostate.iostate.Input)
        self.assertIsNotNone(io)

    def test_float(self):
        io = iodevice.iodevice(16, iostate.iostate.Float)
        self.assertIsNotNone(io)

    def test_output_low(self):
        io = iodevice.iodevice(16, iostate.iostate.Output, None, False, None, None, True, False)
        self.assertIsNotNone(io)
        self.assertEqual(io.mode, iostate.iostate.Output)
        self.assertEqual(io.value(), False)

    def test_output_high(self):
        io = iodevice.iodevice(16, iostate.iostate.Output, None, False, None, None, True, True)
        self.assertIsNotNone(io)
        self.assertEqual(io.mode, iostate.iostate.Output)
        self.assertEqual(io.value(), True)

    def test_input_to_output(self):
        io = iodevice.iodevice(16, iostate.iostate.Input)
        io.outputMode(True)
        self.assertEqual(io.mode, iostate.iostate.Output)
        self.assertEqual(io.value(), True)

    def test_output_to_input(self):
        io = iodevice.iodevice(16, iostate.iostate.Output, None, False, None, None, True, True)
        io.inputMode()
        self.assertEqual(io.mode, iostate.iostate.Input)

    def test_input_to_float(self):
        io = iodevice.iodevice(16, iostate.iostate.Input)
        io.close()
        self.assertEqual(io.mode, iostate.iostate.Float)

    def test_output_to_float(self):
        io = iodevice.iodevice(16, iostate.iostate.Output, None, False, None, None, True, False)
        io.close()
        self.assertEqual(io.mode, iostate.iostate.Float)

    def test_float_to_input(self):
        io = iodevice.iodevice(16, iostate.iostate.Float)
        io.inputMode()
        self.assertEqual(io.mode, iostate.iostate.Input)

    def test_float_to_output(self):
        io = iodevice.iodevice(16, iostate.iostate.Float)
        io.outputMode(False)
        self.assertEqual(io.mode, iostate.iostate.Output)
        self.assertEqual(io.value(), False)