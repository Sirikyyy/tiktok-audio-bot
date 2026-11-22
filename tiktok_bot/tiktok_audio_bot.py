import asyncio
import os
import tempfile
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile

# ================= НАСТРОЙКИ =================
# ВСТАВЬ СЮДА СВОЙ ТОКЕН ОТ @BotFather!
BOT_TOKEN = ТВОЙ_ТОКЕН_ЗДЕСЬ
# =============================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def download_tiktok_audio(url str) - str
    output_template = os.path.join(tempfile.gettempdir(), tiktok_audio_%(id)s.%(ext)s)

    ydl_opts = {
        'format' 'bestaudiobest',
        'postprocessors' [{
            'key' 'FFmpegExtractAudio',
            'preferredcodec' 'mp3',
            'preferredquality' '192',
        }],
        'outtmpl' output_template,
        'quiet' True,
        'no_warnings' True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl
        info = ydl.extract_info(url, download=True)
        filepath = info['requested_downloads'][0]['filepath']
        return filepath

@dp.message(CommandStart())
async def start_handler(message types.Message)
    await message.answer(Привет! 🎵nКидай мне ссылку на видео из TikTok, и я вытащу из него звук.)

@dp.message()
async def link_handler(message types.Message)
    text = message.text or 
    if tiktok.com not in text and vt.tiktok not in text and vm.tiktok not in text
        await message.answer(Это не похоже на ссылку TikTok. Кидай ссылку на видео.)
        return

    status_msg = await message.answer(⏳ Качаю звук, подожди...)

    filepath = None
    try
        loop = asyncio.get_event_loop()
        filepath = await loop.run_in_executor(None, download_tiktok_audio, text)

        if not os.path.exists(filepath)
            raise FileNotFoundError(Файл не создался)

        audio_file = FSInputFile(filepath)
        await message.answer_audio(audio=audio_file, title=TikTok Audio, performer=extracted by bot)
        await status_msg.delete()

    except Exception as e
        error_text = str(e)[200]
        await status_msg.edit_text(f❌ Ошибка {error_text})

    finally
        if filepath and os.path.exists(filepath)
            try
                os.remove(filepath)
            except
                pass

async def main()
    print(Бот запущен. Жду ссылки на TikTok...)
    await dp.start_polling(bot)

if __name__ == __main__
    asyncio.run(main())