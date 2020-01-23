import unittest
from .context import audiomoth as audiomoth

class TestAudioMoth(unittest.TestCase):
    def test_00_init(self):
        try:
            am = audiomoth()
            self.assertIsNotNone(am)
        except:
            self.fail('Unexpected error')
        finally:
            am = None

    def test_01_power(self):
        try:
            am = audiomoth()
            self.assertEqual(am.detectMoth(),True)
        except:
            self.fail('Unexpected error')
        finally:
            am = None

    def test_reset(self):
        try:
            am = audiomoth()
            if am.detectMoth():
                am.resetMoth()
        except:
            self.fail('Unexpected error')
        finally:
            am = None

    def test_mount_unmount(self):
        try:
            am = audiomoth()
            if am.detectMoth():
                am.mountMoth()
                am.unmountMoth()
        except:
            self.fail('Unexpected error')
        finally:
            am = None

    def test_setTime_getTime(self):
        try:
            am = audiomoth()
            if am.detectMoth():
                am.mountMoth()
                am.setTime()
                success, mothDate = am.getTime()
                self.assertTrue(success)
                self.assertIsNotNone(mothDate)
                am.unmountMoth()
        except:
            self.fail('Unexpected error')
        finally:
            am = None

    def test_device_name(self):
        try:
            am = audiomoth()
            if am.detectMoth():
                name = am.getMothDeviceName()
                self.assertIsNotNone(name)
                self.assertRegex(name, "^[a-zA-Z0-9]*$")
        except:
            self.fail('Unexpected error')
        finally:
            am = None
