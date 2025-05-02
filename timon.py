import openai
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
import os
import asyncio

# Установите OpenAI API ключ
openai.api_key = "sk-5678ijklmnopabcd5678ijklmnopabcd5678ijkl"

# Настройка логирования
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram токен
telegram_token = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"

# Flask приложение
app = Flask(__name__)

# Функция для обработки сообщений
async def handle_message(update: Update, context):
    user_message = update.message.text
    chat_id = update.message.chat_id
    # Обработка сообщения с OpenAI
    response = openai.Completion.create(
        model="text-davinci-003",  # Используйте актуальную модель
        prompt=user_message,
        max_tokens=150
    )
    reply_text = response.choices[0].text.strip()
    # Отправка ответа
    await context.bot.send_message(chat_id=chat_id, text=reply_text)

# Функция для настройки webhook
async def set_webhook():
    application = Application.builder().token(telegram_token).build()
    webhook_url = f"https://timon-sgzp.onrender.com/webhook/{telegram_token}"
    await application.bot.set_webhook(url=webhook_url)

# Основной маршрут webhook
@app.route("/webhook/<token>", methods=["POST"])
def webhook(token):
    if token != telegram_token:
        return "Invalid token", 403
    json_str = request.get_data(as_text=True)
    update = Update.de_json(json_str, application.bot)
    application.process_update(update)
    return "OK"

# Запуск Flask сервера
if __name__ == "__main__":
    application = Application.builder().token(telegram_token).build()
    application.add_handler(MessageHandler(filters.TEXT, handle_message))  # Для обработки текстовых сообщений

    # Устанавливаем webhook
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_webhook())

    # Получаем порт из переменной окружения Render
    port = int(os.environ.get("PORT", 5000))

    # Запуск Flask приложения
    app.run(host="0.0.0.0", port=port)
