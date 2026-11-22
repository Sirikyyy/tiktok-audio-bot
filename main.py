import os
import logging
from flask import Flask, request, jsonify

# Настройка логирования (пригодится для отладки на Render)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ============================================================
# ЧТЕНИЕ ТОКЕНА ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ RENDER
# ============================================================
TELEGRAM_TOKEN = os.environ.get("1780244359:Qbfa1vcveyHB0QuTw1RC3lNuszdqZCsk8MO")

if not TELEGRAM_TOKEN:
    logger.warning("TELEGRAM_TOKEN не задан в переменных окружения!")
    # Не роняем приложение сразу, чтобы деплой прошел,
    # но в логах будет предупреждение.

# ============================================================
# ИНИЦИАЛИЗАЦИЯ БОТА (если используешь python-telegram-bot)
# ============================================================
# Раскомментируй, если установлен пакет python-telegram-bot
# from telegram import Bot
# bot = Bot(token=TELEGRAM_TOKEN) if TELEGRAM_TOKEN else None

# ============================================================
# МАРШРУТЫ FLASK
# ============================================================

@app.route("/")
def home():
    """Проверка, что сервис жив."""
    return "TikTok Audio Bot is running!", 200


@app.route("/health")
def health():
    """Health check для Render."""
    return jsonify({"status": "ok"}), 200


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Сюда Telegram будет присылать обновления (если настроен webhook).
    """
    if not TELEGRAM_TOKEN:
        return jsonify({"error": "TELEGRAM_TOKEN not configured"}), 500

    update = request.get_json()
    if not update:
        return jsonify({"error": "No JSON received"}), 400

    logger.info(f"Получено обновление: {update}")

    # ========================================================
    # ЗДЕСЬ ТВОЯ ЛОГИКА ОБРАБОТКИ СООБЩЕНИЙ
    # ========================================================
    # Пример: если пришло сообщение с текстом — отвечаем
    # message = update.get("message", {})
    # chat_id = message.get("chat", {}).get("id")
    # text = message.get("text", "")
    #
    # if chat_id and text:
    #     # Отправка ответа через Bot API
    #     import requests
    #     url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    #     requests.post(url, json={"chat_id": chat_id, "text": f"Ты написал: {text}"})

    return jsonify({"ok": True}), 200


@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    """
    Вспомогательный маршрут: вызывает setWebhook в Telegram.
    Открой этот URL в браузере после деплоя, чтобы привязать бота к Render.
    """
    if not TELEGRAM_TOKEN:
        return jsonify({"error": "TELEGRAM_TOKEN not configured"}), 500

    # Render дает переменную RENDER_EXTERNAL_URL с твоим доменом
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if not render_url:
        return jsonify({"error": "RENDER_EXTERNAL_URL not found"}), 500

    webhook_url = f"{render_url}/webhook"
    telegram_api = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"

    import requests
    response = requests.get(telegram_api, params={"url": webhook_url})
    return jsonify(response.json()), response.status_code


# ============================================================
# ЗАПУСК (локально; на Render используется gunicorn)
# ============================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
