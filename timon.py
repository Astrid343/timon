import logging
import openai
import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters
from telegram.ext import CallbackContext

# Настроим логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализируем Flask приложение
app = Flask(__name__)

# Получаем токен Telegram бота и API ключ OpenAI
BOT_TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
OPENAI_API_KEY = "sk-ijklmnopqrstuvwxijklmnopqrstuvwxijklmnop"
WEBHOOK_URL = "https://timon-sgzp.onrender.com/webhook"

# Настроим ключ API OpenAI
openai.api_key = OPENAI_API_KEY

# Функция для обработки сообщений
async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text  # Получаем сообщение пользователя
    chat_id = update.message.chat_id
    
    try:
        # Отправляем запрос в OpenAI и получаем ответ
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=user_message,
            max_tokens=100
        )
        bot_reply = response.choices[0].text.strip()  # Извлекаем ответ
        # Отправляем ответ пользователю
        await context.bot.send_message(chat_id=chat_id, text=bot_reply)
    except Exception as e:
        logger.error(f"Ошибка в OpenAI API: {e}")
        await context.bot.send_message(chat_id=chat_id, text="Извините, я не могу обработать ваш запрос.")

# Создаем приложение Telegram
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Добавляем обработчик сообщений
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Роут для вебхука
@app.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(), telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK", 200

# Устанавливаем вебхук
async def set_webhook():
    try:
        await telegram_app.bot.set_webhook(WEBHOOK_URL)
        logger.info("Вебхук успешно установлен.")
    except Exception as e:
        logger.error(f"Ошибка при установке вебхука: {e}")

# Запускаем Flask приложение и Telegram бота
if __name__ == "__main__":
    import asyncio
    asyncio.run(set_webhook())  # Устанавливаем вебхук асинхронно
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
