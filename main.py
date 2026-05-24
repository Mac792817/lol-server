from flask import Flask, jsonify, request, Response
import requests
import re
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 抖音请求头（关键！）
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Referer": "https://www.douyin.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

@app.route('/api/parse', methods=['POST'])
def parse_douyin():
    try:
        data = request.get_json()
        url = data.get('url')
        if not url:
            return jsonify({"code": 400, "msg": "请输入链接"})

        # 先跟随短链接跳转，拿到真实页面
        resp = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=20)
        final_url = resp.url

        # 提取 video_id（双重匹配，防止失效）
        match = re.search(r'/video/(\d+)', final_url)
        if not match:
            match = re.search(r'video_id=(\d+)', resp.text)
            if not match:
                return jsonify({"code": 400, "msg": "解析失败"})

        video_id = match.group(1)
        return jsonify({
            "code": 200,
            "video_id": video_id
        })

    except Exception as e:
        return jsonify({"code": 500, "msg": str(e)})

# 视频代理接口（关键！）
@app.route('/api/video/<video_id>')
def proxy_video(video_id):
    try:
        # 抖音无水印视频地址（1080p 最高清）
        video_url = f"https://aweme.snssdk.com/aweme/v1/play/?video_id={video_id}&ratio=1080p&line=0"
        
        # 带上完整请求头，抖音不会拒绝
        video_resp = requests.get(
            video_url, 
            headers=HEADERS, 
            stream=True, 
            timeout=30,
            allow_redirects=True
        )

        # 检查响应状态
        if video_resp.status_code != 200:
            return jsonify({"code": 500, "msg": "视频获取失败"})

        # 直接返回视频流
        return Response(
            video_resp.iter_content(chunk_size=1024*1024),
            content_type='video/mp4',
            headers={
                'Access-Control-Allow-Origin': '*',
                'Content-Disposition': f'attachment; filename="douyin_{video_id}.mp4"',
                'Content-Length': video_resp.headers.get('Content-Length', ''),
                'Accept-Ranges': 'bytes'
            }
        )
    except Exception as e:
        return jsonify({"code": 500, "msg": str(e)})

@app.route('/')
def index():
    return "API Running", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
