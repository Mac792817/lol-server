import requests
from config import DEFAULT_HEADERS, TIMEOUT, RETRY_MAX

class BaseParser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
    
    def get(self, url, **kwargs):
        for _ in range(RETRY_MAX):
            try:
                response = self.session.get(url, timeout=TIMEOUT, **kwargs)
                response.raise_for_status()
                return response
            except Exception:
                continue
        return None
    
    def post(self, url, data=None, json=None, **kwargs):
        for _ in range(RETRY_MAX):
            try:
                response = self.session.post(url, data=data, json=json, timeout=TIMEOUT, **kwargs)
                response.raise_for_status()
                return response
            except Exception:
                continue
        return None
    
    def parse(self, url):
        raise NotImplementedError
    
    def extract_video_info(self, url):
        return None