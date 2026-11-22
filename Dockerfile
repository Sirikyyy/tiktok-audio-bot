FROM python:3.11-slim

# Ставим FFmpeg для конвертации звука и ca-certificates для HTTPS
RUN apt-get update && apt-get install -y ffmpeg ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем и ставим только лёгкие зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
