import re
import json
from .base import BaseParser
from utils import generate_user_agent

class XiaohongshuParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.session.headers['User-Agent'] = generate_user_agent()
    
    def parse(self, url):
        try:
            if 'xiaohongshu.com' not in url:
                return None
            
            if '/explore/' in url or '/discovery/item/' in url:
                return self._parse_xiaohongshu_video(url)
            else:
                return None
        except Exception:
            return None
    
    def _parse_xiaohongshu_video(self, url):
        try:
            self.session.headers['Referer'] = 'https://www.xiaohongshu.com/'
            response = self.get(url)
            
            if response:
                html = response.text
                
                match = re.search(r'window\.__INITIAL_STATE__\s*=\s*(.*?);\s*</script>', html)
                if match:
                    try:
                        data = json.loads(match.group(1))
                        note_data = data.get('NoteDetail', {}).get('note', {})
                        title = note_data.get('title', 'xiaohongshu_video')
                        
                        video_info = note_data.get('video', {})
                        play_url = video_info.get('url', '')
                        
                        if play_url:
                            return {
                                'title': title,
                                'url': play_url,
                                'platform': 'xiaohongshu',
                                'duration': video_info.get('duration', 0)
                            }
                    except Exception:
                        pass
        except Exception:
            pass
        return None