
import os
import re
import asyncio
import tempfile
from pathlib import Path

import yt_dlp
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("9028130297:AAEJPnxSaOwdX1_2O6dP715BY5HDRZqRMRc")

WELCOME = """
👑 أهلاً بك في ADNAN DOWNLOAD

📥 أرسل رابط الفيديو للتحميل.

🌐 المنصات:
TikTok
Instagram
Facebook
YouTube

⚡ سريع وسهل ومتاح للجميع.
"""

def download(url, folder):
    opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": str(Path(folder) / "video.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "max_filesize": 49 * 1024 * 1024,
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    files = list(Path(folder).glob("video.*"))
    return files[0] if files else None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 طريقة الاستخدام:\nأرسل رابط فيديو عام ومسموح بتنزيله."
    )


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not re.match(r"^https?://", url):
        await update.message.reply_text("❌ أرسل رابط صحيح.")
        return

    status = await update.message.reply_text("⏳ جاري تجهيز الفيديو...")

    try:
        with tempfile.TemporaryDirectory() as folder:
            path = await asyncio.to_thread(download, url, folder)

            if not path or path.stat().st_size > 49 * 1024 * 1024:
                await status.edit_text("❌ الفيديو غير متوفر أو حجمه كبير.")
                return

            with open(path, "rb") as video:
                await update.message.reply_video(
                    video=video,
                    caption="👑 ADNAN DOWNLOAD"
                )

            await status.delete()

    except Exception:
        await status.edit_text("❌ تعذر تحميل الفيديو. حاول برابط آخر.")


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN غير مضبوط")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle)
    )

    app.run_polling()


if __name__ == "__main__":
    main()
