from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# Настройки
TELEGRAM_TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
OPENAI_API_KEY = "sk-5678ijklmnopabcd5678ijklmnopabcd5678ijkl"
WEBHOOK_URL = "https://timon-sgzp.onrender.com"

# Flask
app = Flask(__name__)

# OpenAI клиент (новый синтаксис)
client = OpenAI(api_key=OPENAI_API_KEY)

# Telegram приложение
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Запрос к OpenAI (новый синтаксис)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты дружелюбный помощник."},
            {"role": "user", "content": text}
        ]
    )
    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

# Хендлеры
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Вебхук: Flask передаёт Telegram обновления
@app.route(f"/webhook/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK"

# Для проверки доступности
@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

# Установка вебхука при запуске
@app.before_first_request
def setup_webhook():
    application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook/{TELEGRAM_TOKEN}")

# Запуск
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
