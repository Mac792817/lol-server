FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY file_convert_backend/ .

EXPOSE 8000

CMD ["gunicorn", "file_convert.wsgi:application", "--bind", "0.0.0.0:8000"]