import re
import json
from .base import BaseParser
from utils import generate_user_agent

class BilibiliParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.session.headers['User-Agent'] = generate_user_agent()
    
    def parse(self, url):
        try:
            if 'bilibili.com' not in url:
                return None
            
            if '/video/' in url or '/BV' in url or '/av' in url:
                return self._parse_bilibili_video(url)
            else:
                return None
        except Exception:
            return None
    
    def _parse_bilibili_video(self, url):
        try:
            self.session.headers['Referer'] = 'https://www.bilibili.com/'
            
            video_id = self._extract_video_id(url)
            if not video_id:
                return None
            
            api_url = f'https://api.bilibili.com/x/web-interface/view?aid={video_id}' if video_id.startswith('av') else f'https://api.bilibili.com/x/web-interface/view?bvid={video_id}'
            response = self.get(api_url)
            
            if response:
                data = response.json()
                if data.get('code') == 0:
                    video_info = data.get('data', {})
                    title = video_info.get('title', 'bilibili_video')
                    
                    pages = video_info.get('pages', [])
                    if pages:
                        cid = pages[0].get('cid')
                        play_url = self._get_play_url(video_id, cid)
                        
                        if play_url:
                            return {
                                'title': title,
                                'url': play_url,
                                'platform': 'bilibili',
                                'duration': video_info.get('duration', 0)
                            }
        except Exception:
            pass
        return None
    
    def _extract_video_id(self, url):
        match = re.search(r'/video/(BV[\w]+)', url)
        if match:
            return match.group(1)
        match = re.search(r'/av(\d+)', url)
        if match:
            return f'av{match.group(1)}'
        return None
    
    def _get_play_url(self, video_id, cid):
        try:
            api_url = f'https://api.bilibili.com/x/player/playurl?avid={video_id[2:]}&cid={cid}&qn=116' if video_id.startswith('av') else f'https://api.bilibili.com/x/player/playurl?bvid={video_id}&cid={cid}&qn=116'
            response = self.get(api_url)
            
            if response:
                data = response.json()
                if data.get('code') == 0:
                    durl = data.get('data', {}).get('durl', [])
                    if durl:
                        return durl[0].get('url', '')
        except Exception:
            pass
        return None