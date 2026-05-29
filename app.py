from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import os
import tempfile
from parsers import parse_video
from downloader import VideoDownloader
from config import DOWNLOAD_DIR
<<<<<<< HEAD
from utils import is_valid_url, extract_video_url
=======
from utils import is_valid_url
>>>>>>> fb27a5f39caeaec74eb50e0398073d57809c3362

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/parse', methods=['POST'])
def parse():
    data = request.json
    url = data.get('url', '')
    
<<<<<<< HEAD
    extracted_url = extract_video_url(url)
    if extracted_url:
        url = extracted_url
    
=======
>>>>>>> fb27a5f39caeaec74eb50e0398073d57809c3362
    if not is_valid_url(url):
        return jsonify({
            'success': False,
            'error': 'Invalid URL'
        }), 400
    
    try:
        video_info = parse_video(url)
        
        if video_info:
            return jsonify({
                'success': True,
                'data': video_info
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to parse video'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url', '')
    
<<<<<<< HEAD
    extracted_url = extract_video_url(url)
    if extracted_url:
        url = extracted_url
    
=======
>>>>>>> fb27a5f39caeaec74eb50e0398073d57809c3362
    if not is_valid_url(url):
        return jsonify({
            'success': False,
            'error': 'Invalid URL'
        }), 400
    
    try:
        video_info = parse_video(url)
        
        if not video_info:
            return jsonify({
                'success': False,
                'error': 'Failed to parse video'
            }), 400
        
        downloader = VideoDownloader()
        success, path = downloader.download(video_info)
        
        if success:
            return jsonify({
                'success': True,
                'data': {
                    'title': video_info.get('title', 'video'),
                    'platform': video_info.get('platform', 'unknown'),
                    'download_url': f'/api/downloaded/{os.path.basename(path)}'
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': path
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/downloaded/<filename>')
def downloaded_file(filename):
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'success': False, 'error': 'File not found'}), 404

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
