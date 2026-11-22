FROM python:3.11-slim

# Устанавливаем FFmpeg и корневые сертификаты (для безопасного скачивания пакетов)
RUN apt-get update && apt-get install -y ffmpeg ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Создаем виртуальное окружение
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Обновляем pip до свежей версии (часто лечит ошибки установки)
RUN pip install --upgrade pip

# Копируем и ставим зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
