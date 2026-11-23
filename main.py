import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ==========================================
# НАСТРОЙКИ
# ==========================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Проверка, видит ли сервер токен при запуске
if TELEGRAM_TOKEN:
    print(f"DEBUG: Токен найден. Длина: {len(TELEGRAM_TOKEN)} символов.")
else:
    print("DEBUG: ТОКЕН ПУСТОЙ! Переменная TELEGRAM_TOKEN не задана на Render.")

# Адрес API Nyxgram
NYXGRAM_API_URL = f"https://nyxgram.new.tg/bot{TELEGRAM_TOKEN}"

# ==========================================
# МАРШРУТЫ FLASK
# ==========================================

@app.route("/")
def home():
    return "Bot is running!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    if not TELEGRAM_TOKEN:
        return "Token not set", 500

    update = request.get_json()
    print(f"DEBUG: Получено обновление от Nyxgram: {update}")

    if update and "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "Привет! Я бот для скачивания аудио из TikTok. Отправь мне ссылку.")

    return jsonify({"ok": True}), 200

def send_message(chat_id, text):
    url = f"{NYXGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        response = requests.post(url, json=payload)
        print(f"DEBUG: Ответ от Nyxgram при отправке сообщения: {response.text}")
    except Exception as e:
        print(f"DEBUG: Ошибка при отправке сообщения: {e}")

@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    if not TELEGRAM_TOKEN:
        return "Token not set. Проверь переменные окружения на Render!", 500
    
    # Получаем URL сервиса
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "https://tiktok-audio-bot-9.onrender.com")
    webhook_url = f"{render_url}/webhook"
    url = f"{NYXGRAM_API_URL}/setWebhook?url={webhook_url}"
    
    try:
        response = requests.get(url)
        # Возвращаем ответ на экран, чтобы было видно, что ответил Nyxgram
        return f"Запрос отправлен на: {url}<br><br>Ответ: {response.text}"
    except Exception as e:
        return f"Ошибка при запросе к Nyxgram: {str(e)}", 500

# ==========================================
# ЗАПУСК
# ==========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
