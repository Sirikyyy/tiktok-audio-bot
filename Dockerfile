FROM python:3.11-slim

# Устанавливаем FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Создаем виртуальное окружение и активируем его через PATH
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Теперь pip будет ставить пакеты в виртуальное окружение
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
