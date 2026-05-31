from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uuid
from datetime import datetime, timedelta
import shutil
import random
import string
import subprocess
import asyncio

app = FastAPI(title="视频去重服务", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./uploads"
OUTPUT_DIR = "./outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

VIDEO_FORMATS = ["mp4", "avi", "mov", "mkv", "flv", "wmv", "webm"]

def clear_expired_files():
    expire_time = datetime.now() - timedelta(hours=2)
    for dir_path in [UPLOAD_DIR, OUTPUT_DIR]:
        if not os.path.exists(dir_path):
            continue
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            try:
                if datetime.fromtimestamp(os.path.getctime(file_path)) < expire_time:
                    os.remove(file_path)
            except:
                pass

def generate_random_text():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(10))

@app.get("/health")
async def health_check():
    return {"code": 200, "msg": "服务运行正常", "time": str(datetime.now())}

@app.post("/api/video/dedup")
async def video_dedup(
    file: UploadFile = File(...),
    intensity: str = Form("medium")
):
    clear_expired_files()

    original_name = file.filename
    if "." not in original_name:
        raise HTTPException(status_code=400, detail="文件缺少后缀名")

    original_format = original_name.split(".")[-1].lower()
    if original_format not in VIDEO_FORMATS:
        raise HTTPException(status_code=400, detail=f"不支持的视频格式: {original_format}")

    file_id = str(uuid.uuid4())
    upload_path = os.path.join(UPLOAD_DIR, f"{file_id}.{original_format}")
    output_path = os.path.join(OUTPUT_DIR, f"{file_id}_dedup.mp4")

    with open(upload_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        random_text = generate_random_text()
        
        if intensity == "low":
            scale_w, scale_h = random.choice([(1280, 720), (1366, 768)])
            brightness = 0.01
            saturation = 1.05
            codec_params = "-crf 28 -preset fast"
        elif intensity == "high":
            scale_w, scale_h = random.choice([(1280, 720), (1920, 1080), (1366, 768)])
            brightness = 0.03
            saturation = 1.15
            codec_params = "-crf 23 -preset medium"
        else:
            scale_w, scale_h = random.choice([(1280, 720), (1366, 768), (1920, 1080)])
            brightness = 0.02
            saturation = 1.1
            codec_params = "-crf 25 -preset medium"

        filter_str = (
            f"scale={scale_w}:{scale_h},"
            f"eq=brightness={brightness}:saturation={saturation},"
            f"drawtext=text='{random_text}':fontsize=20:fontcolor=white@0.4:x=10:y=10"
        )

        cmd = [
            "ffmpeg", "-y", "-i", upload_path,
            "-vf", filter_str,
            "-c:a", "aac", "-b:a", "128k",
            "-c:v", "libx264",
            "-movflags", "+faststart",
            output_path
        ]
        cmd.extend(codec_params.split())

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode('utf-8', errors='ignore')
            raise HTTPException(status_code=500, detail=f"视频处理失败: {error_msg}")

        os.remove(upload_path)

        return {
            "code": 200,
            "msg": "去重处理成功",
            "data": {
                "file_id": file_id,
                "original_name": original_name,
                "new_name": f"{file_id}_dedup.mp4",
                "format": "mp4",
                "intensity": intensity
            }
        }

    except Exception as e:
        if os.path.exists(upload_path):
            os.remove(upload_path)
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.get("/api/video/download")
async def download_video(file_id: str):
    clear_expired_files()
    for filename in os.listdir(OUTPUT_DIR):
        if filename.startswith(file_id) and "dedup" in filename:
            return FileResponse(
                os.path.join(OUTPUT_DIR, filename),
                filename=filename,
                media_type="video/mp4"
            )
    raise HTTPException(status_code=404, detail="文件不存在或已过期")

@app.get("/api/video/status")
async def video_status(file_id: str):
    for filename in os.listdir(OUTPUT_DIR):
        if filename.startswith(file_id) and "dedup" in filename:
            return {"code": 200, "status": "completed", "file_id": file_id}
    return {"code": 200, "status": "processing", "file_id": file_id}

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)