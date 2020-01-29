from lib.statemachine import state, transition, Machine, pprint

from lib.audiomoth import audiomoth
from lib.camera import camera
from lib.diskio import diskio
from lib.config import cfg
from lib.event import event
from lib.shell import output_shell

from time import sleep
from datetime import datetime, timezone
import math

# States
s_unknown = 'unknown'
s_idling = 'idling'
s_recording = 'recording'
s_configuring = 'configuring'
s_flashing = 'flashing'
s_error = 'error'

states = [
    state('unknown').get(),
    state('configuring').children([
        state('moth').children([
            state('detected').get(),
            state('mounted').get(),
            state('unmounted').get(),
            state('error').children([
                state('unresponsive').get()
            ]).get(),
            state('resetting').get()
        ]).get(),
        state('disk').children([
            state('ok').get(),
            state('full').get(),
            state('clean').get(),
            state('error').children([
                state('corrupt').get(),
                state('permissions').get(),
                state('capacity').get()
            ]).get()
        ]).get(),
        state('time').children([
            state('set').get(),
            state('error').children([
                state('failed').get()
            ]).get()
        ]).get()
    ]).get(),
    state('idling').children([
        state('transferring').children([
            state('audio').get(),
            state('video').get(),
            state('photo').get(),
            state('logs').get()
        ]).get(),
        state('signal').children([
            state('detect').get(),
            state('pause').get(),
            state('reset').get(),
            state('reboot').get()
        ]).get()    
    ]).get(),
    state('recording').children([
        state('ready').get(),
        state('event').get(),
        state('elapsed').get()
    ]).get(),
    state('serial').children([
        state('enabled').get(),
        state('flashed').get()
    ]).get(),
]

#Operations
o_audio_to_disk = 'do_audio_to_disk'
o_disk_to_audio = 'do_disk_to_audio'
o_configure = 'configure'

# Conditions
c_is_disk_detected = 'is_disk_detected'
c_is_disk_mounted = 'is_disk_mounted'

# Transitions
t_setup = 'setup'
t_record = 'record'
t_idle = 'idle'

transitions = [

    # Startup Step 1 (Detect and Mount AudioMoth)
    transition('setup', 'unknown', 'configuring')
        .after('setup_moth').get(),

    transition('setup_moth', 'configuring', 'configuring_moth')
        .after('setup_detect_moth').get(),

    transition('setup_detect_moth', 'configuring_moth', 'configuring_moth_detected')
        .prepare(['do_audio_to_disk', 'do_detect_moth'])
        .conditions('is_moth_detected')
        .after('setup_mount_moth').get(),

    transition('setup_detect_moth', 'configuring_moth', 'configuring_moth_error_unresponsive')
        .after('setup_reset_moth').get(),

    transition('setup_mount_moth',  'configuring_moth_detected', 'configuring_moth_mounted')
        .prepare('do_mount_moth')
        .conditions(['is_moth_mounted'])
        .after('setup_disk_review').get(),

    transition('setup_mount_moth','configuring_moth_detected', 'configuring_moth_error_unresponsive')
        .after('setup_reset_moth').get(),

    transition('setup_reset_moth', 'configuring_moth_error_unresponsive', 'configuring_moth_resetting')
        .prepare('do_reset_moth')
        .after('setup_detect_moth').get(),

    # Startup Step 2 (Get Disk status)
    # Check the disk space, when Moth has just been mounted
    transition('setup_disk_review', 'configuring_moth_mounted', 'configuring_disk_ok')
        .conditions(['is_moth_diskspace_ok'])
        .after('setup_disk_review_stop').get(),
    
    # Check the disk space, after a clean
    transition('setup_disk_review', 'configuring_disk_clean', 'configuring_disk_ok')
        .conditions(['is_moth_diskspace_ok'])
        .after('setup_disk_review_stop').get(),

    transition('setup_disk_review_start','configuring_disk','configuring_disk_clean')
        .prepare('do_wipe_moth')
        .after('setup_disk_review').get(),

    # Stop if, after a clean, the capacity issue still isn't resolved
    transition('setup_disk_review', 'configuring_disk_clean', 'configuring_disk_error_capacity').get(),

    transition('setup_disk_review_stop','configuring_disk_ok', 'configuring_time')
        .conditions(['is_usbhid_online']).after('setup_time').get(),

    transition('setup_time', 'configuring_time', 'configuring_time_set')
        .prepare(['do_set_moth_time','do_get_moth_time'])
        .conditions(['is_moth_time_ok'])
        .after('setup_unmount').get(),
    
    transition('setup_unmount', 'configuring_time_set','configuring_moth_unmounted')
        .prepare('do_unmount_moth')
        .conditions('is_moth_unmounted')
        .after('setup_serial').get(),

    # Check if serial is required
    transition('setup_serial','configuring_moth_unmounted','serial')
        .conditions(['is_firmware_available','is_serial_needed'])
        .after('setup_serial').get(),

    # Enable the Serial port to begin flashing
    transition('setup_serial','serial','serial_enabled')
        .prepare('do_enable_serial')
        .conditions('is_serial_online')
        .after('setup_flashing_start').get(),

    transition('setup_flashing_start','serial_enabled','serial_flashed')
        .prepare(['do_get_moth_serialnumber','do_moth_flash'])
        .conditions('is_flash_ok')
        .after("idling").get()

    # AudioMoth configuration is complete

]

