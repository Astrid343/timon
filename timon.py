import os
import logging
import asyncio
from quart import Quart, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI

# === НАСТРОЙКИ ===
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
DEEPSEEK_API_KEY = "sk-61d183527a914cf093202e5cbf28e6bc"  # ← подставь свой ключ
WEBHOOK_URL = f"https://your-app-name.onrender.com/webhook/{BOT_TOKEN}"

# === ИНИЦИАЛИЗАЦИЯ КЛИЕНТА DeepSeek ===
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# === ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЙ ===
app = Quart(__name__)
application = Application.builder().token(BOT_TOKEN).build()
logging.basicConfig(level=logging.INFO)

# === ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ: ЭКРАНИРОВАНИЕ ДЛЯ MarkdownV2 ===
def escape_markdown(text: str) -> str:
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    for char in escape_chars:
        text = text.replace(char, f"\\{char}")
    return text

# === ВЫЗОВ DeepSeek ===
async def call_deepseek_stream(prompt: str) -> str:
    try:
        response = await asyncio.to_thread(
            lambda: client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"DeepSeek API error: {e}")
        return "❌ Не удалось получить ответ от DeepSeek."

# === ХЕНДЛЕРЫ ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "*Привет!*\n\n"
        "Я — 🤖 *AI бот на базе DeepSeek*.\n\n"
        "Мой создатель: [@your_username](https://t.me/your_username)\n\n"
        "📌 Я умею:\n"
        "• Отвечать на любые вопросы\n"
        "• Объяснять сложные темы\n"
        "• Помогать с кодом и не только\n\n"
        "_Просто напиши сообщение, и я отвечу!_ ✨"
    )
    await update.message.reply_text(welcome, parse_mode="MarkdownV2", disable_web_page_preview=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    reply_raw = await call_deepseek_stream(user_message)
    reply_safe = escape_markdown(reply_raw)
    await update.message.reply_text(reply_safe, parse_mode="MarkdownV2")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# === ВЕБХУК ===
f"/webhook/{BOT_TOKEN}"
async def webhook():
    try:
        data = await request.get_json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    except Exception as e:
        logging.error(f"Exception in webhook: {e}")
    return "", 200

# === MAIN ===
async def main():
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=WEBHOOK_URL)

    from hypercorn.asyncio import serve
    from hypercorn.config import Config
    config = Config()
    config.bind = [f"0.0.0.0:{os.environ.get('PORT', '10000')}"]
    await serve(app, config)

if __name__ == "__main__":
    asyncio.run(main())
