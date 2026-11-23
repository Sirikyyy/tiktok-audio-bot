import os
import requests
import yt_dlp
from flask import Flask, request, jsonify

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("1780244359:df7dCD0Qe38_xGedo9UQohwhDmMYO5-362P")
NYXGRAM_API_URL = f"https://nyxgram.new.tg/bot{TELEGRAM_TOKEN}"

@app.route("/")
def home():
    return "Bot is running!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    if not TELEGRAM_TOKEN:
        return "Token not set", 500

    update = request.get_json()
    
    if update and "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "Я бот созданный @inoagent.Могу скачать мр3 из видео тт. Скинь мне ссылку!")
        
        # Если сообщение содержит ссылку на TikTok
        elif "tiktok.com" in text:
            send_message(chat_id, "⏳ Скачиваю аудио, жди блять.")
            # Запускаем скачивание
            download_and_send_audio(chat_id, text)
            
        else:
            send_message(chat_id, "Пожалуйста, отправь ссылку на видео TikTok.")

    return jsonify({"ok": True}), 200

def send_message(chat_id, text):
    url = f"{NYXGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def download_and_send_audio(chat_id, url):
    # Настройки для скачивания только аудио в формате mp3
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'/tmp/audio_{chat_id}.%(ext)s',
        'quiet': True
    }

    try:
        # Скачиваем аудио
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        file_path = f'/tmp/audio_{chat_id}.mp3'
        
        # Отправляем файл в Nyxgram
        send_audio(chat_id, file_path)

    except Exception as e:
        print(f"Ошибка скачивания: {e}")
        send_message(chat_id, f"❌ Не удалось скачать аудио. Возможно, ссылка неверная или видео удалено.")
    finally:
        # Удаляем файл после отправки, чтобы не забивать память
        if os.path.exists(file_path):
            os.remove(file_path)

def send_audio(chat_id, file_path):
    url = f"{NYXGRAM_API_URL}/sendAudio"
    with open(file_path, 'rb') as audio:
        files = {'audio': audio}
        data = {'chat_id': chat_id}
        response = requests.post(url, data=data, files=files)
        print(f"Ответ от Nyxgram (аудио): {response.text}")

@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "https://tiktok-audio-bot-9.onrender.com")
    webhook_url = f"{render_url}/webhook"
    url = f"{NYXGRAM_API_URL}/setWebhook?url={webhook_url}"
    response = requests.get(url)
    return f"Ответ: {response.text}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
