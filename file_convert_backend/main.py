import os
import shutil
import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image


# 初始化应用
app = FastAPI(title="文件转换小程序后端", version="1.0")

# 跨域配置（允许小程序、本地前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 文件夹配置
UPLOAD_DIR = "./temp_upload"
OUTPUT_DIR = "./temp_output"
# 自动创建文件夹
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 支持的图片转换格式
IMAGE_SUFFIX = ["jpg", "jpeg", "png", "webp", "gif", "bmp"]

# 定时清理过期文件（2小时自动删除临时文件）
def clear_expire_file():
    expire_time = datetime.now() - timedelta(hours=2)
    # 清理上传文件夹
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        file_create_time = datetime.fromtimestamp(os.path.getctime(file_path))
        if file_create_time < expire_time:
            os.remove(file_path)
    # 清理输出文件夹
    for filename in os.listdir(OUTPUT_DIR):
        file_path = os.path.join(OUTPUT_DIR, filename)
        file_create_time = datetime.fromtimestamp(os.path.getctime(file_path))
        if file_create_time < expire_time:
            os.remove(file_path)


# 1. 健康检测接口（小程序校验服务是否在线）
@app.get("/health")
async def health_check():
    return {"code": 200, "msg": "服务运行正常", "time": str(datetime.now())}


# 2. 文件转换核心接口（上传+转换一体）
@app.post("/api/file/convert")
async def file_convert(
        target_format: str = Query(..., description="目标格式：jpg/png/webp等"),
        file: UploadFile = File(..., description="上传原始文件")
):
    clear_expire_file()
    # 获取原始文件后缀
    original_name = file.filename
    if "." not in original_name:
        raise HTTPException(status_code=400, detail="文件缺少后缀名")
    original_suffix = original_name.split(".")[-1].lower()

    # 生成唯一文件名，防止重名覆盖
    unique_id = str(uuid.uuid4())
    upload_file_name = f"{unique_id}.{original_suffix}"
    upload_file_path = os.path.join(UPLOAD_DIR, upload_file_name)

    # 保存上传文件到临时目录
    with open(upload_file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    output_file_name = f"{unique_id}.{target_format}"
    output_file_path = os.path.join(OUTPUT_DIR, output_file_name)

    # ========== 图片格式转换逻辑 ==========
    if original_suffix in IMAGE_SUFFIX and target_format in IMAGE_SUFFIX:
        try:
            img = Image.open(upload_file_path)
            # 透明图片兼容
            if target_format == "jpg":
                img = img.convert("RGB")
            img.save(output_file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"图片转换失败: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail=f"暂不支持 {original_suffix} 转 {target_format}，仅支持图片互转")

    # 返回文件唯一ID，前端用来下载
    return {
        "code": 200,
        "msg": "转换成功",
        "data": {
            "file_id": unique_id,
            "original_name": original_name,
            "new_file_name": output_file_name,
            "target_format": target_format
        }
    }


# 3. 文件下载接口（小程序通过file_id下载转换后的文件）
@app.get("/api/file/download")
async def download_file(file_id: str = Query(..., description="转换接口返回的file_id")):
    clear_expire_file()
    # 遍历输出文件夹匹配文件ID
    for filename in os.listdir(OUTPUT_DIR):
        if filename.startswith(file_id):
            file_path = os.path.join(OUTPUT_DIR, filename)
            return FileResponse(
                path=file_path,
                filename=filename,
                media_type="application/octet-stream"
            )
    raise HTTPException(status_code=404, detail="文件不存在或已过期，请重新转换")


# 4. 获取支持的转换格式列表
@app.get("/api/file/support_format")
async def get_support_format():
    return {
        "code": 200,
        "msg": "支持的图片格式",
        "formats": IMAGE_SUFFIX
    }


if __name__ == "__main__":
    import uvicorn
    # 启动服务，0.0.0.0 允许局域网/小程序访问
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)