"""Models for converter app."""
from django.db import models


class ConversionTask(models.Model):
    """Model to track file conversion tasks."""
    TASK_TYPE_CHOICES = [
        ("image", "图片转换"),
        ("document", "文档转换"),
    ]

    file_id = models.CharField(max_length=64, unique=True, db_index=True)
    original_filename = models.CharField(max_length=255)
    original_format = models.CharField(max_length=32)
    target_format = models.CharField(max_length=32)
    task_type = models.CharField(max_length=32, choices=TASK_TYPE_CHOICES)
    output_filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    is_downloaded = models.BooleanField(default=False)

    class Meta:
        db_table = "conversion_tasks"

    def __str__(self):
        return f"{self.original_filename} -> {self.target_format}"