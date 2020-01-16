import unittest
from .context import audiomoth as audiomoth

class TestAudioMoth(unittest.TestCase):
    def test_00_init(self):
        with audiomoth.audiomoth() as am:
            self.assertIsNotNone(am)

    def test_01_power(self):
        with audiomoth.audiomoth() as am:
            self.assertEqual(am.detectMoth(),True)

    def test_reset(self):
        with audiomoth.audiomoth() as am:
            if am.detectMoth():
                am.resetMoth()

    def test_mount_unmount(self):
        with audiomoth.audiomoth() as am:
            if am.detectMoth():
                am.mountMoth()
                am.unmountMoth()

    def test_setTime_getTime(self):
        with audiomoth.audiomoth() as am:
            if am.detectMoth():
                am.mountMoth()
                am.setTime()
                success, mothDate = am.getTime()
                self.assertTrue(success)
                self.assertIsNotNone(mothDate)
                am.unmountMoth()

    def test_device_name(self):
        with audiomoth.audiomoth() as am:
            if am.detectMoth():
                name = am.getMothDeviceName()
                self.assertIsNotNone(name)
                self.assertRegex(name, "^[a-zA-Z0-9]*$")
