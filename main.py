import os
import time
import json
import requests
import tempfile
import yt_dlp
from threading import Thread

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "1780244359:Qbfa1vcveyHB0QuTw1RC3lNuszdqZCsk8MO"  # <-- ВСТАВЬ ТОКЕН
# =============================================

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_updates(offset=None):
    url = f"{API_URL}/getUpdates"
    params = {"timeout": 30, "offset": offset}
    try:
        resp = requests.get(url, params=params, timeout=40)
        return resp.json()
    except Exception as e:
        print(f"Ошибка getUpdates: {e}")
        return {"ok": False}

def send_message(chat_id, text):
    url = f"{API_URL}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def send_audio(chat_id, filepath, title="TikTok Audio"):
    url = f"{API_URL}/sendAudio"
    with open(filepath, 'rb') as f:
        files = {'audio': f}
        data = {'chat_id': chat_id, 'title': title, 'performer': 'Bot'}
        requests.post(url, files=files, data=data)

def download_tiktok_audio(url: str) -> str:
    output_template = os.path.join(tempfile.gettempdir(), "tiktok_audio_%(id)s.%(ext)s")
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return info['requested_downloads'][0]['filepath']

def handle_message(message):
    chat_id = message['chat']['id']
    text = message.get('text', '')

    if text == '/start':
        send_message(chat_id, "Привет! 🎵 Кидай ссылку на TikTok, я вытащу звук.")
        return

    if "tiktok.com" not in text and "vt.tiktok" not in text:
        send_message(chat_id, "Это не ссылка TikTok.")
        return

    send_message(chat_id, "⏳ Качаю...")
    try:
        filepath = download_tiktok_audio(text)
        if os.path.exists(filepath):
            send_audio(chat_id, filepath)
            os.remove(filepath)
        else:
            send_message(chat_id, "❌ Файл не создался.")
    except Exception as e:
        send_message(chat_id, f"❌ Ошибка: {str(e)[:200]}")

def main():
    print("Бот запущен (HTTP polling)...")
    last_update_id = None
    while True:
        updates = get_updates(offset=last_update_id)
        if updates.get("ok") and updates.get("result"):
            for update in updates["result"]:
                last_update_id = update["update_id"] + 1
                if "message" in update:
                    handle_message(update["message"])
        time.sleep(1)

if __name__ == "__main__":
    main()
