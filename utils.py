import re
import json
import random
import string
from urllib.parse import urlparse, parse_qs, unquote

def extract_urls(text):
    url_pattern = r'https?://[^\s<>"\'`]+|www\.[^\s<>"\'`]+'
    urls = re.findall(url_pattern, text)
    return [url.strip('"\'<>') for url in urls]

def extract_video_url(text):
    urls = extract_urls(text)
    for url in urls:
        if any(domain in url for domain in ['douyin', 'kuaishou', 'bilibili', 'xiaohongshu', 'pipix', 'weibo']):
            return url
    return None

def get_random_string(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_file_extension(url):
    parsed = urlparse(url)
    path = parsed.path
    if '.' in path:
        ext = path.split('.')[-1].lower()
        if ext in ['mp4', 'flv', 'webm', 'mov', 'avi', 'mkv']:
            return ext
    return 'mp4'

def sanitize_filename(filename):
    invalid_chars = r'[\\/:*?"<>|]'
    return re.sub(invalid_chars, '_', filename)[:100]

def parse_jsonp(jsonp_str):
    match = re.search(r'^\w+\((.*)\)$', jsonp_str)
    if match:
        return json.loads(match.group(1))
    return {}

def get_query_param(url, param):
    parsed = urlparse(url)
    return parse_qs(parsed.query).get(param, [None])[0]

def decode_base64(data):
    try:
        import base64
        return base64.b64decode(data).decode('utf-8')
    except Exception:
        return data

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def remove_watermark(video_url):
    return video_url.replace('playwm', 'play')

def generate_user_agent():
    from fake_useragent import UserAgent
    try:
        ua = UserAgent()
        return ua.random
    except Exception:
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'