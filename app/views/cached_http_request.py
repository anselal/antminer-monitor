import requests
import time
from app import logger

class CachedHttpRequest(object):
    def __init__(self, entry_expiration_secs=3600):
        self.cache = {}
        self.entry_expiration_secs = entry_expiration_secs
    
    def get(self, url, timeout_sec=2):
        data = self._get_data_from_cache_if_valid(url)
        if not data is None:
            logger.info("Serving from cache {}".format(url))
            return data
        logger.info("Making request {}".format(url))
        return self._make_request_and_cache(url, timeout_sec)
    
    def _get_data_from_cache_if_valid(self, url):
        if not url in self.cache:
            return None
        data = self.cache[url]
        if time.time() - data['timestamp'] >= self.entry_expiration_secs:
            return None
        return data['payload']
    
    def _make_request_and_cache(self, url, timeout_sec):
        r = requests.get(url, timeout=timeout_sec)
        if r.status_code == 200:
            self.cache[url] = {'timestamp': time.time(), 'payload': r.text}
            return r.text
        else:
            logger.error("Error while making http request. code={}".format(r.status_code))
        return None

