FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY file_convert_backend/ .

RUN python manage.py migrate --run-syncdb

EXPOSE 8000

CMD ["gunicorn", "--workers", "2", "--timeout", "120", "file_convert.wsgi:application", "--bind", "0.0.0.0:8000", "--log-level", "debug"]