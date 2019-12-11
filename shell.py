from subprocess import Popen, PIPE
from log import logging

def output_shell(line):

    try:
        logging.debug(line)
        shell_command = Popen(line, stdout=PIPE, stderr=PIPE, shell=True)
    except OSError:
        return None
    except ValueError:
        return None

    (output, err) = shell_command.communicate()
    shell_command.wait()

    if shell_command.returncode != 0:
        print("Shell command failed to execute:{0}".format(line))
        logging.warning("Command failed: {0}".format(line))
        return None, False

    return str(output.decode("utf-8")), True