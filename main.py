import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Токен берем из настроек Render
TELEGRAM_TOKEN = os.environ.get("1780244359:df7dCD0Qe38_xGedo9UQohwhDmMYO5-362P")

# ТВОЙ НОВЫЙ АДРЕС ДЛЯ NYXGRAM
NYXGRAM_API_URL = f"https://nyxgram.new.tg/bot{TELEGRAM_TOKEN}"

@app.route("/")
def home():
    return "Bot is running!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    if not TELEGRAM_TOKEN:
        return "Token not set", 500

    update = request.get_json()
    
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "Привет! Я бот для скачивания аудио из TikTok. Отправь мне ссылку.")

    return jsonify({"ok": True}), 200

def send_message(chat_id, text):
    url = f"{NYXGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    # Отправляем запрос в Nyxgram
    response = requests.post(url, json=payload)
    # Для отладки можно вывести ответ в логи Render
    print(f"Nyxgram response: {response.text}") 

@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    if not TELEGRAM_TOKEN:
        return "Token not set", 500
    
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    webhook_url = f"{render_url}/webhook"
    
    # Устанавливаем вебхук в Nyxgram
    url = f"{NYXGRAM_API_URL}/setWebhook?url={webhook_url}"
    response = requests.get(url)
    return jsonify(response.json())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
