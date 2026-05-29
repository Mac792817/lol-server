import re
import json
from .base import BaseParser
from utils import generate_user_agent

class DouyinParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.session.headers['User-Agent'] = generate_user_agent()
    
    def parse(self, url):
        try:
            if 'douyin.com' not in url and 'iesdouyin.com' not in url:
                return None
            
            if '/share/video/' in url or '/video/' in url:
                return self._parse_douyin_video(url)
            elif '/share/user/' in url:
                return None
            else:
                return self._parse_douyin_short(url)
        except Exception:
            return None
    
    def _parse_douyin_video(self, url):
        try:
            self.session.headers['Referer'] = 'https://www.douyin.com/'
            response = self.get(url, allow_redirects=True)
            
            if response:
                html = response.text
                match = re.search(r'window\.__INITIAL_STATE__\s*=\s*(.*?);\s*</script>', html)
                if match:
                    try:
                        data = json.loads(match.group(1))
                        video_info = data.get('video', {}).get('videoInfo', {})
                        play_url = video_info.get('playAddr', '')
                        title = video_info.get('title', 'douyin_video')
                        
                        if play_url:
                            play_url = play_url.replace('playwm', 'play')
                            return {
                                'title': title,
                                'url': play_url,
                                'platform': 'douyin',
                                'duration': video_info.get('duration', 0)
                            }
                    except Exception:
                        pass
                
                match = re.search(r'"playAddr":"([^"]+)"', html)
                if match:
                    play_url = match.group(1).replace('\\u002F', '/').replace('playwm', 'play')
                    title_match = re.search(r'"title":"([^"]+)"', html)
                    title = title_match.group(1) if title_match else 'douyin_video'
                    return {
                        'title': title,
                        'url': play_url,
                        'platform': 'douyin',
                        'duration': 0
                    }
        except Exception:
            pass
        return None
    
    def _parse_douyin_short(self, url):
        try:
            short_url = url
            if 'v.douyin.com' in url:
                response = self.get(url, allow_redirects=False)
                if response and response.headers.get('Location'):
                    short_url = response.headers['Location']
            return self._parse_douyin_video(short_url)
        except Exception:
            return None