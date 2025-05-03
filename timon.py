import os
import json
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
BOT_TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
DEEPSEEK_API_KEY = "sk-61d183527a914cf093202e5cbf28e6bc"
WEBHOOK_URL = f"https://your-app-name.onrender.com/webhook/{BOT_TOKEN}"

# === OpenAI SDK с DeepSeek API ===
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# === ИНИЦИАЛИЗАЦИЯ ===
app = Quart(__name__)
application = Application.builder().token(BOT_TOKEN).build()
logging.basicConfig(level=logging.INFO)

# === DeepSeek вызов ===
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
        return "Не удалось получить ответ от DeepSeek."

# === ХЕНДЛЕРЫ ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "*Привет!* 👋\n\n"
        "Я бот, использующий *DeepSeek* 🤖 для того, чтобы помогать тебе отвечать на любые вопросы. "
        "Ты можешь спросить меня что угодно, и я постараюсь ответить наилучшим образом, используя лучшие источники 🧠.\n\n"
        "_Как я могу помочь тебе сегодня?_ 🙌\n\n"
        "*Вот как ты можешь со мной взаимодействовать:* 😎\n"
        "1. Напиши мне свой вопрос, и я постараюсь дать точный и полезный ответ 💬\n"
        "2. Если хочешь узнать, что я могу делать — просто скажи /help 🚀\n\n"
        "Давай начнем! ✨"
    )
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    reply = await call_deepseek_stream(user_message)
    await update.message.reply_text(reply)

# === РЕГИСТРАЦИЯ ХЕНДЛЕРОВ ===
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# === ВЕБХУК ===
f"/webhook/{BOT_TOKEN}"
async def webhook():
    try:
        data = await request.get_json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        logging.info("✅ Webhook обработан.")
    except Exception as e:
        logging.error(f"❌ Ошибка в webhook: {e}")
    return "", 200

# === MAIN ===
async def main():
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=WEBHOOK_URL)
    logging.info(f"🚀 Webhook установлен: {WEBHOOK_URL}")

    from hypercorn.asyncio import serve
    from hypercorn.config import Config
    config = Config()
    config.bind = [f"0.0.0.0:{os.environ.get('PORT', '10000')}"]
    await serve(app, config)

if __name__ == "__main__":
    asyncio.run(main())
