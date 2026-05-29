#!/usr/bin/env python3
import http.server
import socketserver
import json
import urllib.parse
from parsers import parse_video
from utils import is_valid_url

PORT = 5000

class VideoHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('templates/index.html', 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/parse':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(post_data)
                url = data.get('url', '')
                
                if not is_valid_url(url):
                    self.send_json(400, {'success': False, 'error': 'Invalid URL'})
                    return
                
                video_info = parse_video(url)
                
                if video_info:
                    self.send_json(200, {'success': True, 'data': video_info})
                else:
                    self.send_json(400, {'success': False, 'error': 'Failed to parse video'})
            except Exception as e:
                self.send_json(500, {'success': False, 'error': str(e)})
        else:
            self.send_error(404)
    
    def send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), VideoHandler) as httpd:
        print(f"Server running on http://localhost:{PORT}")
        httpd.serve_forever()
