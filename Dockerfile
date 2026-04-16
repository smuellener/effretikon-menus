FROM python:3.11-slim

# System dependencies: tesseract + German language pack
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-deu \
    libglib2.0-0 \
    libgl1 \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV PORT=10000
CMD gunicorn app:app --workers 1 --timeout 120 --bind 0.0.0.0:$PORT
