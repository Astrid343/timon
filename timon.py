import logging
import openai
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Настроим базовое логирование
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Инициализация приложения telegram
TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
OPENAI_API_KEY = "sk-ijklmnopqrstuvwxijklmnopqrstuvwxijklmnop"  # Здесь указываешь свой ключ OpenAI

openai.api_key = OPENAI_API_KEY  # Устанавливаем ключ для работы с OpenAI

telegram_app = Application.builder().token(TOKEN).build()

# Логируем установку webhook
@app.before_first_request
def setup():
    app.logger.info("Устанавливаю webhook...")
    telegram_app.bot.set_webhook("https://timon-sgzp.onrender.com/webhook")
    app.logger.info("Webhook установлен.")

# Обработчик команды /start
async def start(update: Update, context):
    await update.message.reply_text("Привет! Я бот.")

# Функция для получения ответа от OpenAI
async def get_openai_response(user_message: str) -> str:
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo",  # Указываешь модель OpenAI
            prompt=user_message,
            max_tokens=100  # Можно настроить количество токенов (символов)
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Ошибка при запросе к OpenAI: {e}"

# Обработчик обычных сообщений
async def chat(update: Update, context):
    user_message = update.message.text

    # Получаем ответ от OpenAI
    response = await get_openai_response(user_message)
    
    # Отправляем ответ в Telegram
    await update.message.reply_text(response)

# Добавляем обработчики команд и сообщений
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

@app.route('/webhook', methods=["POST"])
def webhook():
    # Получаем данные из POST-запроса
    data = request.get_json(force=True)

    # Логируем входящие данные для отладки
    app.logger.info(f"Incoming webhook data: {data}")

    # Преобразуем данные в объект Update и добавляем в очередь
    update = Update.de_json(data, telegram_app.bot)
    telegram_app.update_queue.put(update)

    return "ok", 200

# Основной запуск
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
