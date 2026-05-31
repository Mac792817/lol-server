from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import uuid
import shutil
import subprocess
from datetime import datetime, timedelta

app = FastAPI(title="视频去重服务", version="3.0")

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

@app.get("/health")
async def health_check():
    return {"code": 200, "msg": "服务运行正常"}

@app.post("/api/video/dedup")
async def video_dedup(file: UploadFile = File(...), intensity: str = "medium"):
    clear_expired_files()

    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}_input.mp4")
    output_path = os.path.join(OUTPUT_DIR, f"{file_id}_dedup.mp4")

    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    watermark_text = f"DEDUP_{file_id[:8]}"

    try:
        if intensity == "low":
            cmd = [
                "ffmpeg", "-y", "-i", input_path,
                "-vf", f"drawtext=text='{watermark_text}':fontsize=24:fontcolor=white:shadowcolor=black:shadowx=2:shadowy=2:x=10:y=10",
                "-c:a", "copy",
                "-preset", "ultrafast",
                output_path
            ]
        elif intensity == "high":
            cmd = [
                "ffmpeg", "-y", "-i", input_path,
                "-vf", f"drawtext=text='{watermark_text}':fontsize=24:fontcolor=white:shadowcolor=black:shadowx=2:shadowy=2:x=10:y=10,scale=iw*0.95:ih*0.95,saturation=1.1:brightness=0.02",
                "-c:a", "copy",
                "-preset", "ultrafast",
                output_path
            ]
        else:
            cmd = [
                "ffmpeg", "-y", "-i", input_path,
                "-vf", f"drawtext=text='{watermark_text}':fontsize=24:fontcolor=white:shadowcolor=black:shadowx=2:shadowy=2:x=10:y=10,scale=iw*0.98:ih*0.98",
                "-c:a", "copy",
                "-preset", "ultrafast",
                output_path
            ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            raise Exception(result.stderr)
        
        os.remove(input_path)
        
        return {
            "code": 200,
            "msg": "去重成功",
            "data": {
                "file_id": file_id,
                "intensity": intensity
            }
        }
    except subprocess.TimeoutExpired:
        os.remove(input_path)
        raise HTTPException(status_code=500, detail="处理超时")
    except Exception as e:
        if os.path.exists(input_path):
            os.remove(input_path)
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.get("/api/video/download")
async def download_video(file_id: str):
    clear_expired_files()
    for filename in os.listdir(OUTPUT_DIR):
        if filename.startswith(file_id):
            return FileResponse(
                os.path.join(OUTPUT_DIR, filename),
                filename=filename,
                media_type="video/mp4"
            )
    raise HTTPException(status_code=404, detail="文件不存在或已过期")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
