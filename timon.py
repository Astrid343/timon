from flask import Flask, request
import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Flask и настройки
app = Flask(__name__)

# Токен бота Telegram
telegram_token = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"

# Токен OpenAI
openai.api_key = "sk-5678ijklmnopabcd5678ijklmnopabcd5678ijkl"

# Настройка приложения для Telegram
application = Application.builder().token(telegram_token).build()

# Функция для получения ответа от OpenAI
def get_openai_response(prompt: str) -> str:
    try:
        # Запрос к API OpenAI для получения ответа
        response = openai.Completion.create(
            model="text-davinci-003",  # Используем модель GPT-3
            prompt=prompt,
            max_tokens=150
        )
        # Извлекаем и возвращаем текст ответа
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error with OpenAI: {e}")
        return "Sorry, I couldn't get a response from OpenAI."

# Функция для обработки сообщений
async def start(update: Update, context: CallbackContext):
    # Отправляем приветственное сообщение
    await update.message.reply_text("Hello! Send me a prompt, and I'll use OpenAI to respond!")

# Функция для обработки вебхука
@app.route('/webhook/<telegram_token>', methods=['POST'])
def webhook(telegram_token):
    json_str = request.get_data().decode('UTF-8')  # Получаем данные от Telegram
    update = Update.de_json(json_str, application.bot)  # Преобразуем данные в объект Update
    application.process_update(update)  # Обрабатываем обновление
    return 'OK', 200

# Устанавливаем вебхук для Telegram
application.bot.set_webhook(url=f"https://timon-sgzp.onrender.com/webhook/{telegram_token}")

# Функция для обработки сообщений и запросов от пользователей
async def handle_message(update: Update, context: CallbackContext):
    # Получаем текст сообщения от пользователя
    user_message = update.message.text
    # Получаем ответ от OpenAI
    openai_response = get_openai_response(user_message)
    # Отправляем ответ пользователю
    await update.message.reply_text(openai_response)

# Регистрируем обработчик для сообщений
application.add_handler(CommandHandler("start", start))  # Для старта
application.add_handler(MessageHandler(filters.TEXT, handle_message))  # Для обработки текстовых сообщений

# Запуск приложения Flask
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
