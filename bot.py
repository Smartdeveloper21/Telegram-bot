import os
import subprocess
import tempfile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters, CallbackQueryHandler

BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me any YouTube link, and I'll download it for you (MP4 or MP3).")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    keyboard = [
        [
            InlineKeyboardButton("📹 MP4 Video", callback_data=f"mp4|{url}"),
            InlineKeyboardButton("🎧 MP3 Audio", callback_data=f"mp3|{url}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose format:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    format_type, url = query.data.split("|", 1)

    await query.edit_message_text(f"⬇️ Downloading {format_type.upper()}... Please wait")

    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = os.path.join(tmpdir, "output.%(ext)s")
        cmd = [
            "yt-dlp",
            url,
            "-o", out_file
        ]
        if format_type == "mp3":
            cmd += ["-x", "--audio-format", "mp3"]

        try:
            subprocess.run(cmd, check=True)
            for file in os.listdir(tmpdir):
                path = os.path.join(tmpdir, file)
                await query.message.reply_document(document=open(path, "rb"))
                return
        except Exception as e:
            await query.message.reply_text(f"❌ Error: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("🤖 Bot running...")
    app.run_polling()
