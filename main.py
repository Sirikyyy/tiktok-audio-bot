import os
import requests
import yt_dlp
import traceback
from flask import Flask, request, jsonify

app = Flask(__name__)

# ==========================================
# НАСТРОЙКИ
# ==========================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
NYXGRAM_API_URL = f"https://nyxgram.new.tg/bot{TELEGRAM_TOKEN}"

# ==========================================
# МАРШРУТЫ FLASK
# ==========================================

@app.route("/")
def home():
    return "Bot is running!", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        if not TELEGRAM_TOKEN:
            return "Token not set", 500

        update = request.get_json()
        
        if update and "message" in update:
            chat_id = update["message"]["chat"]["id"]
            text = update["message"].get("text", "")

            if text == "/start":
                send_message(chat_id, "Привет! Я бот для скачивания аудио из TikTok. Отправь мне ссылку.")
            
            elif "tiktok.com" in text:
                send_message(chat_id, "⏳ Скачиваю аудио, подожди немного...")
                download_and_send_audio(chat_id, text)
            
            else:
                send_message(chat_id, "Пожалуйста, отправь ссылку на видео TikTok.")

        return jsonify({"ok": True}), 200

    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА В WEBHOOK: {e}")
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)}), 200


def send_message(chat_id, text):
    url = f"{NYXGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")


def download_and_send_audio(chat_id, url):
    file_path = f"/tmp/audio_{chat_id}.mp3"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'/tmp/audio_{chat_id}.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'impersonate': 'chrome', # <-- МАСКИРОВКА ПОД БРАУЗЕР
    }

    try:
        # Скачиваем аудио
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Отправляем файл
        if os.path.exists(file_path):
            send_audio(chat_id, file_path)
        else:
            send_message(chat_id, "❌ Ошибка: файл не был создан после скачивания.")

    except Exception as e:
        print(f"Ошибка yt-dlp: {e}")
        traceback.print_exc()
        send_message(chat_id, f"❌ Не удалось скачать аудио. Ошибка: {str(e)[:100]}")

    finally:
        # Удаляем файл, чтобы не забивать диск
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Ошибка при удалении файла: {e}")


def send_audio(chat_id, file_path):
    url = f"{NYXGRAM_API_URL}/sendAudio"
    try:
        with open(file_path, 'rb') as audio:
            files = {'audio': audio}
            data = {'chat_id': chat_id}
            response = requests.post(url, data=data, files=files)
            print(f"Ответ Nyxgram на отправку аудио: {response.text}")
    except Exception as e:
        print(f"Ошибка отправки аудио: {e}")


@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "https://tiktok-audio-bot-9.onrender.com")
    webhook_url = f"{render_url}/webhook"
    url = f"{NYXGRAM_API_URL}/setWebhook?url={webhook_url}"
    
    try:
        response = requests.get(url)
        return f"Ответ: {response.text}"
    except Exception as e:
        return f"Ошибка: {e}"


# ==========================================
# ЗАПУСК
# ==========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
