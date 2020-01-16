from configuration import configuration as config
from log import logging
import requests

## This library tests connectivity to a URL 

class network:
    def __init__(self, url:str = config.ping_test_url, timeout: int = 5):
        if not url:
            self.url = config.ping_test_url
        else:
            self.url = url

        if timeout <= 0 or timeout > 30:
            self.timeout = 5
        else:
            self.timeout = timeout

    def ping(self):
        try:
            _ = requests.get(self.url, timeout=self.timeout)
            return True
        except requests.ConnectionError:
            logging.info('ping connection error')
        return False