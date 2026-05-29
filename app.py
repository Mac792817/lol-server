import os
import re
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

def parse_douyin(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.douyin.com/'
        }
        
        response = requests.get(url, headers=headers, allow_redirects=True)
        html = response.text
        
        patterns = [
            r'"playAddr":"([^"]+)"',
            r'"videoUrl":"([^"]+)"',
            r'"url":"([^"]+\.mp4[^"]*)"'
        ]
        
        video_url = None
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                video_url = match.group(1).replace('\\', '')
                break
        
        if video_url:
            return {'success': True, 'video_url': video_url}
        return {'success': False, 'error': '未能提取视频链接'}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/')
def index():
    return '抖音无水印视频解析 API'

@app.route('/api/parse', methods=['POST'])
def api_parse():
    data = request.get_json()
    url = data.get('url', '')
    
    if not url:
        return jsonify({'error': '请提供抖音视频链接'}), 400
    
    result = parse_douyin(url)
    return jsonify(result)

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)