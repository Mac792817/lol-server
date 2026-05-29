import os
import requests
from tqdm import tqdm
from config import DOWNLOAD_DIR, TIMEOUT, DEFAULT_HEADERS
from utils import sanitize_filename, get_file_extension

class VideoDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
    
    def download(self, video_info, save_path=None):
        if not video_info or not video_info.get('url'):
            return False, 'No video URL provided'
        
        try:
            url = video_info['url']
            title = video_info.get('title', 'video')
            platform = video_info.get('platform', 'unknown')
            
            filename = f"{platform}_{sanitize_filename(title)}.{get_file_extension(url)}"
            
            if save_path:
                full_path = os.path.join(save_path, filename)
            else:
                full_path = os.path.join(DOWNLOAD_DIR, filename)
            
            response = self.session.get(url, stream=True, timeout=TIMEOUT)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(full_path, 'wb') as f, tqdm(
                desc=title,
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))
            
            return True, full_path
        
        except Exception as e:
            return False, str(e)
    
    def download_batch(self, video_info_list, save_path=None):
        results = []
        for idx, video_info in enumerate(video_info_list):
            print(f"\nDownloading {idx + 1}/{len(video_info_list)}: {video_info.get('title', 'Unknown')}")
            success, path = self.download(video_info, save_path)
            results.append({
                'video_info': video_info,
                'success': success,
                'path': path
            })
        
        return results