"""file_convert URL Configuration"""
from django.urls import path, include
from converter import views

urlpatterns = [
    path("health/", views.health_check, name="health"),
    path("api/file/convert/", views.file_convert, name="file_convert"),
    path("api/file/download/", views.download_file, name="download_file"),
    path("api/file/support_format/", views.get_support_format, name="support_format"),
]