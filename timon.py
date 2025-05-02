from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import openai
import asyncio

# === 🔐 Твои ключи ВШИТЫ напрямую ===
TELEGRAM_TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
OPENAI_API_KEY = "sk-ijklmnopqrstuvwxijklmnopqrstuvwxijklmnop"

# Устанавливаем ключ OpenAI
openai.api_key = OPENAI_API_KEY

# === Flask-приложение ===
app = Flask(__name__)

# === Telegram Application ===
application = Application.builder().token(TELEGRAM_TOKEN).build()

# === Команда /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я GPT-бот. Напиши мне сообщение, и я отвечу 😉")

# === Обработка текстовых сообщений ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Можно заменить на "gpt-4", если есть доступ
            messages=[
                {"role": "system", "content": "Ты дружелюбный Telegram-бот на базе ChatGPT."},
                {"role": "user", "content": user_message},
            ],
        )
        reply = response['choices'][0]['message']['content']
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"Ошибка OpenAI: {e}")

# === Обработчики ===
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# === Вебхук для Telegram ===
@app.post(f"/webhook/{TELEGRAM_TOKEN}")
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "OK"

# === Главная страница для Render (200 OK) ===
@app.get("/")
def index():
    return "🤖 Timon бот запущен и ждёт сообщений!", 200

# === Установка Webhook ===
async def set_webhook():
    webhook_url = f"https://timon-sgzp.onrender.com/webhook/{TELEGRAM_TOKEN}"  # ⚠️ Заменить на свой домен Render
    await application.bot.set_webhook(webhook_url)

# === Запуск Flask + установка Webhook ===
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_webhook())
    app.run(host="0.0.0.0", port=5000)
