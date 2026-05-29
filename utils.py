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
        return path.split('.')[-1]
    return 'mp4'

def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename[:200]

def generate_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
    ]
    return random.choice(user_agents)

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def parse_jsonp(jsonp_str):
    try:
        match = re.search(r'^\w+\((.*)\)$', jsonp_str)
        if match:
            return json.loads(match.group(1))
        return None
    except:
        return None