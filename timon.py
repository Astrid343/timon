import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai

# Telegram & OpenAI ключи (вшиты напрямую)
TELEGRAM_TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
OPENAI_API_KEY = "sk-ijklmnopqrstuvwxijklmnopqrstuvwxijklmnop"

openai.api_key = OPENAI_API_KEY

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши что-нибудь, и я сгенерирую ответ с помощью OpenAI.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}],
        max_tokens=100
    )
    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

# Обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Вебхук Flask
@app.route(f"/webhook/{TELEGRAM_TOKEN}", methods=["POST"])
async def webhook() -> str:
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

@app.route("/")
def index():
    return "Бот работает!"

if __name__ == "__main__":
    import asyncio
    asyncio.run(application.bot.set_webhook(url=f"https://timon-sgzp.onrender.com/webhook/{TELEGRAM_TOKEN}"))
    app.run(host="0.0.0.0", port=10000)
