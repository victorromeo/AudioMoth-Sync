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

handler = logging.handlers.WatchedFileHandler(os.environ.get("LOGFILE", "logs/activity.log"))
formatter = OneLineExceptionFormatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
root.addHandler(handler)