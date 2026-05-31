from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import uuid
import shutil
import subprocess
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

@app.get("/")
async def root():
    return {"code": 200, "msg": "视频去重服务运行中"}

@app.get("/health")
async def health_check():
    logger.info("健康检查")
    return {"code": 200, "msg": "服务运行正常"}

@app.get("/test")
async def test():
    logger.info("测试接口")
    return {"code": 200, "msg": "测试成功"}

@app.post("/api/video/dedup")
async def video_dedup(file: UploadFile = File(...), intensity: str = "medium"):
    logger.info(f"开始处理视频，强度: {intensity}")
    
    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}_input.mp4")
    output_path = os.path.join(OUTPUT_DIR, f"{file_id}_dedup.mp4")

    try:
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        logger.info(f"文件已保存: {input_path}")

        watermark_text = f"DEDUP_{file_id[:8]}"

        if intensity == "low":
            cmd = [
                "ffmpeg", "-y", "-i", input_path,
                "-vf", f"drawtext=text='{watermark_text}':fontsize=24:fontcolor=white:shadowcolor=black:shadowx=2:shadowy=2:x=10:y=10",
                "-c:a", "copy",
                "-preset", "ultrafast",
                "-t", "30",
                output_path
            ]
        elif intensity == "high":
            cmd = [
                "ffmpeg", "-y", "-i", input_path,
                "-vf", f"drawtext=text='{watermark_text}':fontsize=24:fontcolor=white:shadowcolor=black:shadowx=2:shadowy=2:x=10:y=10,scale=iw*0.95:ih*0.95",
                "-c:a", "copy",
                "-preset", "ultrafast",
                "-t", "30",
                output_path
            ]
        else:
            cmd = [
                "ffmpeg", "-y", "-i", input_path,
                "-vf", f"drawtext=text='{watermark_text}':fontsize=24:fontcolor=white:shadowcolor=black:shadowx=2:shadowy=2:x=10:y=10,scale=iw*0.98:ih*0.98",
                "-c:a", "copy",
                "-preset", "ultrafast",
                "-t", "30",
                output_path
            ]
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        logger.info(f"命令执行结果: returncode={result.returncode}")
        
        if result.returncode != 0:
            logger.error(f"FFmpeg 错误: {result.stderr}")
            raise Exception(f"FFmpeg 错误: {result.stderr}")
        
        os.remove(input_path)
        
        logger.info(f"处理完成，输出文件: {output_path}")
        
        return {
            "code": 200,
            "msg": "去重成功",
            "data": {
                "file_id": file_id,
                "intensity": intensity
            }
        }
    except subprocess.TimeoutExpired:
        if os.path.exists(input_path):
            os.remove(input_path)
        logger.error("处理超时")
        raise HTTPException(status_code=500, detail="处理超时")
    except Exception as e:
        if os.path.exists(input_path):
            os.remove(input_path)
        logger.error(f"处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.get("/api/video/download")
async def download_video(file_id: str):
    for filename in os.listdir(OUTPUT_DIR):
        if filename.startswith(file_id):
            return FileResponse(
                os.path.join(OUTPUT_DIR, filename),
                filename=filename,
                media_type="video/mp4"
            )
    raise HTTPException(status_code=404, detail="文件不存在或已过期")

if __name__ == "__main__":
    logger.info("启动视频去重服务...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug", timeout_keep_alive=300)
