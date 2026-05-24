from flask import Flask, jsonify, request, Response
import requests
import re
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
}

# 1. 解析接口
@app.route('/api/parse', methods=['GET', 'POST'])
def parse_douyin():
    try:
        if request.method == 'GET':
            url = request.args.get('url')
        else:
            url = request.json.get('url')

        if not url:
            return jsonify({"code": 400, "msg": "请输入抖音链接"})

        resp = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=10)
        final_url = resp.url

        match = re.search(r'/video/(\d+)', final_url)
        if not match:
            match = re.search(r'"video_id":"([^"]+)"', resp.text)
            if not match:
                return jsonify({"code": 400, "msg": "解析失败"})

        video_id = match.group(1)
        return jsonify({
            "code": 200,
            "video_id": video_id
        })

    except Exception as e:
        return jsonify({"code": 500, "msg": str(e)})

# 2. 中转视频接口（关键！）
@app.route('/api/video/<video_id>')
def proxy_video(video_id):
    try:
        video_url = f"https://aweme.snssdk.com/aweme/v1/play/?video_id={video_id}&ratio=1080p&line=0"
        video_resp = requests.get(video_url, headers=HEADERS, stream=True, timeout=30)
        
        return Response(
            video_resp.iter_content(chunk_size=1024*1024),
            content_type='video/mp4',
            headers={
                'Content-Disposition': f'attachment; filename="douyin_{video_id}.mp4"',
                'Access-Control-Allow-Origin': '*'
            }
        )
    except Exception as e:
        return jsonify({"code": 500, "msg": "视频获取失败"})

@app.route('/')
def index():
    return "抖音去水印API运行中～", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
