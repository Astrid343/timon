import os
from flask import Flask, request
import logging
import json
import httpx
import openai
from telegram import Bot, Update
from telegram.ext import CommandHandler, Dispatcher, Filters, MessageHandler, Updater

# Ваши ключи
TELEGRAM_TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
OPENAI_API_KEY = "your-openai-api-key"  # Здесь добавьте ваш OpenAI API ключ
WEBHOOK_URL = "https://your-render-app-url.com/webhook"  # Укажите ваш URL на Render

# Инициализация бота и диспетчера
bot = Bot(TELEGRAM_TOKEN)
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Инициализация OpenAI API
openai.api_key = OPENAI_API_KEY

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Устанавливаем webhook
def set_webhook():
    response = httpx.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook", data={"url": WEBHOOK_URL})
    if response.status_code == 200:
        logging.info("Вебхук успешно установлен.")
    else:
        logging.error("Ошибка установки вебхука.")

# Обработчик команды /start
def start(update, context):
    update.message.reply_text("Привет! Я бот и готов помогать!")

# Функция для общения с OpenAI
def get_openai_response(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # Можно использовать "gpt-4" или другие модели
            prompt=prompt,
            max_tokens=100,
            temperature=0.7,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        logging.error(f"Ошибка при взаимодействии с OpenAI: {e}")
        return "Извините, я не смог обработать ваш запрос."

# Обработчик для получения всех сообщений
def handle_message(update, context):
    user_message = update.message.text
    logging.info(f"Получено сообщение от пользователя: {user_message}")
    
    # Получаем ответ от OpenAI
    openai_response = get_openai_response(user_message)
    
    # Отправляем ответ пользователю
    update.message.reply_text(openai_response)

# Создаем обработчики
start_handler = CommandHandler('start', start)
message_handler = MessageHandler(Filters.text & ~Filters.command, handle_message)

# Добавляем обработчики в диспетчер
dispatcher.add_handler(start_handler)
dispatcher.add_handler(message_handler)

# Обработчик для вебхука
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = Update.de_json(json.loads(json_str), bot)
    dispatcher.process_update(update)
    return '', 200

# Устанавливаем вебхук при запуске
if __name__ == "__main__":
    set_webhook()
    app.run(debug=False, host='0.0.0.0', port=10000)  # Flask запускается на всех адресах
