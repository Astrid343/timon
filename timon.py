import openai
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters

# Токены для Telegram и OpenAI
TELEGRAM_BOT_TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
OPENAI_API_KEY = "sk-ijklmnopqrstuvwxijklmnopqrstuvwxijklmnop"
WEBHOOK_URL = "ВАШ_СЕРВЕРНЫЙ_АДРЕС"  # Например, https://yourdomain.com/webhook

# Инициализация Flask
app = Flask(name)

# Инициализация Telegram бота
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Инициализация OpenAI
openai.api_key = OPENAI_API_KEY

# Обработчик команд /start
def start(update, context):
    update.message.reply_text("Привет! Я бот с ChatGPT. Напиши мне что-нибудь.")

# Обработчик сообщений
def handle_message(update, context):
    user_message = update.message.text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты Telegram-бот с искусственным интеллектом."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        reply = f"Ошибка OpenAI: {e}"

    update.message.reply_text(reply)

# Регистрируем обработчики команд и сообщений
dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Создаём Webhook эндпоинт
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = Update.de_json(json_str, bot)
    dispatcher.process_update(update)
    return 'OK'

if __name__ == '__main__':
    # Устанавливаем Webhook для Telegram
    bot.set_webhook(WEBHOOK_URL)

    # Запуск сервера Flask
    app.run(host='0.0.0.0', port=5000)
