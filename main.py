import asyncio
import os
import tempfile
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# ================= НАСТРОЙКИ =================
# ВСТАВЬ СЮДА СВОЙ ТОКЕН!
BOT_TOKEN = "1780244359:Qbfa1vcveyHB0QuTw1RC3lNuszdqZCsk8MO"

# Render автоматически передаст сюда твой URL (например, https://твой-бот.onrender.com)
# Если переменной нет, используем заглушку для локального теста
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL", "https://localhost")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Порт, который дает Render (обычно 10000, но лучше брать из переменной)
PORT = int(os.getenv("PORT", 10000))
# =============================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

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
        filepath = info['requested_downloads'][0]['filepath']
        return filepath

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Привет! 🎵\nКидай мне ссылку на видео из TikTok, и я вытащу из него звук.")

@dp.message()
async def link_handler(message: types.Message):
    text = message.text or ""
    if "tiktok.com" not in text and "vt.tiktok" not in text and "vm.tiktok" not in text:
        await message.answer("Это не похоже на ссылку TikTok. Кидай ссылку на видео.")
        return

    status_msg = await message.answer("⏳ Качаю звук, подожди...")
    filepath = None
    try:
        loop = asyncio.get_event_loop()
        filepath = await loop.run_in_executor(None, download_tiktok_audio, text)
        if not os.path.exists(filepath):
            raise FileNotFoundError("Файл не создался")
        audio_file = FSInputFile(filepath)
        await message.answer_audio(audio=audio_file, title="TikTok Audio", performer="extracted by bot")
        await status_msg.delete()
    except Exception as e:
        error_text = str(e)[:200]
        await status_msg.edit_text(f"❌ Ошибка: {error_text}")
    finally:
        if filepath and os.path.exists(filepath):
            try: os.remove(filepath)
            except: pass

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
async def on_startup(bot: Bot):
    # Говорим Telegram, куда отправлять сообщения
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook установлен на: {WEBHOOK_URL}")

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()

async def healthcheck(request):
    # Этот эндпоинт нужен, чтобы Render не усыплял бота
    return web.Response(text="OK")

def main():
    app = web.Application()
    
    # Настройка вебхука
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    
    # Добавляем healthcheck
    app.router.add_get("/", healthcheck)
    
    # Хуки запуска/остановки
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    setup_application(app, dp, bot=bot)
    
    print(f"Запуск веб-сервера на порту {PORT}...")
    web.run_app(app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
