from subprocess import Popen, PIPE
from lib.log import logging

def output_shell(line, raise_on_non_zero:bool = False):

    try:
        logging.debug(line)
        print(f'SHELL:{line}', flush=True)
        shell_command = Popen(line, stdout=PIPE, stderr=PIPE, shell=True)
    except OSError:
        return None
    except ValueError:
        return None

    (output, err) = shell_command.communicate()
    shell_command.wait()

    if shell_command.returncode != 0 and raise_on_non_zero:
        print(f"Shell command failed to execute:{line}\n{err}\n{output if not None else ''}")
        logging.warning(f"Command failed: {line}")
        return output, False

    return str(output.decode("utf-8")), True

def output_shell_str(line, fallback: str):
    result, error = output_shell(line)
    return fallback if error else result

def output_shell_int(line, fallback: int):
    result, error = output_shell(line)
    return fallback if error or result is None else int(result.split(' ')[0])
