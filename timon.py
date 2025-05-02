from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import openai
import asyncio

# Токены
telegram_token = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
openai.api_key = "sk-5678ijklmnopabcd5678ijklmnopabcd5678ijkl"

# Инициализация Flask и Telegram Application
app = Flask(__name__)
application = Application.builder().token(telegram_token).build()

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}]
    )
    reply = response["choices"][0]["message"]["content"]
    await update.message.reply_text(reply)

# Установка вебхука
async def set_webhook():
    webhook_url = f"https://timon-sgzp.onrender.com/webhook/{telegram_token}"
    await application.bot.set_webhook(url=webhook_url)

# Маршрут для Telegram webhook
@app.route(f"/webhook/{telegram_token}", methods=["POST"])
async def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update)
        return "OK"

# Главная страница (не обязательно)
@app.route("/")
def index():
    return "Бот работает!"

# Регистрация хендлеров и запуск
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    asyncio.run(set_webhook())
    app.run(host="0.0.0.0", port=5000)
