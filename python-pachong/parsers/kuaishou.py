import re
import json
from .base import BaseParser
from utils import generate_user_agent

class KuaishouParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.session.headers['User-Agent'] = generate_user_agent()
    
    def parse(self, url):
        try:
            if 'kuaishou.com' not in url:
                return None
            
            if 'photo' in url:
                return self._parse_kuaishou_video(url)
            else:
                return self._parse_kuaishou_short(url)
        except Exception:
            return None
    
    def _parse_kuaishou_video(self, url):
        try:
            self.session.headers['Referer'] = 'https://www.kuaishou.com/'
            response = self.get(url)
            
            if response:
                html = response.text
                
                match = re.search(r'window\.initialState\s*=\s*(.*?);\s*</script>', html)
                if match:
                    try:
                        data = json.loads(match.group(1))
                        video_data = data.get('video', {}).get('video', {})
                        play_url = video_data.get('src', '')
                        title = video_data.get('caption', 'kuaishou_video')
                        
                        if play_url:
                            return {
                                'title': title,
                                'url': play_url,
                                'platform': 'kuaishou',
                                'duration': video_data.get('duration', 0)
                            }
                    except Exception:
                        pass
                
                match = re.search(r'"src":"([^"]+)"', html)
                if match:
                    play_url = match.group(1).replace('\\u002F', '/')
                    title_match = re.search(r'"caption":"([^"]+)"', html)
                    title = title_match.group(1) if title_match else 'kuaishou_video'
                    return {
                        'title': title,
                        'url': play_url,
                        'platform': 'kuaishou',
                        'duration': 0
                    }
        except Exception:
            pass
        return None
    
    def _parse_kuaishou_short(self, url):
        try:
            short_url = url
            if 'k.sina.com.cn' in url or 't.cn' in url:
                response = self.get(url, allow_redirects=False)
                if response and response.headers.get('Location'):
                    short_url = response.headers['Location']
            return self._parse_kuaishou_video(short_url)
        except Exception:
            return None