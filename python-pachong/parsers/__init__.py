from .douyin import DouyinParser
from .kuaishou import KuaishouParser
from .bilibili import BilibiliParser
from .xiaohongshu import XiaohongshuParser
from .pipixia import PipixiaParser
from .weibo import WeiboParser

PARSERS = {
    'douyin': DouyinParser,
    'kuaishou': KuaishouParser,
    'bilibili': BilibiliParser,
    'xiaohongshu': XiaohongshuParser,
    'pipixia': PipixiaParser,
    'weibo': WeiboParser,
}

def get_parser(url):
    import re
    from config import PLATFORM_PATTERNS
    
    for platform, pattern in PLATFORM_PATTERNS.items():
        if re.match(pattern, url):
            return PARSERS.get(platform)
    return None

def parse_video(url):
    parser = get_parser(url)
    if parser:
        return parser().parse(url)
    return None