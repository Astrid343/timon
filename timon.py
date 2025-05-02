from telegram import Update
from telegram.ext import Application, CommandHandler
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Установи логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Твой OpenAI ключ и Telegram токен
openai_api_key = "sk-ijklmnopqrstuvwxijklmnopqrstuvwxijklmnop"
telegram_token = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"

# Создание экземпляра Application
application = Application.builder().token(telegram_token).build()

async def start(update: Update, context):
    await update.message.reply_text("Hello! I'm your bot.")

# Добавление обработчиков
application.add_handler(CommandHandler("start", start))

# Установка вебхука
async def set_webhook():
    await application.bot.set_webhook(url="https://timon-sgzp.onrender.com/webhook/" + telegram_token)

# Вебхук
@app.route(f'/webhook/{telegram_token}', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)  # Получаем данные как строку
    update = Update.de_json(json_str, application.bot)  # Преобразуем строку в объект Update
    application.process_update(update)
    return '', 200

# Запуск Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
