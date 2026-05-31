from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uuid
from datetime import datetime, timedelta
import shutil

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

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)