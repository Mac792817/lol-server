from fastapi import FastAPI, UploadFile, File, HTTPException
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

app = FastAPI(title="文件处理服务", version="2.0")

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

IMAGE_FORMATS = ["jpg", "jpeg", "png", "webp", "gif", "bmp"]
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
    return ''.join(random.choice(chars) for _ in range(8))

@app.get("/health")
async def health_check():
    return {"code": 200, "msg": "服务运行正常", "time": str(datetime.now())}

@app.post("/api/convert")
async def convert_file(file: UploadFile = File(...), target_format: str = "png"):
    clear_expired_files()

    original_name = file.filename
    if "." not in original_name:
        raise HTTPException(status_code=400, detail="文件缺少后缀名")

    original_format = original_name.split(".")[-1].lower()
    target_format = target_format.lower()

    if original_format not in IMAGE_FORMATS:
        raise HTTPException(status_code=400, detail=f"不支持的源格式: {original_format}")

    if target_format not in IMAGE_FORMATS:
        raise HTTPException(status_code=400, detail=f"不支持的目标格式: {target_format}")

    file_id = str(uuid.uuid4())
    upload_path = os.path.join(UPLOAD_DIR, f"{file_id}.{original_format}")
    output_path = os.path.join(OUTPUT_DIR, f"{file_id}.{target_format}")

    with open(upload_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        from PIL import Image
        img = Image.open(upload_path)
        if target_format == "jpg" or target_format == "jpeg":
            img = img.convert("RGB")
        img.save(output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")

    os.remove(upload_path)

    return {
        "code": 200,
        "msg": "转换成功",
        "data": {
            "file_id": file_id,
            "original_name": original_name,
            "new_name": f"{file_id}.{target_format}",
            "format": target_format
        }
    }

@app.get("/api/download")
async def download_file(file_id: str):
    clear_expired_files()
    for filename in os.listdir(OUTPUT_DIR):
        if filename.startswith(file_id):
            return FileResponse(
                os.path.join(OUTPUT_DIR, filename),
                filename=filename,
                media_type="application/octet-stream"
            )
    raise HTTPException(status_code=404, detail="文件不存在或已过期")

@app.get("/api/formats")
async def get_formats():
    return {"code": 200, "formats": IMAGE_FORMATS}

@app.post("/api/video/dedup")
async def video_dedup(
    file: UploadFile = File(...),
    intensity: str = "medium"
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
            filter_str = f"drawtext=text='{random_text}':fontsize=24:fontcolor=white@0.3:x=10:y=10"
            codec_params = "-c:v libx264 -preset ultrafast -crf 28"
        elif intensity == "high":
            scale_w = random.randint(1280, 1920)
            scale_h = random.randint(720, 1080)
            filter_str = (
                f"drawtext=text='{random_text}':fontsize=36:fontcolor=white@0.5:x=10:y=10,"
                f"scale={scale_w}:{scale_h},"
                f"eq=brightness=0.02:saturation=1.1"
            )
            codec_params = "-c:v libx264 -preset fast -crf 23"
        else:
            scale_w = random.choice([1280, 1366, 1920])
            scale_h = random.choice([720, 768, 1080])
            filter_str = (
                f"drawtext=text='{random_text}':fontsize=30:fontcolor=white@0.4:x=10:y=10,"
                f"scale={scale_w}:{scale_h}"
            )
            codec_params = "-c:v libx264 -preset medium -crf 25"

        cmd = [
            "ffmpeg", "-y", "-i", upload_path,
            "-vf", filter_str,
            "-c:a", "aac", "-b:a", "128k",
            codec_params,
            "-movflags", "+faststart",
            output_path
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode('utf-8', errors='ignore')
            raise Exception(f"FFmpeg处理失败: {error_msg}")

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
        raise HTTPException(status_code=500, detail=f"视频处理失败: {str(e)}")

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
