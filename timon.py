import logging
import openai
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Токены
TELEGRAM_API_TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
OPENAI_API_KEY = "sk-5678ijklmnopabcd5678ijklmnopabcd5678ijkl"

# Инициализация Flask
app = Flask(__name__)

# Настройка OpenAI API
openai.api_key = OPENAI_API_KEY

# Логирование
logging.basicConfig(level=logging.INFO)

# Обработка команды /start
async def start(update: Update, context):
    await update.message.reply_text("Привет! Напиши мне сообщение, и я отвечу с помощью GPT-3.")

# Обработка входящих сообщений
async def handle_message(update: Update, context):
    user_message = update.message.text

    try:
        # Запрос к OpenAI
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=user_message,
            max_tokens=150
        )
        await update.message.reply_text(response.choices[0].text.strip())
    except Exception as e:
        await update.message.reply_text("Ошибка: Не удалось обработать запрос.")
        logging.error(f"Ошибка: {e}")

# Роут для вебхука
@app.route(f"/webhook/{TELEGRAM_API_TOKEN}", methods=["POST"])
def webhook():
    try:
        # Получаем данные от Telegram
        payload = request.get_json()
        update = Update.de_json(payload, None)

        # Создаем приложение Telegram
        application = Application.builder().token(TELEGRAM_API_TOKEN).build()

        # Обрабатываем обновление
        application.process_update(update)
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        logging.error(f"Ошибка при обработке вебхука: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Запуск Flask приложения
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=10000)
