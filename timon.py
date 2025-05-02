from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
import openai

telegram_token = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
openai.api_key = "sk-5678ijklmnopabcd5678ijklmnopabcd5678ijkl"

app = Flask(__name__)

# Создаем Telegram-приложение
application = ApplicationBuilder().token(telegram_token).build()

# Обработка команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши мне что-нибудь, и я отвечу с помощью ChatGPT.")

# Обработка обычных сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        reply = response['choices'][0]['message']['content']
    except Exception as e:
        reply = "Произошла ошибка при запросе к OpenAI."

    await update.message.reply_text(reply)

# Регистрируем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Синхронная обработка вебхуков
@app.route(f"/webhook/{telegram_token}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.process_update(update)
    return "ok"

# Простой root маршрут для проверки
@app.route("/")
def home():
    return "Бот работает!"

# Устанавливаем webhook при запуске
def set_webhook():
    webhook_url = f"https://timon-sgzp.onrender.com/webhook/{telegram_token}"
    import asyncio
    asyncio.run(application.bot.set_webhook(url=webhook_url))

if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=5000)
