"""API views for file conversion."""
import os
import uuid
import shutil
from datetime import datetime

from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import ConversionTask
from .converters import (
    ImageConverter,
    DocumentConverter,
    is_image_format,
    is_document_format,
)


def clear_expire_files():
    """Clear expired files (older than 2 hours)."""
    expire_time = datetime.now().timestamp() - 7200

    for directory in [settings.UPLOAD_DIR, settings.OUTPUT_DIR]:
        if not os.path.exists(directory):
            continue
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.getctime(file_path) < expire_time:
                try:
                    os.remove(file_path)
                except OSError:
                    pass


@api_view(["GET"])
def health_check(request):
    """Health check endpoint."""
    return Response({
        "code": 200,
        "msg": "服务运行正常",
        "time": str(datetime.now())
    })


@api_view(["POST"])
def file_convert(request):
    """Core file conversion endpoint."""
    clear_expire_files()

    if "file" not in request.FILES:
        return Response({
            "code": 400,
            "msg": "请上传文件"
        }, status=status.HTTP_400_BAD_REQUEST)

    target_format = request.GET.get("target_format", "").lower().strip()
    if not target_format:
        return Response({
            "code": 400,
            "msg": "请指定目标格式"
        }, status=status.HTTP_400_BAD_REQUEST)

    uploaded_file = request.FILES["file"]
    original_name = uploaded_file.name

    if "." not in original_name:
        return Response({
            "code": 400,
            "msg": "文件缺少后缀名"
        }, status=status.HTTP_400_BAD_REQUEST)

    original_suffix = original_name.rsplit(".", 1)[-1].lower()

    if original_suffix not in ["jpg", "jpeg", "png", "webp", "gif", "bmp", "txt", "docx", "xlsx", "csv", "pptx"]:
        return Response({
            "code": 400,
            "msg": f"不支持的文件格式: {original_suffix}"
        }, status=status.HTTP_400_BAD_REQUEST)

    if target_format not in ["jpg", "jpeg", "png", "webp", "gif", "bmp", "txt", "docx", "xlsx", "csv"]:
        return Response({
            "code": 400,
            "msg": f"不支持的目标格式: {target_format}"
        }, status=status.HTTP_400_BAD_REQUEST)

    unique_id = str(uuid.uuid4())
    upload_file_name = f"{unique_id}.{original_suffix}"
    upload_file_path = os.path.join(settings.UPLOAD_DIR, upload_file_name)

    with open(upload_file_path, "wb") as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)

    output_file_name = f"{unique_id}.{target_format}"
    output_file_path = os.path.join(settings.OUTPUT_DIR, output_file_name)

    try:
        task_type = "image" if is_image_format(original_suffix) else "document"

        if is_image_format(original_suffix) and is_image_format(target_format):
            ImageConverter.convert(upload_file_path, output_file_path, target_format)
        elif original_suffix == "txt" and target_format == "docx":
            DocumentConverter.txt_to_docx(upload_file_path, output_file_path)
        elif original_suffix == "docx" and target_format == "txt":
            DocumentConverter.docx_to_txt(upload_file_path, output_file_path)
        elif original_suffix == "xlsx" and target_format == "csv":
            DocumentConverter.xlsx_to_csv(upload_file_path, output_file_path)
        elif original_suffix == "csv" and target_format == "xlsx":
            DocumentConverter.csv_to_xlsx(upload_file_path, output_file_path)
        elif original_suffix == "pptx" and target_format == "txt":
            DocumentConverter.pptx_to_txt(upload_file_path, output_file_path)
        else:
            return Response({
                "code": 400,
                "msg": f"暂不支持 {original_suffix} 转 {target_format}"
            }, status=status.HTTP_400_BAD_REQUEST)

        file_size = os.path.getsize(output_file_path)

        task = ConversionTask.objects.create(
            file_id=unique_id,
            original_filename=original_name,
            original_format=original_suffix,
            target_format=target_format,
            task_type=task_type,
            output_filename=output_file_name,
            file_size=file_size,
            is_completed=True
        )

        return Response({
            "code": 200,
            "msg": "转换成功",
            "data": {
                "file_id": unique_id,
                "original_name": original_name,
                "new_file_name": output_file_name,
                "target_format": target_format,
                "file_size": file_size
            }
        })

    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"转换失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        if os.path.exists(upload_file_path):
            try:
                os.remove(upload_file_path)
            except OSError:
                pass


@api_view(["GET"])
def download_file(request):
    """Download converted file by file_id."""
    clear_expire_files()

    file_id = request.GET.get("file_id", "").strip()
    if not file_id:
        return Response({
            "code": 400,
            "msg": "请提供file_id"
        }, status=status.HTTP_400_BAD_REQUEST)

    for filename in os.listdir(settings.OUTPUT_DIR):
        if filename.startswith(file_id):
            file_path = os.path.join(settings.OUTPUT_DIR, filename)

            ConversionTask.objects.filter(file_id=file_id).update(is_downloaded=True)

            response = FileResponse(
                open(file_path, "rb"),
                content_type="application/octet-stream"
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response

    return Response({
        "code": 404,
        "msg": "文件不存在或已过期，请重新转换"
    }, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
def get_support_format(request):
    """Get supported conversion formats."""
    return Response({
        "code": 200,
        "msg": "支持的转换格式",
        "data": {
            "image": ImageConverter.SUPPORTED_FORMATS,
            "document": {
                "doc": ["txt", "docx"],
                "sheet": ["xlsx", "csv"],
                "presentation": ["pptx"],
                "note": "目前支持: txt<->docx, xlsx<->csv, pptx->txt"
            }
        }
    })
