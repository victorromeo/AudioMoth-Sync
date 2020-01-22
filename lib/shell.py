from subprocess import Popen, PIPE
from lib.log import logging

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
        print(f"Shell command failed to execute:{line}\n{err}")
        logging.warning(f"Command failed: {line}")
        return None, False

    return str(output.decode("utf-8")), True