from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import openai
import asyncio

# --- Настройки ---
BOT_TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"https://timon-sgzp.onrender.com{WEBHOOK_PATH}"
OPENAI_API_KEY = "sk-5678ijklmnopabcd5678ijklmnopabcd5678ijkl"

openai.api_key = OPENAI_API_KEY
app = Flask(__name__)

application = Application.builder().token(BOT_TOKEN).build()
init_task = None

# Инициализация приложения один раз
@app.before_first_request
def before_first_request():
    global init_task
    loop = asyncio.get_event_loop()
    if init_task is None:
        init_task = loop.create_task(initialize_bot())

async def initialize_bot():
    await application.initialize()
    await application.bot.set_webhook(url=WEBHOOK_URL)

# Обработчик /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот с OpenAI. Напиши мне что-нибудь.")

# Обработка текста и ответ через ChatGPT
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        reply = f"Произошла ошибка при обращении к OpenAI: {e}"
    await update.message.reply_text(reply)

# Добавление хендлеров
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

# Webhook маршрут
@app.post(WEBHOOK_PATH)
async def webhook():
    data = await request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "OK"

# Проверка на главной странице
@app.get("/")
def index():
    return "Бот работает!"

# Запуск
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
