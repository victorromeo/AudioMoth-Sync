import sys
sys.path.append("..") # Adds higher directory to python modules path.

from configuration import configuration as config
import logging
import logging.handlers
import os
 
class OneLineExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super().formatException(exc_info)
        return repr(result)
 
    def format(self, record):
        result = super().format(record)
        if record.exc_text:
            result = result.replace("\n", "")
        return result

logfile = '{0}/activity.log'.format(config.local_log_path)

if not os.path.exists(logfile):
    with open(logfile, "a+") as f:
        f.write('')

handler = logging.handlers.WatchedFileHandler(os.environ.get("LOGFILE", "capture/logs/activity.log"))
formatter = OneLineExceptionFormatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
root.addHandler(handler)