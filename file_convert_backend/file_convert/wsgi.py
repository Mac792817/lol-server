"""WSGI config for file_convert project."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "file_convert.settings")
application = get_wsgi_application()