class Device(Machine):

    am: audiomoth
    c: camera
    d: diskio

    def __init__(self): 
        self.states = states
        Machine.__init__(self, 
            states = states, 
            transitions = transitions,
            queued=True,
            initial='unknown',
            before_state_change='before_state_changes', 
            after_state_change='after_state_changes')

        self.am = audiomoth()
        self.c = camera()
        self.d = diskio()

        self.mount_path = None
        self.device_name = None
        self.device_path = None

        pprint(self.am.state())

    def before_state_changes(self):
        print(f'Leaving {self.state}')

    def after_state_changes(self):
        print(f'Entering {self.state}')

    def do_audio_to_disk(self):
        self.am.clk.close()
        self.am.swdio.outputMode(True)
    
    def do_disk_to_audio(self):
        self.am.clk.close()
        self.am.swdio.close()

    def do_detect_moth(self):
        print('Detecting Moth ', end='')
        for _ in range(30):
            print('.', end='', flush=True)
            ready = self.is_moth_detected()
            if ready: 
                break
            sleep(1)

        print(' done' if ready else ' fail')
        return ready
        
    def do_mount_moth(self):
        print('Mounting Moth ', end='')
        if not self.is_moth_mounted() and self.device_path.startswith('/dev/sd'):
            self.d.mount_device(self.device_path, '/mnt/Moth')
        
        for _ in range(30):
            print('.', end='', flush=True)
            ready = self.is_moth_mounted()
            if ready: 
                break
            sleep(1)

        print(' done' if ready else ' fail')

        return ready


    def do_unmount_moth(self):
        print('Unmounting Moth ', end='')

        self.d.unmount_device(self.device_path)
        sleep(1)

        # Ensuring the disk is removed
        ready = False
        for _ in range(120):
            print('.', end='', flush=True)
            ready = self.is_moth_unmounted()

            if ready:
                break

            sleep(1)

        print(' done' if ready else ' fail')

    def do_reset_moth(self):
        self.am.swdio.close()
        self.am.rst.close()

        self.am.clk.outputMode(True)
        self.am.clk.close()
        
        self.am.rst.outputMode(False)
        sleep(2)
        self.am.rst.close()

    def do_enable_serial(self):
        self.am.clk.outputMode(True)
        self.am.rst.outputMode(False)
        self.am.swdio.close()
        sleep(1)
        self.am.rst.close()

    def do_wipe_moth(self):
        self.d.remove_files(self.mount_path, pattern="*.WAV", sudo=True)

    def do_set_moth_time(self):
        now = datetime.now(timezone.utc)
        buffer = [0x00, 0x02, 0x00, 0x00, 0x00, 0x00]
        self.dateToBuffer(buffer, 2, now)
        setTimeCommand = "./apps/usbhidtool 0x10C4 0x0002 {0}".format(''.join('0x{:02x} '.format(a) for a in buffer))

        result, success = output_shell(setTimeCommand)
        
        cfg.getOrAddFloat('time', 'set', float(now.timestamp()))

        if (success):
            print(result)

    def do_get_moth_time(self):

        buffer = [0x00, 0x01]

        getTimeCommand = "./apps/usbhidtool 0x10C4 0x0002 {0}".format(''.join('0x{:02x} '.format(a) for a in buffer))
        result, success = output_shell(getTimeCommand)
        #logger.info("getTime {0}:{1}".format(getTimeCommand, result))

        if success and result != 'NULL':
            print(result)
            hexValues = result.split(' ')

            if hexValues[0] == 'NULL\n':
                return False, None

            for hexValue in hexValues:
                buffer.append(int(hexValue, 16))

        mothDate = self.bufferToDate(buffer, 3)
        print("{0}".format(mothDate))

        cfg.getOrAddFloat('time', 'get', float(mothDate.timestamp()))

        return True, mothDate

    def do_get_moth_serial_path(self):
        result, success = output_shell(f'{cfg.paths.root}/apps/flash ')
        self.serial_path = result.strip() if success and not result.startswith('No serial ports found') else None

    def do_get_moth_serialnumber(self):
        if self.serial_path is None:
            return None

        result, success = output_shell(f'{cfg.paths.root}/apps/flash -i {self.serial_path}')
        return result.strip() if success and result is not None else None

    def do_get_moth_firmware_crc(self):
        result, success = output_shell(f'{cfg.paths.root}/apps/flash -c {self.serial_path}')
        return result.strip() if success and result is not None else None

    def do_moth_flash(self):
        flash_image = f'{cfg.paths.root}/apps/AudioMoth-Project.bin'
        result, success = output_shell(f'{cfg.paths.root}/apps/flash -u {self.serial_path} {flash_image}')

        if result is not None:
            cfg.addOrUpdate('flash','crc', self.do_get_moth_firmware_crc())

        return result.strip() if success and not result.startswith('ERROR') else None

    ## 1973  lsblk | { grep -q sd && echo "MSD " || echo "NO-MSD " ;} && ls /dev | { grep -q 'ttyACM' && echo "SERIAL " || echo "NO-SERIAL " ;} && lsusb | { grep -q 10c4 && echo "HID" || echo "NO-HID" ;}
    def is_moth_detected(self):

        find_moth_device_command = "ls -l /dev/ | grep 'moth' | grep -E 'sd[a-z]+[0-9]' | awk 'NF>1{print $NF}'"
        moth_device_name, success = output_shell(find_moth_device_command)

        self.device_name = moth_device_name[:-1] \
            if (success and len(moth_device_name) > 3) else None
        self.device_path = f"/dev/{self.device_name}" \
            if self.device_name is not None else None

        return self.device_name is not None

    def is_moth_not_detected(self):
        return not self.is_moth_detected()

    def is_moth_mounted(self):
        _, self.mount_path = self.d.is_mounted(self.device_path)
        return self.mount_path is not None
    
    def is_moth_unmounted(self):
        if self.mount_path is not None:

            r, _ = output_shell(f"lsblk | grep '{self.device_name}' | grep -c '{self.mount_path}'")

            if r is None or int(r) == 0:
                self.mount_path = None
                return True

        return False

    def is_moth_diskspace_ok(self):
        _, _, free, percentage = self.d.check_disk(True,True,self.mount_path)
        
        return percentage > 20 and free > 5 * 1024

    def is_usbhid_online(self):
        find_moth_hid_command = 'lsusb | grep -q 10c4'
        _, success = output_shell(find_moth_hid_command)

        return success

    def is_moth_time_ok(self):
        set_timestamp = cfg.getOrAddFloat('time','set',0)
        get_timestamp = cfg.getOrAddFloat('time','get',0)

        return int(set_timestamp) <= int(get_timestamp) and set_timestamp > 0

    def is_serial_online(self):
        find_moth_serial_command = "ls /dev | grep -E 'ttyACM[0-9]'"
        result, success = output_shell(find_moth_serial_command)
        self.serial_device = result.strip() if result is not None else None

        return success

    def is_serial_offline(self):
        return not self.is_serial_online()

    def is_serial_needed(self):
        flash_path = f'{cfg.paths.root}/apps/AudioMoth-Project.bin'
        result,success = self.d.get_md5(flash_path)
        print(f'MD5: {result}')
        return not success or cfg.getOrAdd('flash','md5','-') != result

    def is_firmware_available(self):
        flash_path = f'{cfg.paths.root}/apps/AudioMoth-Project.bin'
        return self.d.exists(flash_path)

    def is_flash_ok(self):
        crc_current = self.do_get_moth_firmware_crc()
        crc_cfg = cfg.getOrAdd('flash','crc', '')
        return crc_current is not None and crc_cfg == crc_current

    def dateToBuffer(self, buffer:[], offset, dateValue:datetime):
        timestamp = math.floor(dateValue.timestamp())

        buffer[offset + 3] = (timestamp >> 24) & 0xff
        buffer[offset + 2] = (timestamp >> 16) & 0xff
        buffer[offset + 1] = (timestamp >> 8) & 0xff
        buffer[offset + 0] = (timestamp & 0xff)

    def bufferToDate(self, buffer, offset):
        timestamp = 0

        if len(buffer) > 3:
            timestamp |= (int(buffer[offset]) & 0xff) | ((int(buffer[offset + 1]) & 0xff) << 8) | ((int(buffer[offset + 2]) & 0xff) << 16) | ((int(buffer[offset + 3]) & 0xff) << 24)

        #timestamp = ((buffer[offset] & 0xff) | (buffer[offset + 1] 0x0ff) | (buffer[offset + 2] & 0xff) | (buffer[offset + 3] & 0xff)) / 1000
        return datetime.fromtimestamp(timestamp)
