# This operation requires that udev has a custom rule to create a symbolic link when the AudioMoth is detected
# To Add the required udev rule, run the following command 
#    nano /etc/udev/rules.d/10-local.rules 
# And then type following
#      ACTION=="add", ATTRS{model}=="EFM32 MSD Device", SUBSYSTEMS=="scsi", SYMLINK+="moth%n"
#

from subprocess import Popen, PIPE

# Command to fetch the device name of the AudioMoth
getMothDeviceName = "ls -la /dev/moth* | grep 'sd.[0-9]' | awk 'NF>1{print $NF}'"

def output_shell(line):

    try:
        shell_command = Popen(line, stdout=PIPE, stderr=PIPE, shell=True)
    except OSError:
        return None
    except ValueError:
        return None

    (output, err) = shell_command.communicate()
    shell_command.wait()
    if shell_command.returncode != 0:
        print("Shell command failed to execute")
        return None, False
    return str(output.decode("utf-8")), True

def getMothDevice():
    mothDeviceName, success = output_shell(getMothDeviceName)
    return '/dev/' + mothDeviceName if (success and len(mothDeviceName) > 3) else None
