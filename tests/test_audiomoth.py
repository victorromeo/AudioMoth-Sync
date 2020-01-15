import unittest
from .context import audiomoth as audiomoth

class TestAudioMoth(unittest.TestCase):
    def test_00_init(self):
        am = audiomoth.audiomoth()
        self.assertIsNotNone(am)

    def test_01_power(self):
        am = audiomoth.audiomoth()
        self.assertEqual(am.detectMoth(),True)

    def test_reset(self):
        am = audiomoth.audiomoth()
        if am.detectMoth():
            am.resetMoth()

    def test_mount_unmount(self):
        am = audiomoth.audiomoth()
        if am.detectMoth():
            am.mountMoth()
            am.unmountMoth()

    def test_setTime_getTime(self):
        am = audiomoth.audiomoth()
        if am.detectMoth():
            am.mountMoth()
            am.setTime()
            success, mothDate = am.getTime()
            self.assertTrue(success)
            self.assertIsNotNone(mothDate)
            am.unmountMoth()

    def test_device_name(self):
        am = audiomoth.audiomoth()
        if am.detectMoth():
            name = am.getMothDeviceName()
            self.assertIsNotNone(name)
            self.assertRegex(name, "^[a-zA-Z0-9]*$")
