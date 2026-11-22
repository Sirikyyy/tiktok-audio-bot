import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Твой токен берется из настроек Render
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

@app.route("/")
def home():
    return "Bot is running!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    if not TELEGRAM_TOKEN:
        return "Token not set", 500

    update = request.get_json()
    
    # Если пришло сообщение
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        # Если написали /start
        if text == "/start":
            send_message(chat_id, "Привет! Я бот для скачивания аудио из TikTok. Отправь мне ссылку.")

    return jsonify({"ok": True}), 200

def send_message(chat_id, text):
    """Функция для отправки сообщения в Telegram"""
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    """Привязывает Telegram к нашему серверу"""
    if not TELEGRAM_TOKEN:
        return "Token not set", 500
    
    # Получаем ссылку на наш сервис на Render
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    webhook_url = f"{render_url}/webhook"
    
    url = f"{TELEGRAM_API_URL}/setWebhook?url={webhook_url}"
    response = requests.get(url)
    return jsonify(response.json())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
