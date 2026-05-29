import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'downloads')

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

TIMEOUT = 30
RETRY_MAX = 3

PLATFORM_PATTERNS = {
    'douyin': r'(?:https?://)?(?:www\.)?(?:douyin\.com|iesdouyin\.com)/[^ ]+',
    'kuaishou': r'(?:https?://)?(?:www\.)?kuaishou\.com/[^ ]+',
    'bilibili': r'(?:https?://)?(?:www\.)?bilibili\.com/[^ ]+',
    'xiaohongshu': r'(?:https?://)?(?:www\.)?xiaohongshu\.com/[^ ]+',
    'pipixia': r'(?:https?://)?(?:www\.)?pipix\.com/[^ ]+',
    'weibo': r'(?:https?://)?(?:www\.)?weibo\.com/[^ ]+',
}