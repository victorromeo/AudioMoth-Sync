import sys
sys.path.append("..") # Adds higher directory to python modules path.

import logging
import logging.handlers
import os
import re
from lib.config import cfg

class OneLineExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super().formatException(exc_info)
        return repr(result)
 
    def format(self, record):
        result = super().format(record)
        if record.exc_text:
            result = result.replace("\n", "")
        return result

#with open(cfg.log_file(), "a+") as f:
#    f.write('')

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))

log_format = "%(asctime)s - %(levelname)s - %(message)s"
log_level = 10
handler = logging.handlers.TimedRotatingFileHandler(f'{cfg.paths.logs}/activity', when="midnight", interval=1)
handler.setLevel(log_level)
formatter = logging.Formatter(log_format)
handler.setFormatter(formatter)

# add a suffix which you want
handler.suffix = "%Y%m%d"

#need to change the extMatch variable to match the suffix for it
handler.extMatch = re.compile(r"^\d{8}$") 

# finally add handler to logger    
logger.addHandler(handler)
