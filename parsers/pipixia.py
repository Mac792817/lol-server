import re
import json
from .base import BaseParser
from utils import generate_user_agent

class PipixiaParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.session.headers['User-Agent'] = generate_user_agent()
    
    def parse(self, url):
        try:
            if 'pipix.com' not in url and 'huya.com' not in url:
                return None
            
            if '/video/' in url:
                return self._parse_pipixia_video(url)
            else:
                return None
        except Exception:
            return None
    
    def _parse_pipixia_video(self, url):
        try:
            self.session.headers['Referer'] = 'https://www.pipix.com/'
            response = self.get(url)
            
            if response:
                html = response.text
                
                match = re.search(r'window\.__INITIAL_STATE__\s*=\s*(.*?);\s*</script>', html)
                if match:
                    try:
                        data = json.loads(match.group(1))
                        video_data = data.get('videoDetail', {}).get('videoInfo', {})
                        play_url = video_data.get('playUrl', '')
                        title = video_data.get('title', 'pipixia_video')
                        
                        if play_url:
                            return {
                                'title': title,
                                'url': play_url,
                                'platform': 'pipixia',
                                'duration': video_data.get('duration', 0)
                            }
                    except Exception:
                        pass
        except Exception:
            pass
        return None