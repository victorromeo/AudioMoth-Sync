
def read(filename):
    with open(filename, 'r') as f:
        f.readline().strip()

root = read('root')
device = read('device')
bucket = read('bucket') 

if root is None:
    root = '/home/pi/Documents/AudioMoth-Sync'

class configuration:
    am_swdio_pin = 20
    am_swclk_pin = 21
    am_swo_pin = 19
    am_rst_pin = 16
    am_pwr_pin = 26
    pir_pins = {12, 13}
    am_mount_path = '/media/pi/Moth'
    root_path = root
    local_audio_path = '{0}/capture/recordings'.format(root_path)
    local_visual_path = '{0}/capture/photos'.format(root_path)
    local_log_path = '{0}/capture/logs'.format(root_path)
    motion_sec = 5
    motion_queue_len = 50
    min_disk_mb = 200
    min_disk_percent = 0.2
    photo_count_on_motion = 5
    photo_count_delay_sec = 1
    ping_test_url = 'https://www.google.com'
    device_name = device
    aws_bucket_name = 's3://{0}'.format(bucket)
