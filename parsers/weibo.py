import re
import json
from .base import BaseParser
from utils import generate_user_agent

class WeiboParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.session.headers['User-Agent'] = generate_user_agent()
    
    def parse(self, url):
        try:
            if 'weibo.com' not in url:
                return None
            
            if '/status/' in url:
                return self._parse_weibo_video(url)
            else:
                return None
        except Exception:
            return None
    
    def _parse_weibo_video(self, url):
        try:
            self.session.headers['Referer'] = 'https://weibo.com/'
            response = self.get(url)
            
            if response:
                html = response.text
                
                match = re.search(r'video-object":\s*({.*?})\s*,', html)
                if match:
                    try:
                        video_data = json.loads(match.group(1))
                        play_url = video_data.get('stream_url', '')
                        title = video_data.get('title', 'weibo_video')
                        
                        if play_url:
                            return {
                                'title': title,
                                'url': play_url,
                                'platform': 'weibo',
                                'duration': video_data.get('duration', 0)
                            }
                    except Exception:
                        pass
                
                match = re.search(r'"stream_url":"([^"]+)"', html)
                if match:
                    play_url = match.group(1).replace('\\u002F', '/')
                    title_match = re.search(r'"title":"([^"]+)"', html)
                    title = title_match.group(1) if title_match else 'weibo_video'
                    return {
                        'title': title,
                        'url': play_url,
                        'platform': 'weibo',
                        'duration': 0
                    }
        except Exception:
            pass
        return None